"""
MAMET OS - Base Agent
=====================
Kelas dasar untuk semua sub-agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Kerangka dasar untuk semua sub-agent di MAMET OS."""
    
    def __init__(self, provider, user_id: str):
        """
        Args:
            provider: AIProvider (misal: Router) untuk memanggil LLM.
            user_id: ID pengguna yang sedang aktif (email).
        """
        self.provider = provider
        self.user_id = user_id
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Nama dari agen."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Deskripsi kemampuan agen."""
        pass
        
    @abstractmethod
    async def process(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        Menjalankan tugas spesifik agen.
        
        Args:
            task: Instruksi atau pertanyaan dari pengguna.
            context: Konteks tambahan (seperti path file, memori, dll).
            
        Returns:
            String hasil/jawaban dari agen.
        """
        pass
