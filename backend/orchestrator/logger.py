import sys
import os
import datetime
from pathlib import Path
from collections import deque

class MametLogger:
    """Interceptor untuk stdout dan stderr agar log tersimpan di file dan bisa dibaca UI (Pilar D3)."""
    
    _instance = None
    
    @classmethod
    def setup(cls):
        if cls._instance is None:
            cls._instance = cls()
            sys.stdout = cls._instance
            
            # Buat interceptor stderr sederhana
            class StderrLogger:
                def write(self, msg):
                    cls._instance.write_err(msg)
                def flush(self):
                    cls._instance.terminal_err.flush()
            sys.stderr = StderrLogger()
            print(f"[LOGGER] MametLogger aktif dan menulis ke path: {cls._instance.log_file}")
    
    def __init__(self, log_dir=None):
        self.terminal = sys.stdout
        self.terminal_err = sys.stderr
        
        if log_dir is None:
            self.log_dir = Path.home() / ".mamet" / "logs"
        else:
            self.log_dir = Path(log_dir)
            
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "mamet.log"
        
        # Rotasi log manual jika lebih dari 5MB
        if self.log_file.exists() and self.log_file.stat().st_size > 5 * 1024 * 1024:
            self.log_file.rename(self.log_dir / f"mamet_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log")

    def write(self, message):
        self.terminal.write(message)
        self._write_to_file(message)
        
    def write_err(self, message):
        self.terminal_err.write(message)
        if not message or message == '\n':
            return
        self._write_to_file(f"[ERROR] {message}")

    def _write_to_file(self, message):
        if not message or message == '\n':
            return
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        lines = message.splitlines()
        
        formatted_lines = []
        for line in lines:
            if not line.strip():
                continue
            if line.startswith("["):
                formatted_lines.append(f"[{timestamp}] {line}\n")
            else:
                formatted_lines.append(f"[{timestamp}] [SYS] {line}\n")
                
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.writelines(formatted_lines)
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            pass

    def flush(self):
        self.terminal.flush()
        
    @staticmethod
    def get_recent_logs(lines=100, log_dir=None):
        log_dir = Path(log_dir) if log_dir else Path.home() / ".mamet" / "logs"
        log_file = log_dir / "mamet.log"
        
        if not log_file.exists():
            return []
            
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                # Menggunakan deque untuk mengambil baris terakhir secara efisien
                return list(deque(f, lines))
        except Exception:
            return []
