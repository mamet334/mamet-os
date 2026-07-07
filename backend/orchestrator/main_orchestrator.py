"""
MAMET OS - Main Orchestrator (KERNEL)
======================================
Jantung MAMET OS. Loop utama yang menerima input,
merencanakan, mengumpulkan bukti, memutuskan, dan merespons.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional

from .planning_engine import PlanningEngine
from .evidence_collector import EvidenceCollector
from .decision_engine import DecisionEngine

from memory.user_memory import UserMemory
from ai.provider_router import ProviderRouter


class MainOrchestrator:
    """Kernel MAMET OS."""
    
    def __init__(self):
        self.planning_engine = PlanningEngine()
        self.evidence_collector = EvidenceCollector()
        self.decision_engine = DecisionEngine()
        self.boot_time = None
        self.is_running = False
        
    async def boot(self):
        self.boot_time = datetime.now()
        self.is_running = True
        
        await self.planning_engine.initialize()
        await self.evidence_collector.initialize()
        await self.decision_engine.initialize()
        
        # Trigger Forgetting Mechanism saat boot (secara default untuk user default)
        try:
            mem = UserMemory(email="default")
            deleted = mem.cleanup_expired_facts()
            print(f"[KERNEL] Forgetting Mechanism: Dihapus {deleted} fakta kedaluwarsa.")
        except Exception as e:
            print(f"[KERNEL] Gagal menjalankan forgetting mechanism: {e}")
            
        print(f"[KERNEL] Booted at {self.boot_time}")
        print(f"[KERNEL] Planning Engine: READY")
        print(f"[KERNEL] Evidence Collector: READY")
        print(f"[KERNEL] Decision Engine: READY")
        
    async def shutdown(self):
        self.is_running = False
        print(f"[KERNEL] Shutdown. Uptime: {datetime.now() - self.boot_time}")
        
    async def process(
        self,
        user_id: str,
        column: str,
        message: str,
        api_key: Optional[str] = None,
        agent: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        if not self.is_running:
            return self._error_response("Kernel belum siap. Silakan tunggu...")
        
        print(f"\n[KERNEL] ========== NEW REQUEST ==========")
        print(f"[KERNEL] User: {user_id}")
        print(f"[KERNEL] Kolom: {column}")
        print(f"[KERNEL] Message: {message[:100]}...")
        
        plan = await self.planning_engine.create_plan(
            user_id=user_id,
            column=column,
            message=message
        )
        if agent:
            plan["sub_agent"] = agent
            if "invoke_sub_agent" not in plan["steps"]:
                plan["steps"].append("invoke_sub_agent")
        
        print(f"[KERNEL] Plan: {plan['steps']}")
        
        evidence = await self.evidence_collector.collect(
            user_id=user_id,
            column=column,
            plan=plan,
            api_key=api_key
        )
        print(f"[KERNEL] Evidence collected: {len(evidence.get('items', []))} items")
        print(f"[KERNEL] Confidence: {evidence.get('confidence', 0)}")
        
        decision = await self.decision_engine.decide(
            user_id=user_id,
            column=column,
            plan=plan,
            evidence=evidence,
            api_key=api_key
        )
        print(f"[KERNEL] Decision: {decision['action']}")
        if "rag_results" in decision:
            print(f"[KERNEL] RAG results: {len(decision['rag_results'])} items")
        if "combined_context" in decision:
            print(f"[KERNEL] Combined context: {len(decision['combined_context'])} chars")
        
        response = await self._build_response(
            plan=plan,
            decision=decision,
            evidence=evidence,
            api_key=api_key,
            user_id=user_id
        )
        print(f"[KERNEL] Response: {str(response)[:100]}...")
        
        await self._save_conversation(
            user_id=user_id,
            column=column,
            message=message,
            response=response.get("response", ""),
            api_key=api_key
        )
        
        elapsed_time = time.time() - start_time
        if "response" in response:
            response["response"] += f"\n\n⏱️ _[Waktu proses: {elapsed_time:.2f} detik]_"
        
        return response
    
    async def _save_conversation(
        self,
        user_id: str,
        column: str,
        message: str,
        response: str,
        api_key: Optional[str] = None
    ):
        try:
            memory = UserMemory(email=user_id)
            memory.save_conversation(
                column=column,
                message=message,
                response=response
            )
            print(f"[KERNEL] Percakapan tersimpan ke memori")
            
            # Ekstrak fakta jika dari Kolom 2 (Asisten Pribadi)
            if column == "kolom2" and api_key:
                asyncio.create_task(
                    self._extract_and_save_facts(user_id, message, response, api_key)
                )
                
        except Exception as e:
            print(f"[KERNEL] Gagal menyimpan percakapan: {e}")
            
    async def _extract_and_save_facts(self, user_id: str, message: str, response: str, api_key: str):
        """Mengekstrak fakta secara asinkron di latar belakang."""
        try:
            print(f"[KERNEL] Memulai ekstraksi fakta untuk user {user_id}...")
            from ai.provider_router import ProviderRouter
            from memory.fact_extractor import FactExtractor
            
            router = ProviderRouter(email=user_id)
            router.add_provider("openrouter", api_key, priority=1)
            
            extractor = FactExtractor(provider=router)
            facts = await extractor.extract_facts(message, response)
            
            if facts:
                memory = UserMemory(email=user_id)
                for f in facts:
                    fact_text = f.get("fact")
                    confidence = f.get("confidence", 0.5)
                    if fact_text:
                        memory.add_fact(fact=fact_text, source="extraction", confidence=confidence)
                        print(f"[KERNEL] Fakta baru disimpan: {fact_text} (conf: {confidence})")
            else:
                print(f"[KERNEL] Tidak ada fakta baru yang diekstrak.")
        except Exception as e:
            print(f"[KERNEL] Gagal mengekstrak fakta: {e}")
    
    async def _build_response(
        self,
        plan: Dict[str, Any],
        decision: Dict[str, Any],
        evidence: Dict[str, Any],
        api_key: Optional[str] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        try:
            action = decision.get("action", "error")
            
            if action == "direct_reply":
                rag_results = decision.get("rag_results", [])
                if rag_results:
                    lines = ["📋 **Hasil Pencarian:**\n"]
                    for i, r in enumerate(rag_results, 1):
                        lines.append(f"{i}. **{r['source']}** (relevansi: {r['similarity']})")
                        lines.append(f"   {r['text']}\n")
                    rag_response = "\n".join(lines)
                    return {
                        "response": rag_response,
                        "sources": evidence.get("sources", []),
                        "actions_taken": decision.get("actions_taken", []),
                        "requires_approval": False,
                        "approval_details": {}
                    }
                
                engineer_response = None
                for item in evidence.get("items", []):
                    if item.get("source") == "engineer":
                        engineer_response = item.get("data", {}).get("response")
                
                response_text = (
                    engineer_response or
                    decision.get("message") or
                    evidence.get("direct_answer", "Saya tidak menemukan jawaban.")
                )
                
                return {
                    "response": response_text,
                    "sources": evidence.get("sources", []),
                    "actions_taken": decision.get("actions_taken", []),
                    "requires_approval": False,
                    "approval_details": {}
                }
            
            elif action == "need_llm":
                combined_context = decision.get("combined_context", "")
                
                if api_key:
                    try:
                        router = ProviderRouter(email=user_id)
                        router.add_provider("openrouter", api_key, priority=1)
                        
                        system_prompt = "Kamu adalah MAMET OS, asisten pribadi yang personal dan hangat. Gunakan bahasa Indonesia. Jawablah dengan ramah dan singkat."
                        messages = [{"role": "system", "content": system_prompt}]
                        
                        if combined_context:
                            messages.append({"role": "system", "content": f"Konteks tambahan:\n{combined_context}"})
                        
                        user_msg = ""
                        for item in evidence.get("items", []):
                            if item.get("source") == "user_memory":
                                recent = item.get("recent_conversations", [])
                                if recent:
                                    user_msg = recent[-1].get("message", "")
                        
                        if not user_msg:
                            user_msg = evidence.get("direct_answer", "Halo")
                        
                        messages.append({"role": "user", "content": user_msg})
                        
                        llm_response = router.chat(messages)
                        
                        return {
                            "response": llm_response,
                            "sources": evidence.get("sources", []),
                            "actions_taken": decision.get("actions_taken", []),
                            "requires_approval": False,
                            "approval_details": {}
                        }
                        
                    except Exception as e:
                        print(f"[KERNEL] LLM error: {e}")
                
                if combined_context:
                    return {
                        "response": f"{combined_context}\n\n_(Menunggu koneksi AI untuk respons lebih personal)_",
                        "sources": evidence.get("sources", []),
                        "actions_taken": decision.get("actions_taken", []),
                        "requires_approval": False,
                        "approval_details": {}
                    }
                
                return {
                    "response": "[LLM] Fitur ini akan tersedia setelah integrasi OpenRouter.",
                    "sources": evidence.get("sources", []),
                    "actions_taken": decision.get("actions_taken", []),
                    "requires_approval": False,
                    "approval_details": {}
                }
            
            elif action == "need_agent":
                agent_name = decision.get("agent")
                agent_instance = None
                
                from ai.provider_router import ProviderRouter
                router = ProviderRouter(email=user_id)
                if api_key:
                    router.add_provider("openrouter", api_key, priority=1)
                
                if agent_name == "database":
                    from agents.database_explorer_agent import DatabaseExplorerAgent
                    agent_instance = DatabaseExplorerAgent(provider=router, user_id=user_id)
                elif agent_name == "file":
                    from agents.file_analysis_agent import FileAnalysisAgent
                    agent_instance = FileAnalysisAgent(provider=router, user_id=user_id)
                elif agent_name == "web":
                    from agents.web_search_agent import WebSearchAgent
                    agent_instance = WebSearchAgent(provider=router, user_id=user_id)
                elif agent_name == "research":
                    from agents.research_agent import ResearchAgent
                    agent_instance = ResearchAgent(provider=router, user_id=user_id)
                    
                if agent_instance:
                    user_msg = plan.get("original_message", "")
                    # Eksekusi agen secara nyata!
                    try:
                        agent_response = await agent_instance.process(task=user_msg, context=evidence)
                        return {
                            "response": f"[AGENT - {agent_instance.name}]\n\n{agent_response}",
                            "sources": evidence.get("sources", []),
                            "actions_taken": decision.get("actions_taken", []),
                            "requires_approval": False,
                            "approval_details": {}
                        }
                    except Exception as e:
                        return {
                            "response": f"❌ Agen '{agent_name}' gagal mengeksekusi tugas:\n{e}",
                            "sources": [],
                            "actions_taken": [],
                            "requires_approval": False,
                            "approval_details": {}
                        }
                        
                return {
                    "response": f"❌ Agen '{agent_name}' tidak ditemukan atau belum diimplementasikan.",
                    "sources": evidence.get("sources", []),
                    "actions_taken": decision.get("actions_taken", []),
                    "requires_approval": False,
                    "approval_details": {}
                }
            
            elif action == "need_approval":
                return {
                    "response": decision.get("message", "Membutuhkan persetujuan Anda."),
                    "sources": evidence.get("sources", []),
                    "actions_taken": decision.get("actions_taken", []),
                    "requires_approval": True,
                    "approval_details": decision.get("approval_details", {})
                }
            
            else:
                return self._error_response("Tindakan tidak dikenali.")
        
        except Exception as e:
            print(f"[KERNEL] ERROR building response: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._error_response(f"Gagal membangun respons: {str(e)}")
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        return {
            "response": f"❌ {message}",
            "sources": [],
            "actions_taken": [],
            "requires_approval": False,
            "approval_details": {}
        }