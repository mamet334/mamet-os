"""
MAMET OS - Embedding via OpenRouter
=====================================
Menggunakan OpenRouter API untuk embedding teks.
Setiap user memakai API key sendiri.
"""

import requests
from typing import List, Optional

# Default model embedding (murah, cepat)
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
OPENROUTER_EMBEDDING_URL = "https://openrouter.ai/api/v1/embeddings"


class EmbeddingEngine:
    """Mesin embedding via OpenRouter."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        self.api_key = api_key
        self.model = model or DEFAULT_EMBEDDING_MODEL
    
    def set_api_key(self, api_key: str):
        """Set API key user."""
        self.api_key = api_key
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed single query.
        
        Args:
            text: Teks query
            
        Returns:
            List[float]: Vector embedding
        """
        return self._call_api([text])[0]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents (batch).
        
        Args:
            texts: List teks dokumen
            
        Returns:
            List[List[float]]: List vector embedding
        """
        return self._call_api(texts)
    
    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """
        Panggil OpenRouter Embeddings API.
        
        Args:
            texts: List teks yang akan di-embed
            
        Returns:
            List[List[float]]: List vector embedding
        """
        if not self.api_key:
            print("[EMBEDDING] ⚠️ Tidak ada API key. Menggunakan embedding dummy (zeros).")
            return [[0.0] * 768 for _ in texts]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts
        }
        
        try:
            response = requests.post(
                OPENROUTER_EMBEDDING_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract embeddings dari response
            embeddings = []
            for item in data.get("data", []):
                embeddings.append(item.get("embedding", []))
            
            print(f"[EMBEDDING] ✅ {len(embeddings)} embeddings dibuat (model: {self.model})")
            return embeddings
            
        except requests.exceptions.RequestException as e:
            print(f"[EMBEDDING] ❌ Error: {str(e)}")
            # Fallback: return zeros
            return [[0.0] * 768 for _ in texts]
    
    def get_embedding_dimension(self) -> int:
        """Dapatkan dimensi embedding untuk model ini."""
        dimensions = {
            "nomic-embed-text": 768,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        return dimensions.get(self.model, 768)