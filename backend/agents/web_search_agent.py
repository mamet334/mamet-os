"""
MAMET OS - Web Search Agent
===========================
Agen spesialis pencarian informasi dari internet (menggunakan API Wikipedia publik).
"""

import urllib.request
import urllib.parse
import json
from typing import Dict, Any
from .base_agent import BaseAgent

class WebSearchAgent(BaseAgent):
    """Agen untuk mencari data di web."""
    
    @property
    def name(self) -> str:
        return "Web Search Agent"
        
    @property
    def description(self) -> str:
        return "Mencari informasi real-time dari internet (wikipedia)."
        
    async def process(self, task: str, context: Dict[str, Any] = None) -> str:
        print(f"[AGENT: {self.name}] Ekstraksi kata kunci...")
        
        # 1. Ekstrak keyword pencarian
        kw_messages = [
            {"role": "system", "content": "Kamu adalah pengekstrak kata kunci. Berikan HANYA 1-3 kata kunci pencarian Wikipedia dari tugas pengguna. Jangan beri penjelasan apapun."},
            {"role": "user", "content": task}
        ]
        keyword = self.provider.chat(kw_messages).strip().strip('"').strip("'")
        
        search_results = ""
        print(f"[AGENT: {self.name}] Mencari Wikipedia untuk: '{keyword}'")
        
        # 2. Panggil API Wikipedia
        try:
            url = f"https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(keyword)}&utf8=&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'MametOS/2.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            snippets = []
            for item in data.get("query", {}).get("search", [])[:3]:
                # Bersihkan tag HTML <span> dll dari snippet
                import re
                clean_snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
                snippets.append(f"- {item.get('title')}: {clean_snippet}")
                
            if snippets:
                search_results = "\n".join(snippets)
            else:
                search_results = "Tidak ditemukan hasil di Wikipedia."
        except Exception as e:
            search_results = f"Gagal mengambil data dari internet: {str(e)}"
            
        # 3. Sintesis jawaban
        prompt = f"""
        Tugas Pengguna: {task}
        
        Kata Kunci Pencarian: {keyword}
        Hasil Pencarian Web:
        {search_results}
        
        Berdasarkan hasil pencarian di atas, jawablah tugas/pertanyaan pengguna. 
        Jika hasilnya kurang relevan, sebutkan bahwa informasi di internet terbatas.
        """
        
        messages = [
            {"role": "system", "content": "Kamu adalah Web Search Agent di MAMET OS. Tugasmu merangkum hasil pencarian internet untuk pengguna."},
            {"role": "user", "content": prompt}
        ]
        
        return f"🌐 **[Hasil Pencarian Web]**\n\n{self.provider.chat(messages)}"
