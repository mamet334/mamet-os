import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_audit():
    print("=== AUDIT PILAR E: AUTH & DASHBOARD ===")
    
    import time
    test_email = f"audit_{int(time.time())}@example.com"
    test_pass = "SecurePass123!"

    print(f"\n[1] Mendaftarkan user baru: {test_email}")
    res_reg = client.post("/api/register", json={"email": test_email, "password": test_pass})
    print(f"Status Code: {res_reg.status_code}")
    if res_reg.status_code == 200:
        print("  [OK] Pendaftaran berhasil.")
    else:
        print(f"  [FAIL] Pendaftaran gagal: {res_reg.text}")

    print(f"\n[2] Login dengan kredensial yang valid")
    res_login = client.post("/api/login", json={"email": test_email, "password": test_pass})
    print(f"Status Code: {res_login.status_code}")
    if res_login.status_code == 200:
        print("  [OK] Login berhasil.")
        token = res_login.json().get("token")
        if token:
            print(f"  [OK] Token JWT diterima: {token[:20]}...")
    else:
        print(f"  [FAIL] Login gagal: {res_login.text}")

    print(f"\n[3] Login dengan kredensial yang salah (Negative Test)")
    res_bad = client.post("/api/login", json={"email": test_email, "password": "wrongpassword"})
    if res_bad.status_code == 401:
        print("  [OK] Sistem sukses memblokir login yang salah.")
    else:
        print("  [FAIL] Masalah keamanan: Login lolos dengan kredensial salah.")

    print(f"\n[4] Mengakses /api/status untuk Dashboard Awal")
    res_status = client.get(f"/api/status?email={test_email}")
    print(f"Status Code: {res_status.status_code}")
    if res_status.status_code == 200:
        data = res_status.json()
        print("  [OK] Mendapatkan metrik dashboard:")
        print(f"     - Kernel: {data.get('kernel')}")
        print(f"     - AI Provider: {data.get('ai_provider')}")
        print(f"     - RAG Docs: {data.get('rag', {}).get('docs')}")
        print(f"     - Memory Facts: {data.get('memory', {}).get('facts')}")
        print(f"     - Budget: Rp {data.get('budget', {}).get('total_cost')} / {data.get('budget', {}).get('monthly_cap')}")
    else:
        print(f"  [FAIL] Endpoint /api/status gagal: {res_status.text}")

if __name__ == "__main__":
    run_audit()
