"""
MAMET OS - Engineer Sandbox
=============================
Mengelola workspace, review, live, dan rollback untuk Engineer.
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class EngineerSandbox:
    """Dua sandbox + rollback untuk keamanan Engineer."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        
        # Folder sandbox disembunyikan di .sandbox
        self.sandbox_base = self.project_root / ".sandbox"
        self.workspace_dir = self.sandbox_base / "workspace"
        self.review_dir = self.sandbox_base / "review"
        self.rollback_dir = self.sandbox_base / "rollback"
        
        # Live adalah proyek itu sendiri!
        self.live_dir = self.project_root
        
        # Inisialisasi folder sandbox
        self._init_directories()
    
    def _init_directories(self):
        """Buat folder sandbox jika belum ada."""
        for d in [self.sandbox_base, self.workspace_dir, self.review_dir, self.rollback_dir]:
            d.mkdir(exist_ok=True, parents=True)
            
    def _sync_to_workspace(self, relative_path: str):
        """Salin file spesifik dari live ke workspace sebelum diedit."""
        live_file = self.live_dir / relative_path
        work_file = self.workspace_dir / relative_path
        
        if live_file.exists():
            work_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live_file, work_file)
    
    def get_workspace_path(self, relative_path: str = "") -> Path:
        """Dapatkan path di dalam workspace."""
        target = self.workspace_dir / relative_path
        target = target.resolve()
        
        # Security: pastikan tetap di dalam workspace
        if not str(target).startswith(str(self.workspace_dir.resolve())):
            raise PermissionError(f"Akses di luar workspace ditolak: {relative_path}")
        
        return target
    
    def write_file(self, relative_path: str, content: str):
        """Tulis file ke workspace."""
        # Sync file asli ke workspace dulu agar diff utuh jika diedit sebagian (jika ini sistem patch)
        # Tapi karena ini write_file (timpa semua), langsung saja.
        target = self.get_workspace_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {"status": "success", "path": str(target.relative_to(self.project_root))}
    
    def read_file(self, relative_path: str) -> str:
        """Baca file dari workspace."""
        target = self.get_workspace_path(relative_path)
        
        if not target.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {relative_path}")
        
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()
    
    def move_to_review(self, file_paths: list = None):
        """
        Pindahkan hasil dari workspace ke review.
        Jika file_paths kosong, pindahkan semua.
        """
        if file_paths:
            for fp in file_paths:
                src = self.workspace_dir / fp
                dst = self.review_dir / fp
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
        else:
            # Copy semua dari workspace ke review
            if self.review_dir.exists():
                shutil.rmtree(self.review_dir)
            shutil.copytree(self.workspace_dir, self.review_dir, dirs_exist_ok=True)
        
        return {"status": "success", "message": "File dipindahkan ke review"}
    
    def get_diff(self) -> str:
        """
        Dapatkan diff antara live dan review.
        Mengembalikan teks diff sederhana.
        """
        diff_lines = ["📊 **Diff: Review → Live**\n"]
        
        # Bandingkan file di review vs live
        review_files = set()
        for f in self.review_dir.rglob("*"):
            if f.is_file():
                review_files.add(str(f.relative_to(self.review_dir)))
        
        live_files = set()
        for f in self.live_dir.rglob("*"):
            if f.is_file():
                live_files.add(str(f.relative_to(self.live_dir)))
        
        # File baru atau berubah
        for rf in review_files:
            review_path = self.review_dir / rf
            live_path = self.live_dir / rf
            
            if rf not in live_files:
                diff_lines.append(f"➕ **BARU:** {rf}")
                try:
                    content = review_path.read_text(encoding='utf-8')
                    diff_lines.append(f"```\n{content[:300]}\n```\n")
                except:
                    diff_lines.append("_(file binary)_\n")
            else:
                try:
                    review_content = review_path.read_text(encoding='utf-8')
                    live_content = live_path.read_text(encoding='utf-8')
                    if review_content != live_content:
                        diff_lines.append(f"✏️ **BERUBAH:** {rf}")
                        diff_lines.append(f"```diff\n- {live_content[:150]}\n+ {review_content[:150]}\n```\n")
                except:
                    diff_lines.append(f"✏️ **BERUBAH:** {rf} (binary)\n")
        
        # File dihapus
        for lf in live_files:
            if lf not in review_files:
                diff_lines.append(f"➖ **DIHAPUS:** {lf}\n")
        
        return "\n".join(diff_lines)
    
    def approve_to_live(self) -> Dict:
        """
        Setujui perubahan: pindahkan workspace/review ke live dengan backup.
        """
        # Pindahkan workspace ke review secara otomatis jika user bypass 'review' step
        self.move_to_review()
        
        # Cek jika tidak ada perubahan sama sekali
        if not list(self.review_dir.rglob("*")):
            return {"status": "error", "message": "Tidak ada file untuk di-approve."}
            
        # Backup live sebelum diubah
        self.create_backup()
        
        # Hapus live lama? TIDAK. Live adalah root!
        # Kita hanya meng-copy file dari review ke live (timpa).
        for item in self.review_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(self.review_dir)
                dest = self.live_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
        
        # Bersihkan workspace dan review
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
        if self.review_dir.exists():
            shutil.rmtree(self.review_dir)
        
        self.workspace_dir.mkdir(exist_ok=True)
        self.review_dir.mkdir(exist_ok=True)
        
        return {"status": "success", "message": "Perubahan disetujui dan live diperbarui"}
    
    def reject_changes(self) -> Dict:
        """Tolak perubahan: bersihkan workspace dan review."""
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
        if self.review_dir.exists():
            shutil.rmtree(self.review_dir)
        
        self.workspace_dir.mkdir(exist_ok=True)
        self.review_dir.mkdir(exist_ok=True)
        
        return {"status": "success", "message": "Perubahan ditolak, workspace dibersihkan"}
    
    def create_backup(self) -> str:
        """Buat backup live sebelum perubahan atau secara manual."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = self.rollback_dir / backup_name
        
        exclude_dirs = {'.git', 'venv', 'node_modules', '__pycache__', '.next', '.sandbox', 'chroma_db'}
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.live_dir):
                # Filter folder yang dikecualikan
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    # Filter file spesifik yang dikecualikan (opsional)
                    if file.endswith('.sqlite3') or file.endswith('.db'):
                        continue
                        
                    file_path = Path(root) / file
                    try:
                        zf.write(file_path, file_path.relative_to(self.live_dir))
                    except Exception:
                        pass # Abaikan file yang dikunci system
        
        print(f"[SANDBOX] Backup dibuat: {backup_name}")
        
        # Mekanisme Pembersihan Otomatis (Hanya simpan 5 backup terakhir)
        self._cleanup_old_backups(keep=5)
        
        return backup_name
        
    def _cleanup_old_backups(self, keep: int = 5):
        """Hapus backup lama dan hanya sisakan sejumlah `keep`."""
        if not self.rollback_dir.exists():
            return
            
        backups = sorted(self.rollback_dir.glob("backup_*.zip"), key=lambda x: x.stat().st_mtime, reverse=True)
        if len(backups) > keep:
            for old_backup in backups[keep:]:
                try:
                    old_backup.unlink()
                    print(f"[SANDBOX] Menghapus backup lama: {old_backup.name}")
                except Exception as e:
                    print(f"[SANDBOX] Gagal menghapus backup lama: {e}")
    
    def list_backups(self) -> list:
        """List file backup yang tersedia."""
        if not self.rollback_dir.exists():
            return []
        
        backups = []
        for f in sorted(self.rollback_dir.glob("backup_*.zip"), reverse=True):
            backups.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            })
        return backups
    
    def rollback_to(self, backup_filename: str) -> Dict:
        """Kembalikan ke backup tertentu."""
        backup_path = self.rollback_dir / backup_filename
        
        if not backup_path.exists():
            return {"status": "error", "message": f"Backup tidak ditemukan: {backup_filename}"}
        
        # Backup live saat ini dulu
        self.create_backup()
        
        # Ekstrak backup ke live (akan menimpa file yang ada dengan versi lama)
        # Catatan: file yang BARU dibuat sejak backup tidak akan terhapus oleh zip extract, 
        # tapi file lama akan kembali ke versi semula.
        self.live_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(backup_path, 'r') as zf:
            zf.extractall(self.live_dir)
        
        return {"status": "success", "message": f"Rollback ke {backup_filename} berhasil"}