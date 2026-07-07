"""
MAMET OS - Safety Guard (Engineer)
====================================
Aturan keamanan untuk Engineer.
Semua tindakan destruktif wajib persetujuan user.
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    INSTALL = "install"
    GIT_PUSH = "git_push"


@dataclass
class SafetyCheck:
    """Hasil pengecekan keamanan."""
    allowed: bool
    requires_approval: bool
    message: str
    details: Dict[str, Any]


class SafetyGuard:
    """Pagar keamanan Engineer."""
    
    PROTECTED_FILES = [
        ".gitignore",
        "SPESIFIKASI.md",
        "backend/auth/auth_handler.py"
    ]
    
    RESTRICTED_FOLDERS = [
        "venv",
        "node_modules",
        ".next",
        ".git"
    ]
    
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
        details = details or {}
        
        if action_type == ActionType.READ:
            return SafetyCheck(
                allowed=True,
                requires_approval=False,
                message="✅ Membaca file diizinkan",
                details=details
            )
        
        if self._is_protected(target):
            return SafetyCheck(
                allowed=False,
                requires_approval=True,
                message=f"🔒 File '{target}' dilindungi. Tidak bisa diubah.",
                details={"reason": "protected_file"}
            )
        
        if self._is_restricted(target):
            return SafetyCheck(
                allowed=False,
                requires_approval=True,
                message=f"🔒 Folder '{target}' dibatasi aksesnya.",
                details={"reason": "restricted_folder"}
            )
        
        if action_type == ActionType.EXECUTE:
            if self._is_forbidden_command(target):
                return SafetyCheck(
                    allowed=False,
                    requires_approval=True,
                    message=f"⛔ Command '{target}' dilarang.",
                    details={"reason": "forbidden_command"}
                )
        
        return SafetyCheck(
            allowed=True,
            requires_approval=True,
            message=f"⚠️ Tindakan '{action_type.value}' pada '{target}' memerlukan persetujuan.",
            details={"action_type": action_type.value, "target": target}
        )
    
    def _is_protected(self, target: str) -> bool:
        for protected in self.PROTECTED_FILES:
            if protected in target:
                return True
        return False
    
    def _is_restricted(self, target: str) -> bool:
        for restricted in self.RESTRICTED_FOLDERS:
            if restricted in target:
                return True
        return False
    
    def _is_forbidden_command(self, command: str) -> bool:
        command_lower = command.lower()
        for forbidden in self.FORBIDDEN_COMMANDS:
            if forbidden in command_lower:
                return True
        return False
    
    def get_approval_prompt(self, action_type: ActionType, target: str, diff: str = "") -> Dict[str, Any]:
        return {
            "action_type": action_type.value,
            "target": target,
            "diff": diff,
            "message": f"Engineer ingin melakukan '{action_type.value}' pada '{target}'. Setujui?",
            "options": ["setuju", "tolak", "lihat_diff"]
        }