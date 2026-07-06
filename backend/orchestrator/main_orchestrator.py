"""
MAMET OS - Main Orchestrator (KERNEL)
======================================
Jantung MAMET OS. Loop utama yang menerima input,
merencanakan, mengumpulkan bukti, memutuskan, dan merespons.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from .planning_engine import PlanningEngine
from .evidence_collector import EvidenceCollector
from .decision_engine import DecisionEngine


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
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
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
        
        response = await self._build_response(
            decision=decision,
            evidence=evidence,
            api_key=api_key
        )
        print(f"[KERNEL] Response: {str(response)[:100]}...")
        
        return response
    
    async def _build_response(
        self,
        decision: Dict[str, Any],
        evidence: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            action = decision.get("action", "error")
            
            if action == "direct_reply":
                # Jika ada hasil RAG, format dengan baik
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
                
                # Cek respons dari Engineer
                engineer_response = None
                for item in evidence.get("items", []):
                    if item.get("source") == "engineer":
                        engineer_response = item.get("data", {}).get("response")
                
                response_text = engineer_response or decision.get("message") or evidence.get("direct_answer", "Saya tidak menemukan jawaban.")
                
                return {
                    "response": response_text,
                    "sources": evidence.get("sources", []),
                    "actions_taken": decision.get("actions_taken", []),
                    "requires_approval": False,
                    "approval_details": {}
                }
            
            elif action == "need_llm":
                return {
                    "response": "[LLM] Fitur ini akan tersedia setelah integrasi OpenRouter.",
                    "sources": evidence.get("sources", []),
                    "actions_taken": decision.get("actions_taken", []),
                    "requires_approval": False,
                    "approval_details": {}
                }
            
            elif action == "need_agent":
                return {
                    "response": f"[AGENT] Agen '{decision.get('agent')}' akan dipanggil.",
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