"""
MAMET OS - File Reader (Engineer)
==================================
Membaca file dan struktur direktori proyek.
Digunakan oleh Engineer untuk menganalisis codebase.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional


class FileReader:
    """Membaca dan menjelajahi struktur proyek."""
    
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path or os.getcwd())
    
    def list_directory(self, path: str = ".", recursive: bool = False, depth: int = 2) -> List[str]:
        """List file dan folder dalam direktori."""
        target = (self.root_path / path).resolve()
        if not target.exists():
            return [f"❌ Path tidak ditemukan: {path}"]
        
        result = []
        current_depth = 0
        
        def _walk(p: Path, d: int):
            if d > depth:
                return
            try:
                for item in sorted(p.iterdir()):
                    relative = item.relative_to(self.root_path)
                    if item.is_dir() and not item.name.startswith('.') and item.name not in ['venv', 'node_modules', '__pycache__', '.next']:
                        result.append(f"📁 {relative}/")
                        if recursive:
                            _walk(item, d + 1)
                    elif item.is_file():
                        result.append(f"📄 {relative}")
            except PermissionError:
                result.append(f"🔒 {p.relative_to(self.root_path)}/ (no permission)")
        
        _walk(target, current_depth)
        return result
    
    def read_file(self, file_path: str) -> str:
        """Baca isi file."""
        target = (self.root_path / file_path).resolve()
        
        if not target.exists():
            return f"❌ File tidak ditemukan: {file_path}"
        
        if not str(target).startswith(str(self.root_path)):
            return "❌ Akses ditolak: file di luar root proyek"
        
        try:
            with open(target, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"❌ Gagal membaca file: {str(e)}"
    
    def get_project_tree(self, max_depth: int = 3) -> str:
        """Dapatkan struktur pohon proyek."""
        items = self.list_directory(recursive=True, depth=max_depth)
        return "\n".join(items)
    
    def search_files(self, pattern: str) -> List[str]:
        """Cari file berdasarkan nama."""
        result = []
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden folders dan virtual environments
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'node_modules', '__pycache__', '.next']]
            for file in files:
                if pattern.lower() in file.lower():
                    full_path = Path(root) / file
                    result.append(str(full_path.relative_to(self.root_path)))
        return result