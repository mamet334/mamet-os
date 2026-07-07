"""
MAMET OS - Lego Module Interface
================================
Antarmuka standar untuk membuat modul custom/plugin (Fase 4).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class LegoModule(ABC):
    """
    Interface standar untuk semua modul kustom di MAMET OS.
    Engineer bisa membuat modul turunan ini untuk integrasi API eksternal,
    kontrol IoT, atau kemampuan AI tambahan.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nama unik modul."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versi modul (misal: '1.0.0')."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """Modul atau pustaka Python lain yang diperlukan."""
        return []
    
    @abstractmethod
    def can_handle(self, input_data: Dict[str, Any]) -> bool:
        """
        Menentukan apakah modul ini memiliki kapabilitas untuk menangani input tertentu.
        Contoh input_data: {"intent": "iot_control", "device": "lampu"}
        """
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proses utama modul."""
        pass
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validasi hasil output sebelum dikembalikan ke sistem."""
        return True
    
    def rollback(self) -> None:
        """Mengembalikan state sistem jika proses gagal (opsional)."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Mengembalikan status modul saat ini."""
        return {
            "name": self.name, 
            "version": self.version, 
            "active": True
        }
