import asyncio
import os
import sys

# Tambahkan backend ke path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database_detector.detector import DatabaseDetector
from database_detector.schema_mapper import SchemaMapper
from agents.database_explorer_agent import DatabaseExplorerAgent

class MockProvider:
    def chat(self, messages, model=None):
        print(f"[MOCK LLM] Menerima prompt dengan {len(messages)} pesan.")
        for msg in messages:
            if msg["role"] == "user":
                print("\n--- KONTEN PROMPT KE LLM ---")
                print(msg["content"][:500] + "\n... (dipotong)")
                print("----------------------------\n")
        return "Simulasi Analisis LLM: Struktur database CSV ini terlihat valid dan memiliki kolom yang sesuai."

async def run_simulation():
    print("==================================================")
    print("SIMULASI MENDALAM FASE 3: DATABASE DETECTOR & AGENT")
    print("==================================================")
    
    # 1. Buat file dummy
    dummy_csv = "dummy_simulasi.csv"
    with open(dummy_csv, "w", encoding="utf-8") as f:
        f.write("id,nama,umur,pekerjaan\n")
        f.write("1,Budi,30,Engineer\n")
        f.write("2,Siti,25,Designer\n")
        f.write("3,Agus,40,Manager\n")
    print(f"\n[1] File dummy '{dummy_csv}' berhasil dibuat.")
    
    try:
        # 2. Uji Database Detector
        db_type = DatabaseDetector.detect_type(dummy_csv)
        print(f"\n[2] DatabaseDetector mendeteksi tipe: {db_type.upper()}")
        
        # 3. Uji Schema Mapper
        schema = SchemaMapper.extract_schema(dummy_csv, db_type)
        print(f"\n[3] SchemaMapper mengekstrak:")
        print(f"    - Tabel: {list(schema['tables'].keys())}")
        cols = [c['name'] for c in schema['tables']['default']['columns']]
        print(f"    - Kolom: {cols}")
        print(f"    - Jumlah Sampel Data: {len(schema['tables']['default']['sample_data'])}")
        
        # 4. Uji Agent Database Explorer
        print(f"\n[4] Menjalankan DatabaseExplorerAgent...")
        agent = DatabaseExplorerAgent(provider=MockProvider(), user_id="test")
        
        # Simulasi konteks dari orchestrator (file_path disuplai via regex di collector)
        context = {"file_path": os.path.abspath(dummy_csv)}
        task = "Tolong analisis struktur data CSV ini."
        
        response = await agent.process(task=task, context=context)
        print("\n[5] Respons Akhir Agen:")
        print(response)
        
    finally:
        # Hapus dummy file
        if os.path.exists(dummy_csv):
            os.remove(dummy_csv)
            print(f"\n[6] Pembersihan file dummy selesai.")

if __name__ == "__main__":
    asyncio.run(run_simulation())
