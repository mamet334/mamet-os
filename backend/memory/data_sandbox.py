import os
import shutil
from datetime import datetime
from typing import Optional

class DataSandbox:
    """
    Sandbox khusus untuk Kolom 2.
    Melindungi database dan file pengguna saat Agent mencoba memodifikasi.
    """
    
    def __init__(self, email: str = "default"):
        self.base_dir = os.path.join(os.path.expanduser("~"), ".mamet", email)
        self.sandbox_dir = os.path.join(self.base_dir, ".data_sandbox")
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
    def backup_data(self, file_path: str) -> Optional[str]:
        """Backup sebuah file database/data sebelum agen memodifikasinya."""
        if not os.path.exists(file_path):
            return None
            
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filename}_{timestamp}.bak"
        backup_path = os.path.join(self.sandbox_dir, backup_name)
        
        shutil.copy2(file_path, backup_path)
        print(f"[DATA SANDBOX] Backup dibuat: {backup_path}")
        return backup_path
        
    def restore_data(self, original_path: str, backup_path: str) -> bool:
        """Kembalikan data dari backup jika terjadi kesalahan modifikasi agen."""
        if not os.path.exists(backup_path):
            return False
            
        shutil.copy2(backup_path, original_path)
        print(f"[DATA SANDBOX] Data direstorasi ke {original_path}")
        return True
