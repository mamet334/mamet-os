"""
MAMET OS - Safety Guard (Engineer)
====================================
Aturan keamanan untuk Engineer.
Semua tindakan destruktif wajib persetujuan user.
"""

from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    READ = "read"          # Baca file - tidak perlu izin
    WRITE = "write"        # Tulis file - perlu izin
    DELETE = "delete"      # Hapus file - perlu izin
    EXECUTE = "execute"    # Jalankan command - perlu izin
    INSTALL = "install"    # Install package - perlu izin
    GIT_PUSH = "git_push"  # Push ke git - perlu izin


@dataclass
class SafetyCheck:
    """Hasil pengecekan keamanan."""
    allowed: bool
    requires_approval: bool
    message: str
    details: Dict[str, Any]


class SafetyGuard:
    """Pagar keamanan Engineer."""
    
    # File yang TIDAK BOLEH diubah sama sekali
    PROTECTED_FILES = [
        ".gitignore",
        "SPESIFIKASI.md",
        "backend/auth/auth_handler.py"
    ]
    
    # Folder yang dibatasi aksesnya
    RESTRICTED_FOLDERS = [
        "venv",
        "node_modules",
        ".next",
        ".git"
    ]
    
    # Command yang dilarang
    FORBIDDEN_COMMANDS = [
        "rm -rf /",
        "format c:",
        "shutdown",
        "restart"
    ]
    
    def check_action(
        self,
        action_type: ActionType,
        target: str = "",
        details: Dict[str, Any] = None
    ) -> SafetyCheck:
        """
        Cek apakah suatu tindakan aman dilakukan.
        
        Returns:
            SafetyCheck dengan status allowed dan requires_approval
        """
        details = details or {}
        
        # READ selalu diizinkan tanpa persetujuan
        if action_type == ActionType.READ:
            return SafetyCheck(
                allowed=True,
                requires_approval=False,
                message="✅ Membaca file diizinkan",
                details=details
            )
        
        # Cek protected files
        if self._is_protected(target):
            return SafetyCheck(
                allowed=False,
                requires_approval=True,
                message=f"🔒 File '{target}' dilindungi. Tidak bisa diubah.",
                details={"reason": "protected_file"}
            )
        
        # Cek restricted folders
        if self._is_restricted(target):
            return SafetyCheck(
                allowed=False,
                requires_approval=True,
                message=f"🔒 Folder '{target}' dibatasi aksesnya.",
                details={"reason": "restricted_folder"}
            )
        
        # Cek forbidden commands
        if action_type == ActionType.EXECUTE:
            if self._is_forbidden_command(target):
                return SafetyCheck(
                    allowed=False,
                    requires_approval=True,
                    message=f"⛔ Command '{target}' dilarang.",
                    details={"reason": "forbidden_command"}
                )
        
        # Semua tindakan lain: perlu persetujuan user
        return SafetyCheck(
            allowed=True,
            requires_approval=True,
            message=f"⚠️ Tindakan '{action_type.value}' pada '{target}' memerlukan persetujuan.",
            details={"action_type": action_type.value, "target": target}
        )
    
    def _is_protected(self, target: str) -> bool:
        """Cek apakah file termasuk dalam protected files."""
        for protected in self.PROTECTED_FILES:
            if protected in target:
                return True
        return False
    
    def _is_restricted(self, target: str) -> bool:
        """Cek apakah target ada di folder terbatas."""
        for restricted in self.RESTRICTED_FOLDERS:
            if restricted in target:
                return True
        return False
    
    def _is_forbidden_command(self, command: str) -> bool:
        """Cek apakah command dilarang."""
        command_lower = command.lower()
        for forbidden in self.FORBIDDEN_COMMANDS:
            if forbidden in command_lower:
                return True
        return False
    
    def get_approval_prompt(self, action_type: ActionType, target: str, diff: str = "") -> Dict[str, Any]:
        """Buat prompt persetujuan untuk user."""
        return {
            "action_type": action_type.value,
            "target": target,
            "diff": diff,
            "message": f"Engineer ingin melakukan '{action_type.value}' pada '{target}'. Setujui?",
            "options": ["setuju", "tolak", "lihat_diff"]
        }