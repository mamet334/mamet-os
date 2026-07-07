"""
MAMET OS - File Analysis Agent
==============================
Agen spesialis membaca dan menganalisis teks panjang atau dokumen (PDF, Word, Excel).
"""

import os
from typing import Dict, Any
from .base_agent import BaseAgent

class FileAnalysisAgent(BaseAgent):
    """Agen untuk menganalisis dokumen teks, PDF, Word, dan Excel."""
    
    @property
    def name(self) -> str:
        return "File Analysis Agent"
        
    @property
    def description(self) -> str:
        return "Membaca dan menganalisis isi dokumen (.txt, .md, .pdf, .docx, .xlsx)."

    def _read_pdf(self, file_path: str) -> str:
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text
        except ImportError:
            return "ERROR: Library PyPDF2 tidak ditemukan. Silakan jalankan `pip install PyPDF2` di terminal."

    def _read_docx(self, file_path: str) -> str:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            return "ERROR: Library python-docx tidak ditemukan. Silakan jalankan `pip install python-docx` di terminal."

    def _read_excel(self, file_path: str) -> str:
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_string()
        except ImportError:
            return "ERROR: Library pandas atau openpyxl tidak ditemukan. Silakan jalankan `pip install pandas openpyxl`."

    async def process(self, task: str, context: Dict[str, Any] = None) -> str:
        context = context or {}
        file_path = context.get("file_path")
        
        if not file_path or not os.path.exists(file_path):
            return "❌ Agent File Analysis membutuhkan path file yang valid. Coba sertakan nama file di pesan Anda."
            
        ext = file_path.lower().split('.')[-1]
        print(f"[AGENT: {self.name}] Membaca file {file_path} (Tipe: {ext})...")
        
        try:
            # 1. Ekstraksi Konten Berdasarkan Ekstensi
            if ext == 'pdf':
                content = self._read_pdf(file_path)
            elif ext in ['docx', 'doc']:
                content = self._read_docx(file_path)
            elif ext in ['xlsx', 'xls']:
                content = self._read_excel(file_path)
            elif ext == 'csv':
                try:
                    import pandas as pd
                    content = pd.read_csv(file_path).to_string()
                except ImportError:
                    return "ERROR: Library pandas tidak ditemukan. Silakan jalankan `pip install pandas`."
            else:
                # Fallback untuk file teks (.txt, .md, .py, .json, dll)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
            if content.startswith("ERROR:"):
                return f"❌ {content}"
                
            # Solusi Dilema Token:
            # Kita TIDAK MEMOTONG KONTEN. LLM modern (Gemini 1.5, Claude 3, GPT-4o) 
            # memiliki context window yang sangat besar (128k - 2juta token).
            # Kita biarkan Provider Router yang menangani jika token benar-benar over-limit.
            # Namun, kita berikan instruksi khusus agar LLM membaca secara komprehensif.
            
            prompt = f"""
            Tugas Analisis dari Pengguna: {task}
            
            === ISI FILE ({os.path.basename(file_path)}) ===
            {content}
            ================================================
            
            Tolong lakukan analisis SANGAT komprehensif berdasarkan seluruh isi dokumen di atas.
            Gali informasi penting secara detail, jangan ada fakta krusial yang terlewat.
            Jawab menggunakan bahasa Indonesia yang rapi, profesional, dan gunakan markdown.
            """
            
            messages = [
                {
                    "role": "system", 
                    "content": "Kamu adalah File Analysis Agent senior. Tugasmu mengekstraksi wawasan, meringkas detail-detail penting, dan mencari anomali di dalam dokumen teks/data yang besar. Jangan pernah meringkas terlalu pendek jika pengguna meminta detail."
                },
                {"role": "user", "content": prompt}
            ]
            
            response = self.provider.chat(messages)
            return f"📄 **[Laporan Analisis File: {os.path.basename(file_path)}]**\n\n{response}"
            
        except Exception as e:
            return f"❌ Terjadi kesalahan saat menganalisis file: {str(e)}"
