"""
MAMET OS - Evidence Collector
===============================
Mengumpulkan bukti dari berbagai sumber berdasarkan rencana.

Filosofi:
- Modular: setiap sumber adalah Lego
- Bertingkat: cek cache dulu, baru sumber lain
- Confidence score: setiap evidence punya tingkat kepercayaan
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
            "user_memory": {"priority": 2, "enabled": False},  # Belum diimplementasi
            "rag": {"priority": 3, "enabled": False},  # Belum diimplementasi
            "web": {"priority": 4, "enabled": False},  # Belum diimplementasi
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
        """
        Kumpulkan evidence sesuai rencana.
        
        Args:
            user_id: Email user
            column: Kolom chat
            plan: Rencana dari Planning Engine
            api_key: OpenRouter API key (opsional)
            
        Returns:
            Dict berisi evidence yang dikumpulkan
        """
        evidence = {
            "items": [],
            "sources": [],
            "confidence": 0.0,
            "direct_answer": None
        }
        
        steps = plan.get("steps", [])
        
        # Eksekusi setiap langkah pengumpulan
        for step in steps:
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
        
        # Jika tidak ada evidence, beri response default
        if not evidence["items"]:
            evidence["direct_answer"] = self._get_fallback_response(column)
            evidence["confidence"] = 0.1
        
        return evidence
    
    async def _check_cache(self, user_id: str, plan: dict) -> dict:
        """Cek cache untuk respons yang sama."""
        # Placeholder - belum diimplementasi
        return None
    
    async def _check_user_memory(self, user_id: str, plan: dict) -> dict:
        """Cek User Memory."""
        # Placeholder - belum diimplementasi
        return None
    
    async def _check_rag(self, user_id: str, plan: dict, api_key: str = None) -> dict:
        """Cek RAG untuk pencarian."""
        # Placeholder - belum diimplementasi
        return None
    
    def _get_fallback_response(self, column: str) -> str:
        """Response default saat tidak ada evidence."""
        fallbacks = {
            "kolom1": "Maaf, saya belum menemukan hasil pencarian. Fitur RAG akan segera tersedia.",
            "kolom2": "Halo! Saya Asisten Pribadi MAMET OS. Fitur saya masih dalam pengembangan.",
            "kolom3": "Engineer MAMET OS siap membantu. Silakan beri tahu apa yang ingin Anda bangun atau perbaiki."
        }
        return fallbacks.get(column, "Maaf, saya belum mengerti.")