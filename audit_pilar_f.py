import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Pastikan import berhasil
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.main import app
from backend.engineer.google_drive_sync import GoogleDriveSync

client = TestClient(app)

def test_pilar_f():
    print("=== AUDIT PILAR F: CLOUD SYNC & LEGACY WIZARD ===")
    
    user_id = "default"
    sync = GoogleDriveSync(user_id=user_id)
    
    # 1. Test F1: Status API Endpoint
    print("\n[1] Menguji Endpoint /api/legacy/status (F1)...")
    try:
        response = client.get(f"/api/legacy/status?email={user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Endpoint merespons dengan status: {data.get('status')} - {data.get('message')}")
        else:
            print(f"[ERROR] Endpoint gagal dengan status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error memanggil endpoint: {e}")

    # 2. Test F2: Google Drive Sync Instantiation & Configuration Check
    print("\n[2] Menguji Inisialisasi GoogleDriveSync (F2)...")
    try:
        if sync.token_path.exists():
            print(f"[OK] Token ditemukan di {sync.token_path}. Legacy Wizard sudah aktif.")
        else:
            print(f"[OK] Token belum ada di {sync.token_path}. Legacy Wizard belum diaktifkan (Sesuai ekspektasi awal).")
            
        cred_path = Path(os.path.join(os.getcwd(), "backend", "credentials.json"))
        if not cred_path.exists():
            cred_path = Path(os.path.join(os.getcwd(), "credentials.json"))
            
        if cred_path.exists():
            print(f"[OK] File credentials.json (OAuth) ditemukan di: {cred_path.name}")
        else:
            print(f"[WARN] File credentials.json tidak ditemukan! Legacy Wizard tidak bisa dijalankan sebelum API Key Google disediakan.")
    except Exception as e:
        print(f"[ERROR] Error pada inisialisasi GDriveSync: {e}")

    # 3. Test F1: Mekanisme Pembacaan sync.log
    print("\n[3] Menguji Pembacaan sync.log (F1)...")
    try:
        status = sync.get_sync_status()
        print(f"[OK] Fungsi internal get_sync_status() merespons: {status}")
    except Exception as e:
        print(f"[ERROR] Error membaca sync_log: {e}")
        
    print("\n=== AUDIT SELESAI ===")

if __name__ == "__main__":
    test_pilar_f()
