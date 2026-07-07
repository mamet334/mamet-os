"""
MAMET OS - Database Explorer Agent
==================================
Agen spesialis pembaca dan penganalisis database.
"""

from typing import Dict, Any
import json
from .base_agent import BaseAgent
from database_detector import DatabaseDetector, SchemaMapper

class DatabaseExplorerAgent(BaseAgent):
    """Agen untuk mengeksplorasi dan menganalisis file database (Lego DB)."""
    
    @property
    def name(self) -> str:
        return "Database Explorer"
        
    @property
    def description(self) -> str:
        return "Menganalisis file database (SQLite, CSV, JSON) dan menjawab pertanyaan berdasarkan strukturnya."
        
    async def process(self, task: str, context: Dict[str, Any] = None) -> str:
        context = context or {}
        file_path = context.get("file_path")
        
        if not file_path:
            return "❌ Agent Database Explorer membutuhkan *path* file database untuk bekerja. Berikan path di dalam folder Anda."
            
        try:
            # 1. Deteksi Tipe Database
            db_type = DatabaseDetector.detect_type(file_path)
            if db_type == 'unknown':
                return f"❌ Tipe file `{file_path}` tidak dikenali sebagai database yang didukung (SQLite, CSV, JSON)."
                
            # 2. Ekstrak Skema dan Sampel Data
            schema = SchemaMapper.extract_schema(file_path, db_type)
            if "error" in schema:
                return f"❌ Gagal mengekstrak skema database: {schema['error']}"
                
            # 3. Merakit Prompt untuk LLM
            prompt = f"""
            Tugas dari Pengguna: {task}
            
            === INFORMASI DATABASE ===
            File: {file_path}
            Tipe Database: {db_type}
            
            Skema dan 5 Baris Sampel Data:
            {json.dumps(schema, indent=2)}
            ==========================
            
            Tolong jawab tugas/pertanyaan pengguna HANYA berdasarkan informasi skema dan sampel data di atas.
            Jika pengguna meminta query SQL, tulislah. Jika meminta analisis dari sampel, jelaskan.
            Gunakan format Markdown dan bahasa Indonesia yang rapi.
            """
            
            messages = [
                {
                    "role": "system", 
                    "content": "Kamu adalah Database Explorer Agent di MAMET OS. Kamu ahli membedah dan memahami struktur database. Berikan jawaban yang analitis dan akurat."
                }, 
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # 4. Memanggil LLM
            print(f"[AGENT: {self.name}] Memanggil LLM untuk menganalisis {file_path}...")
            response = self.provider.chat(messages)
            
            return f"🔎 **[Laporan Database Explorer]**\n\n{response}"
            
        except Exception as e:
            return f"❌ Terjadi kesalahan pada Database Explorer Agent: {str(e)}"
