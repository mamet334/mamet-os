import os
import platform

class DiskDetector:
    """Modul untuk mendeteksi flashdisk / removable drive."""
    
    @staticmethod
    def get_removable_drives():
        drives = []
        system = platform.system()
        
        if system == "Windows":
            try:
                import ctypes
                bitmask = ctypes.windll.kernel32.GetLogicalDrives()
                for i in range(26):
                    if bitmask & (1 << i):
                        letter = chr(65 + i) + ":\\"
                        # 2 = DRIVE_REMOVABLE
                        if ctypes.windll.kernel32.GetDriveTypeW(letter) == 2:
                            drives.append(letter)
            except Exception as e:
                print(f"[DiskDetector] Error Windows: {e}")
                
        elif system == "Linux":
            media = "/media"
            if os.path.exists(media):
                for user in os.listdir(media):
                    path = os.path.join(media, user)
                    if os.path.isdir(path):
                        for d in os.listdir(path):
                            drives.append(os.path.join(path, d))
                            
        elif system == "Darwin":
            vol = "/Volumes"
            if os.path.exists(vol):
                for d in os.listdir(vol):
                    if d != "Macintosh HD":
                        drives.append(os.path.join(vol, d))
                        
        return drives
