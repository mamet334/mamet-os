"""
MAMET OS - User Memory (SQLite)
================================
Menyimpan fakta personal, preferensi, dan riwayat percakapan user.
Mendukung multi-identitas (ganti email = ganti database).
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class UserMemory:
    """Memori jangka panjang user berbasis SQLite."""
    
    def __init__(self, email: str = "default"):
        """
        Inisialisasi User Memory.
        
        Args:
            email: Email user (untuk multi-identitas)
        """
        # Tentukan folder database
        base_dir = os.path.join(os.path.expanduser("~"), ".mamet", email)
        os.makedirs(base_dir, exist_ok=True)
        
        self.db_path = os.path.join(base_dir, "memory.db")
        self._init_database()
        print(f"[MEMORY] Database siap: {self.db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Mendapatkan koneksi ke database dengan penanganan multi-threading."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=10.0  # Tunggu hingga 10 detik jika DB di-lock oleh thread lain
        )
        conn.row_factory = sqlite3.Row
        
        # Aktifkan WAL (Write-Ahead Logging) mode
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        
        return conn

    def _init_database(self):
        """Buat tabel jika belum ada."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT NOT NULL,
                    source TEXT DEFAULT 'conversation',
                    confidence REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    column_name TEXT DEFAULT 'kolom2',
                    message TEXT NOT NULL,
                    response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
    @property
    def is_legacy_mode(self) -> bool:
        """Cek apakah sistem dalam status Warisan Digital (Read-Only facts)."""
        return self.get_preference("legacy_mode", "false").lower() == "true"
        
    def enable_legacy_mode(self):
        """Mengunci memori menjadi Warisan Digital (fakta tidak bisa diubah lagi)."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
                ("legacy_mode", "true", datetime.now())
            )
            conn.commit()
            print(f"[LEGACY] Mode Warisan Digital DIAKTIFKAN untuk user {self.db_path}")
            
    def disable_legacy_mode(self):
        """Membuka kembali memori (kembali ke mode asisten normal)."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
                ("legacy_mode", "false", datetime.now())
            )
            conn.commit()
            print(f"[LEGACY] Mode Warisan Digital DINONAKTIFKAN.")
    
    def add_fact(self, fact: str, source: str = "conversation", confidence: float = 0.5, ttl_days: int = 30) -> int:
        """
        Tambahkan fakta baru tentang user.
        
        Args:
            fact: Fakta yang diingat
            source: Sumber fakta (conversation, manual, extraction)
            confidence: Skor kepercayaan (0.0 - 1.0)
            ttl_days: Masa berlaku fakta dalam hari
            
        Returns:
            ID fakta yang baru dibuat
        """
        if self.is_legacy_mode:
            print("[MEMORY-LEGACY] Menolak fakta baru: Memori terkunci (Legacy Mode).")
            return -1
            
        expires_at = datetime.now() + timedelta(days=ttl_days)
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO facts (fact, source, confidence, expires_at) VALUES (?, ?, ?, ?)",
                (fact, source, confidence, expires_at)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_facts(self, active_only: bool = True, min_confidence: float = 0.3) -> List[Dict]:
        """
        Ambil fakta tentang user.
        
        Args:
            active_only: Hanya fakta yang masih aktif
            min_confidence: Confidence minimum
            
        Returns:
            List fakta
        """
        query = "SELECT id, fact, source, confidence, created_at, expires_at FROM facts WHERE confidence >= ?"
        params = [min_confidence]
        
        if active_only:
            query += " AND is_active = 1 AND (expires_at IS NULL OR expires_at > ?)"
            params.append(datetime.now())
        
        query += " ORDER BY confidence DESC"
        
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def deactivate_fact(self, fact_id: int):
        """Nonaktifkan fakta (soft delete)."""
        if self.is_legacy_mode:
            print("[MEMORY-LEGACY] Menolak hapus fakta: Memori terkunci (Legacy Mode).")
            return
            
        with self._get_connection() as conn:
            conn.execute("UPDATE facts SET is_active = 0 WHERE id = ?", (fact_id,))
            conn.commit()
    
    def cleanup_expired_facts(self) -> int:
        """Hapus fakta yang sudah kadaluarsa. Return jumlah yang dihapus."""
        if self.is_legacy_mode:
            return 0  # Jangan hapus apapun di mode warisan
            
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE facts SET is_active = 0 WHERE expires_at <= ? AND is_active = 1",
                (datetime.now(),)
            )
            conn.commit()
            return cursor.rowcount
    
    def set_preference(self, key: str, value: str):
        """Simpan preferensi user."""
        if self.is_legacy_mode and key != "legacy_mode":
            print("[MEMORY-LEGACY] Menolak ubah preferensi: Memori terkunci (Legacy Mode).")
            return
            
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, datetime.now())
            )
            conn.commit()
    
    def get_preference(self, key: str, default: str = None) -> str:
        """Ambil preferensi user."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM preferences WHERE key = ?", (key,)
            ).fetchone()
            return row[0] if row else default
    
    def get_all_preferences(self) -> Dict[str, str]:
        """Ambil semua preferensi."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT key, value FROM preferences").fetchall()
            return {row[0]: row[1] for row in rows}
    
    def save_conversation(self, column: str, message: str, response: str):
        """Simpan riwayat percakapan."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO conversations (column_name, message, response) VALUES (?, ?, ?)",
                (column, message, response)
            )
            conn.commit()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Ambil percakapan terbaru."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def get_facts_context(self) -> str:
        """
        Format fakta sebagai konteks untuk LLM.
        Digunakan saat membangun respons di Asisten Pribadi.
        """
        facts = self.get_facts(active_only=True, min_confidence=0.3)
        if not facts:
            return ""
        
        if self.is_legacy_mode:
            lines = ["SYSTEM ALERT: Saat ini kamu berjalan dalam LEGACY MODE (Mode Warisan). Kamu bertindak sebagai representasi/warisan pemikiran dari user sebelumnya. Gunakan fakta berikut untuk mensimulasikan pengetahuannya:"]
        else:
            lines = ["Fakta yang saya ingat tentang Anda:"]
            
        for f in facts[:10]:  # Batasi 10 fakta
            lines.append(f"- {f['fact']} (confidence: {f['confidence']:.0%})")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """Statistik memori."""
        with self._get_connection() as conn:
            total_facts = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            active_facts = conn.execute("SELECT COUNT(*) FROM facts WHERE is_active = 1").fetchone()[0]
            total_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            total_preferences = conn.execute("SELECT COUNT(*) FROM preferences").fetchone()[0]
        
        return {
            "total_facts": total_facts,
            "active_facts": active_facts,
            "total_conversations": total_conversations,
            "total_preferences": total_preferences,
            "db_path": self.db_path
        }