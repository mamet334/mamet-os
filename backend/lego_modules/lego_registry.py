"""
MAMET OS - Lego Registry
========================
Sistem registrasi untuk memuat dan mendaftarkan semua LegoModule.
"""

from typing import Dict, Any, List
from .base_lego import LegoModule

class LegoRegistry:
    """Manajer untuk mendaftarkan dan mengeksekusi modul-modul Lego."""
    
    def __init__(self):
        self._modules: Dict[str, LegoModule] = {}
        
    def register(self, module: LegoModule) -> bool:
        """Mendaftarkan modul baru ke dalam ekosistem."""
        if not isinstance(module, LegoModule):
            print(f"[LEGO] Gagal: Modul {module} tidak mengimplementasikan LegoModule.")
            return False
            
        self._modules[module.name.lower()] = module
        print(f"[LEGO] Berhasil mendaftarkan modul: {module.name} (v{module.version})")
        return True
        
    def unregister(self, module_name: str) -> bool:
        """Melepas modul dari sistem."""
        name_key = module_name.lower()
        if name_key in self._modules:
            del self._modules[name_key]
            print(f"[LEGO] Modul {module_name} dilepas.")
            return True
        return False
        
    def get_modules(self) -> List[Dict[str, Any]]:
        """Mendapatkan daftar semua modul yang aktif."""
        return [mod.get_status() for mod in self._modules.values()]
        
    async def route_to_module(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mencari modul yang cocok dengan input, lalu memprosesnya.
        Hanya mengembalikan hasil dari modul PERTAMA yang can_handle() = True.
        """
        for name, module in self._modules.items():
            try:
                if module.can_handle(input_data):
                    print(f"[LEGO] Routing ke {module.name}...")
                    result = await module.process(input_data)
                    
                    if module.validate_output(result):
                        return {
                            "status": "success",
                            "module": module.name,
                            "result": result
                        }
                    else:
                        module.rollback()
                        return {
                            "status": "error",
                            "module": module.name,
                            "error": "Validasi output gagal, rollback dilakukan."
                        }
            except Exception as e:
                module.rollback()
                print(f"[LEGO] Kesalahan pada {name}: {e}")
                
        return {
            "status": "skipped",
            "message": "Tidak ada modul Lego yang merespons input ini."
        }
