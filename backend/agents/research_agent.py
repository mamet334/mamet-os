"""
MAMET OS - Research Agent
=========================
Agen spesialis penelitian dan sintesis informasi.
"""

from typing import Dict, Any
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """Agen untuk melakukan riset mendalam."""
    
    @property
    def name(self) -> str:
        return "Research Agent"
        
    @property
    def description(self) -> str:
        return "Melakukan riset mendalam berdasarkan topik yang diberikan."
        
    async def process(self, task: str, context: Dict[str, Any] = None) -> str:
        prompt = f"""
        Kamu ditugaskan untuk melakukan riset mendalam mengenai topik/tugas berikut:
        "{task}"
        
        Buatlah laporan riset yang terstruktur dengan format berikut:
        
        # 🔬 Laporan Riset: [Judul Topik]
        
        ## 1. Ringkasan Eksekutif
        [Ringkasan singkat 1-2 paragraf]
        
        ## 2. Analisis Utama
        [Pecah topik menjadi poin-poin krusial atau argumen utama]
        
        ## 3. Pro & Kontra / Sisi Lain
        [Berikan perspektif penyeimbang jika ada]
        
        ## 4. Kesimpulan & Rekomendasi
        [Sintesis akhir dan apa yang sebaiknya dilakukan]
        
        Pastikan gaya bahasa akademis namun tetap mudah dipahami.
        """
        
        messages = [
            {"role": "system", "content": "Kamu adalah Research Agent senior di MAMET OS. Tugasmu menyusun laporan komprehensif, obyektif, dan terstruktur."},
            {"role": "user", "content": prompt}
        ]
        
        print(f"[AGENT: {self.name}] Memulai riset mendalam...")
        response = self.provider.chat(messages)
        return response
