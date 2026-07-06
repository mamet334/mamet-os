"""
MAMET OS - Evidence Collector
===============================
Mengumpulkan bukti dari berbagai sumber berdasarkan rencana.
"""

class EvidenceCollector:
    """Pengumpul bukti dari berbagai sumber."""
    
    def __init__(self):
        self.sources = {}
        self._register_default_sources()
    
    def _register_default_sources(self):
        """Daftarkan sumber evidence default."""
        self.sources = {
            "cache": {"priority": 1, "enabled": True},
            "user_memory": {"priority": 2, "enabled": False},
            "rag": {"priority": 3, "enabled": False},
            "web": {"priority": 4, "enabled": False},
            "engineer": {"priority": 3, "enabled": True}
        }
    
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
        return None
    
    async def _check_user_memory(self, user_id: str, plan: dict) -> dict:
        return None
    
    async def _check_rag(self, user_id: str, plan: dict, api_key: str = None) -> dict:
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
        fallbacks = {
            "kolom1": "Maaf, saya belum menemukan hasil pencarian. Fitur RAG akan segera tersedia.",
            "kolom2": "Halo! Saya Asisten Pribadi MAMET OS. Fitur saya masih dalam pengembangan.",
            "kolom3": "Engineer MAMET OS siap membantu. Silakan beri tahu apa yang ingin Anda bangun atau perbaiki."
        }
        return fallbacks.get(column, "Maaf, saya belum mengerti.")