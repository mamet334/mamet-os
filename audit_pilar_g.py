import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Pastikan import berhasil
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.main import app
from backend.engineer.disk_detector import DiskDetector
from backend.memory.user_memory import UserMemory
from backend.engineer.sandbox import EngineerSandbox

client = TestClient(app)

def test_pilar_g():
    print("=== AUDIT PILAR G: HEALTH MONITORING & RECOVERY ===")
    
    # 1. Test G1: Disk Detector
    print("\n[1] Menguji DiskDetector (G1)...")
    try:
        drives = DiskDetector.get_removable_drives()
        print(f"[OK] DiskDetector berhasil berjalan. Terdeteksi {len(drives)} drive: {drives}")
    except Exception as e:
        print(f"[ERROR] Error pada DiskDetector: {e}")
        
    # 2. Test G2: Integrity Check
    print("\n[2] Menguji Integrity Check SQLite (G2)...")
    try:
        memory = UserMemory(email="default")
        is_healthy = memory.check_integrity()
        if is_healthy:
            print("[OK] Database sehat (PRAGMA integrity_check == ok).")
        else:
            print("[WARN] Database dilaporkan rusak.")
    except Exception as e:
        print(f"[ERROR] Error pada Integrity Check: {e}")
        
    # 3. Test G3: Status API Endpoint
    print("\n[3] Menguji Endpoint /api/status...")
    try:
        response = client.get("/api/status")
        if response.status_code == 200:
            data = response.json()
            db_status = data.get("memory", {}).get("database")
            if db_status:
                print(f"[OK] Endpoint merespons dengan status database: {db_status}")
            else:
                print(f"[ERROR] Endpoint tidak mengandung status database. Data: {data.get('memory')}")
        else:
            print(f"[ERROR] Endpoint gagal dengan status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error memanggil endpoint: {e}")
        
    # 4. Test G1: Flashdisk API
    print("\n[4] Menguji Endpoint /api/flashdisk/status (G1)...")
    try:
        response = client.get("/api/flashdisk/status")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Endpoint berhasil merespons drives: {data.get('drives')}")
        else:
            print(f"[ERROR] Endpoint gagal dengan status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error memanggil endpoint: {e}")
        
    # 5. Test G3/G4: Sandbox Auto Backup Logic
    print("\n[5] Menguji Logika Sandbox Auto Backup (G3 & G4)...")
    try:
        sandbox = EngineerSandbox()
        # Test pemanggilan awal auto_backup (harus sukses/membuat zip)
        # Tapi hati-hati, kita mungkin tidak mau sungguhan zip jika besar, tapi ini local test.
        # Jika berhasil jalan tanpa error, sudah cukup baik.
        sandbox.daily_auto_backup("default")
        
        # Cek apakah ada file auto_backup_... di dalam sandbox.rollback_dir
        auto_backups = list(sandbox.rollback_dir.glob("auto_backup_*.zip"))
        if auto_backups:
            print(f"[OK] Auto-Backup harian berhasil dibuat: {auto_backups[0].name}")
        else:
            print("[WARN] Auto-Backup harian dibatalkan (Mungkin karena belum 24 jam sejak backup terakhir).")
            
    except Exception as e:
        print(f"[ERROR] Error pada auto backup sandbox: {e}")
        
    print("\n=== AUDIT SELESAI ===")

if __name__ == "__main__":
    test_pilar_g()
