"""
MAMET OS - Fact Extractor
===========================
Mengekstrak fakta tentang user dari percakapan menggunakan LLM.
"""

from typing import List, Dict, Optional
import json


class FactExtractor:
    """Ekstrak fakta dari percakapan menggunakan LLM provider."""
    
    def __init__(self, provider=None):
        """
        Args:
            provider: AIProvider instance (akan diintegrasikan nanti)
        """
        self.provider = provider
    
    async def extract_facts(
        self,
        user_message: str,
        assistant_response: str,
        provider=None
    ) -> List[Dict]:
        """
        Ekstrak fakta baru dari satu interaksi.
        
        Args:
            user_message: Pesan user
            assistant_response: Respons asisten
            provider: AIProvider (jika tidak di-set di __init__)
            
        Returns:
            List fakta dengan confidence
        """
        llm = provider or self.provider
        
        if llm is None:
            print("[FACT_EXTRACTOR] ⚠️ Tidak ada LLM provider. Melewati ekstraksi.")
            return []
        
        prompt = f"""
        Berdasarkan percakapan berikut, ekstrak fakta baru tentang user.
        Hanya ekstrak fakta yang eksplisit disebutkan, jangan mengarang.
        Berikan confidence score 0.0 - 1.0.
        
        User: {user_message}
        Asisten: {assistant_response}
        
        Format JSON:
        [
          {{"fact": "fakta tentang user", "confidence": 0.8}},
          {{"fact": "fakta lain", "confidence": 0.5}}
        ]
        
        Jika tidak ada fakta baru, return [].
        """
        
        try:
            response = llm.chat(
                messages=[{"role": "user", "content": prompt}],
                model=None  # Gunakan default provider
            )
            
            # Parse JSON dari response
            # Cari JSON array di dalam response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                facts = json.loads(json_match.group())
                return facts
            else:
                return []
                
        except Exception as e:
            print(f"[FACT_EXTRACTOR] ❌ Gagal ekstraksi: {str(e)}")
            return []