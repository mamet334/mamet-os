"""
MAMET OS - Engineer Executor
===============================
Menjalankan command dengan safety guard.
"""

import subprocess
import os
from typing import Dict
from pathlib import Path
from .safety_guard import SafetyGuard, ActionType


class Executor:
    """Eksekusi command dengan pengamanan."""
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = Path(workspace_dir or os.getcwd())
        self.safety_guard = SafetyGuard()
    
    def execute(self, command: str, cwd: str = None) -> Dict:
        """
        Jalankan command.
        
        Args:
            command: Command yang akan dijalankan
            cwd: Working directory (default: workspace)
            
        Returns:
            Dict dengan stdout, stderr, return_code
        """
        # Cek keamanan
        check = self.safety_guard.check_action(ActionType.EXECUTE, command)
        if not check.allowed:
            return {
                "status": "error",
                "message": check.message,
                "stdout": "",
                "stderr": check.message,
                "return_code": -1
            }
        
        # Tentukan working directory
        working_dir = cwd or str(self.workspace_dir)
        os.makedirs(working_dir, exist_ok=True)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=60  # Maksimal 60 detik
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:2000],
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Command timeout (60 detik)",
                "stdout": "",
                "stderr": "Timeout",
                "return_code": -1
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
    
    def run_python(self, script: str, cwd: str = None) -> Dict:
        """Jalankan script Python."""
        # Simpan script ke file sementara di workspace
        temp_file = self.workspace_dir / "_temp_script.py"
        temp_file.write_text(script, encoding='utf-8')
        
        result = self.execute(f"python {temp_file}", cwd=cwd)
        
        # Hapus file sementara
        if temp_file.exists():
            temp_file.unlink()
        
        return result
    
    def run_npm(self, command: str, cwd: str = None) -> Dict:
        """Jalankan npm command."""
        return self.execute(f"npm {command}", cwd=cwd)
    
    def run_git(self, command: str, cwd: str = None) -> Dict:
        """Jalankan git command."""
        # Hanya izinkan git commands yang aman
        safe_commands = ["status", "diff", "log", "branch", "add", "commit"]
        cmd_parts = command.strip().split()
        
        if not cmd_parts or cmd_parts[0] not in safe_commands:
            return {
                "status": "error",
                "message": f"Git command '{cmd_parts[0]}' tidak diizinkan. Hanya: {', '.join(safe_commands)}",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }
        
        return self.execute(f"git {command}", cwd=cwd)