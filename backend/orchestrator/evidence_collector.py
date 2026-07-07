"""
MAMET OS - Evidence Collector
===============================
Mengumpulkan bukti dari berbagai sumber berdasarkan rencana.
"""

import os
from rag.rag_engine import RAGEngine
from memory.user_memory import UserMemory
from engineer.engineer_main import Engineer

class EvidenceCollector:
    """Pengumpul bukti dari berbagai sumber."""
    
    def __init__(self):
        self.sources = {}
        self._register_default_sources()
        self._rag_engine = None
        
        # Tambahkan Lego Registry
        from lego_modules.lego_registry import LegoRegistry
        self.lego_registry = LegoRegistry()
    
    def _register_default_sources(self):
        """Daftarkan sumber evidence default."""
        self.sources = {
            "cache": {"priority": 1, "enabled": True},
            "user_memory": {"priority": 2, "enabled": True},
            "rag": {"priority": 3, "enabled": True},
            "web": {"priority": 4, "enabled": False},
            "engineer": {"priority": 3, "enabled": True}
        }
    
    def _get_rag_engine(self, api_key=None):
        """Dapatkan instance RAG Engine (singleton)."""
        if self._rag_engine is None:
            try:
                persist_dir = os.path.join(os.getcwd(), "chroma_db")
                self._rag_engine = RAGEngine(persist_dir=persist_dir, api_key=api_key)
            except Exception as e:
                print(f"[COLLECTOR] Gagal inisialisasi RAG: {e}")
        return self._rag_engine
    
    async def initialize(self):
        """Inisialisasi evidence collector."""
        enabled = [name for name, cfg in self.sources.items() if cfg["enabled"]]
        print(f"  [COLLECTOR] {len(enabled)} sumber aktif: {', '.join(enabled)}")
    
    async def collect(
        self,
        user_id: str,
        column: str,
        plan: dict,
        api_key: str = None
    ) -> dict:
        """
        Kumpulkan evidence sesuai rencana.
        """
        evidence = {
            "items": [],
            "sources": [],
            "confidence": 0.0,
            "direct_answer": None
        }
        
        steps = plan.get("steps", [])
        print(f"  [COLLECTOR] Steps: {steps}")
        
        for step in steps:
            print(f"  [COLLECTOR] Executing step: {step}")
            
            if step == "check_cache":
                result = await self._check_cache(user_id, plan)
                if result:
                    evidence["items"].append(result)
                    evidence["sources"].append("cache")
                    evidence["confidence"] = max(evidence["confidence"], 0.9)
            
            elif step == "check_user_memory":
                result = await self._check_user_memory(user_id, plan)
                if result:
                    evidence["items"].append(result)
                    evidence["sources"].append("user_memory")
                    evidence["confidence"] = max(evidence["confidence"], 0.7)
            
            elif step == "check_rag":
                result = await self._check_rag(user_id, plan, api_key)
                if result:
                    evidence["items"].append(result)
                    evidence["sources"].append("rag")
                    evidence["confidence"] = max(evidence["confidence"], 0.8)
                    
            elif step == "check_lego_modules":
                input_data = {
                    "intent": plan.get("intent"),
                    "message": plan.get("original_message"),
                    "user_id": user_id
                }
                lego_result = await self.lego_registry.route_to_module(input_data)
                if lego_result.get("status") == "success":
                    evidence["items"].append({
                        "source": "lego_module",
                        "module": lego_result["module"],
                        "data": lego_result["result"]
                    })
                    evidence["confidence"] = 1.0
            
            elif step == "check_rag_knowledge":
                print("  [COLLECTOR] Memanggil Engineer...")
                result = await self._check_engineer(user_id, plan, api_key)
                print(f"  [COLLECTOR] Engineer result: {result}")
                if result:
                    evidence["items"].append(result)
                    evidence["sources"].append("engineer")
                    evidence["confidence"] = max(evidence["confidence"], result.get("confidence", 0.8))
                    
            elif step == "invoke_sub_agent":
                result = await self._invoke_sub_agent(user_id, plan, api_key)
                if result:
                    evidence["items"].append(result)
                    evidence["sources"].append("sub_agent")
                    evidence["confidence"] = 0.95
        
        # Fallback untuk kolom3: panggil Engineer langsung jika tidak ada evidence
        if column == "kolom3" and not evidence["items"]:
            print("  [COLLECTOR] Fallback: memanggil Engineer langsung untuk kolom3")
            result = await self._check_engineer(user_id, plan, api_key)
            print(f"  [COLLECTOR] Fallback Engineer result: {result}")
            if result:
                evidence["items"].append(result)
                evidence["sources"].append("engineer")
                evidence["confidence"] = result.get("confidence", 0.8)
        
        if not evidence["items"]:
            evidence["direct_answer"] = self._get_fallback_response(column)
            evidence["confidence"] = 0.1
        
        return evidence
    
    async def _check_cache(self, user_id: str, plan: dict) -> dict:
        """Cek cache untuk respons yang sama."""
        return None
    
    async def _check_user_memory(self, user_id: str, plan: dict) -> dict:
        """Cek User Memory untuk fakta tentang user."""
        try:
            memory = UserMemory(email=user_id)
            
            # Ambil fakta sebagai konteks
            facts_context = memory.get_facts_context()
            
            # Ambil percakapan terbaru
            recent = memory.get_recent_conversations(limit=5)
            
            if facts_context or recent:
                return {
                    "source": "user_memory",
                    "facts_context": facts_context,
                    "recent_conversations": [
                        {"message": c["message"], "response": c["response"]}
                        for c in recent
                    ],
                    "total_facts": memory.get_stats()["active_facts"]
                }
        except Exception as e:
            print(f"[COLLECTOR] Error akses User Memory: {e}")
        
        return None
    
    async def _check_rag(self, user_id: str, plan: dict, api_key: str = None) -> dict:
        """Cari di RAG berdasarkan query user."""
        query = plan.get("original_message", "")
        if not query:
            return None
        
        rag = self._get_rag_engine(api_key)
        if rag is None:
            return None
        
        try:
            results = rag.search(query)
            if results:
                # Format hasil untuk respons
                formatted = []
                for r in results[:10]:  # Batasi 10 hasil teratas
                    formatted.append({
                        "text": r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"],
                        "source": r["source"],
                        "similarity": r["similarity"]
                    })
                return {
                    "source": "rag",
                    "results": formatted,
                    "total": len(results)
                }
        except Exception as e:
            print(f"[COLLECTOR] Error pencarian RAG: {e}")
        return None
    
    async def _check_engineer(self, user_id: str, plan: dict, api_key: str = None) -> dict:
        """Cek Engineer untuk analisis dan tindakan."""
        print("  [ENGINEER] Mulai memproses...")
        try:
            engineer = Engineer()
            result = await engineer.process(
                message=plan.get("original_message", ""),
                user_id=user_id
            )
            print(f"  [ENGINEER] Sukses: {result}")
            return {
                "source": "engineer",
                "data": result,
                "confidence": 0.9
            }
        except Exception as e:
            print(f"  [ENGINEER] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "source": "engineer",
                "data": {"error": str(e)},
                "confidence": 0.1
            }
            
    async def _invoke_sub_agent(self, user_id: str, plan: dict, api_key: str = None) -> dict:
        """Cek dan panggil sub-agent spesifik."""
        agent_name = plan.get("sub_agent")
        if not agent_name:
            return None
            
        print(f"  [COLLECTOR] Memanggil Sub-Agent: {agent_name}")
        try:
            from ai.provider_router import ProviderRouter
            router = ProviderRouter(email=user_id)
            if api_key:
                router.add_provider("openrouter", api_key, priority=1)
                
            agent = None
            context = {}
            if agent_name == "database":
                from agents.database_explorer_agent import DatabaseExplorerAgent
                agent = DatabaseExplorerAgent(provider=router, user_id=user_id)
                import re
                import os
                message = plan.get("original_message", "")
                file_match = re.search(r'([^\s"\']+\.(?:db|sqlite|csv|json|sqlite3))', message, re.IGNORECASE)
                if file_match:
                    context["file_path"] = os.path.join(os.getcwd(), file_match.group(1))
            elif agent_name == "research":
                from agents.research_agent import ResearchAgent
                agent = ResearchAgent(provider=router, user_id=user_id)
            elif agent_name == "web":
                from agents.web_search_agent import WebSearchAgent
                agent = WebSearchAgent(provider=router, user_id=user_id)
            elif agent_name == "file":
                from agents.file_analysis_agent import FileAnalysisAgent
                agent = FileAnalysisAgent(provider=router, user_id=user_id)
                import re
                import os
                message = plan.get("original_message", "")
                file_match = re.search(r'([^\s"\']+\.[a-zA-Z0-9]+)', message, re.IGNORECASE)
                if file_match:
                    context["file_path"] = os.path.join(os.getcwd(), file_match.group(1))
                
            if agent:
                response = await agent.process(task=plan.get("original_message", ""), context=context)
                return {
                    "source": "sub_agent",
                    "agent_name": agent_name,
                    "response": response,
                    "confidence": 0.95
                }
        except Exception as e:
            print(f"[COLLECTOR] Error pada Sub-Agent {agent_name}: {e}")
            
        return None
    
    def _get_fallback_response(self, column: str) -> str:
        """Response default saat tidak ada evidence."""
        fallbacks = {
            "kolom1": "📭 Tidak ditemukan hasil untuk pencarian ini. Coba kata kunci lain atau unggah dokumen baru.",
            "kolom2": "Halo! Saya Asisten Pribadi MAMET OS. Fitur saya masih dalam pengembangan.",
            "kolom3": "Engineer MAMET OS siap membantu. Silakan beri tahu apa yang ingin Anda bangun atau perbaiki."
        }
        return fallbacks.get(column, "Maaf, saya belum mengerti.")