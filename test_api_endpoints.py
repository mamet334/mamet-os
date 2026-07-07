import sys
import os
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient
sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "backend"))

# Disable chroma db persistent errors by mocking it if necessary
try:
    from main import app
except Exception as e:
    print(f"Gagal mengimpor aplikasi FastAPI: {e}")
    sys.exit(1)

def run_simulation():
    print("="*60)
    print("🚀 SIMULASI KONEKSI API FRONTEND-BACKEND 🚀")
    print("="*60)
    
    with TestClient(app) as client:
        # 1. Test Endpoint Upload File (/api/upload)
        print("\n[1] MENGUJI KABEL UPLOAD (RAG Kolom 1)...")
        dummy_text = "MAMET OS adalah sistem warisan digital yang sangat hebat buatan Slamet."
        file_content = dummy_text.encode('utf-8')
    
        try:
            response = client.post(
                "/api/upload",
                files={"file": ("dokumen_penting.txt", file_content, "text/plain")}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    print(f"  ✅ [BERHASIL] File terkirim ke backend.")
                    print(f"  ✅ [RESPONSE] {data['chunks']} chunk diproses, {data['char_count']} karakter tersimpan.")
                else:
                    print(f"  ❌ [GAGAL] Endpoint upload mengembalikan error: {data}")
            else:
                print(f"  ❌ [GAGAL] HTTP Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ❌ [CRASH] Terjadi kesalahan: {e}")

        # 2. Test Endpoint Chat (/api/process)
        print("\n[2] MENGUJI KABEL CHAT (Kolom 1 Pencarian)...")
        payload = {
            "user_id": "test_user",
            "column": "kolom1",
            "message": "Apa itu MAMET OS?",
            "api_key": ""
        }
        try:
            response = client.post("/api/process", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    print(f"  ✅ [BERHASIL] Chat masuk ke backend dan dibalas.")
                    print(f"  ✅ [RESPONSE] {data['response'][:100]}...")
                else:
                    print(f"  ❌ [GAGAL] Format respons salah: {data}")
            else:
                print(f"  ❌ [GAGAL] HTTP Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"  ❌ [CRASH] Terjadi kesalahan: {e}")

    print("\n" + "="*60)
    print("🎉 SIMULASI SELESAI 🎉")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
