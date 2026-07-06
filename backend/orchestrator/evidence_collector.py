"""
MAMET OS - Evidence Collector
===============================
Mengumpulkan bukti dari berbagai sumber berdasarkan rencana.
"""

import os

class EvidenceCollector:
    """Pengumpul bukti dari berbagai sumber."""
    
    def __init__(self):
        self.sources = {}
        self._register_default_sources()
        self._rag_engine = None
    
    def _register_default_sources(self):
        """Daftarkan sumber evidence default."""
        self.sources = {
            "cache": {"priority": 1, "enabled": True},
            "user_memory": {"priority": 2, "enabled": False},
            "rag": {"priority": 3, "enabled": True},
            "web": {"priority": 4, "enabled": False},
            "engineer": {"priority": 3, "enabled": True}
        }
    
    def _get_rag_engine(self, api_key=None):
        """Dapatkan instance RAG Engine (singleton)."""
        if self._rag_engine is None:
            try:
                from rag.rag_engine import RAGEngine
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
            
            elif step == "check_rag_knowledge":
                print("  [COLLECTOR] Memanggil Engineer...")
                result = await self._check_engineer(user_id, plan, api_key)
                print(f"  [COLLECTOR] Engineer result: {result}")
                if result:
                    evidence["items"].append(result)
                    evidence["sources"].append("engineer")
                    evidence["confidence"] = max(evidence["confidence"], result.get("confidence", 0.8))
        
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
        """Cek User Memory."""
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
            from engineer.engineer_main import Engineer
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
    
    def _get_fallback_response(self, column: str) -> str:
        """Response default saat tidak ada evidence."""
        fallbacks = {
            "kolom1": "Maaf, saya belum menemukan hasil pencarian. Fitur RAG akan segera tersedia.",
            "kolom2": "Halo! Saya Asisten Pribadi MAMET OS. Fitur saya masih dalam pengembangan.",
            "kolom3": "Engineer MAMET OS siap membantu. Silakan beri tahu apa yang ingin Anda bangun atau perbaiki."
        }
        return fallbacks.get(column, "Maaf, saya belum mengerti.")