"""
MAMET OS - Database Detector
============================
Mendeteksi jenis database dari file yang diberikan.
Mendukung: SQLite, CSV, JSON
"""

import os

class DatabaseDetector:
    """Deteksi jenis file database secara otomatis."""
    
    @staticmethod
    def detect_type(file_path: str) -> str:
        """
        Mendeteksi tipe database berdasarkan ekstensi dan konten file.
        Returns: 'sqlite', 'csv', 'json', atau 'unknown'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
            
        ext = file_path.split('.')[-1].lower()
        
        # Deteksi SQLite (Cek header file / Magic Bytes)
        if ext in ['db', 'sqlite', 'sqlite3']:
            if DatabaseDetector._is_sqlite3(file_path):
                return 'sqlite'
                
        # Deteksi CSV
        if ext == 'csv':
            return 'csv'
            
        # Deteksi JSON
        if ext == 'json':
            return 'json'
            
        # Fallback deteksi konten jika ekstensi tidak jelas
        if DatabaseDetector._is_sqlite3(file_path):
            return 'sqlite'
            
        return 'unknown'

    @staticmethod
    def _is_sqlite3(file_path: str) -> bool:
        """Cek magic bytes file SQLite."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                return header == b'SQLite format 3\000'
        except Exception:
            return False
