"""
MAMET OS - Engineer Main
==========================
Orchestrator Engineer. Menghubungkan semua modul Engineer
dan menyediakan interface ke Main Orchestrator.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from .file_reader import FileReader
from .code_analyzer import CodeAnalyzer
from .safety_guard import SafetyGuard, ActionType


class Engineer:
    """Engineer Basic - Jantung self-maintenance MAMET OS."""
    
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path or __file__).parent.parent.parent
        self.file_reader = FileReader(str(self.root_path))
        self.code_analyzer = CodeAnalyzer(str(self.root_path))
        self.safety_guard = SafetyGuard()
        print(f"  [ENGINEER] Initialized with root: {self.root_path}")
    
    async def process(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Proses permintaan ke Engineer.
        """
        print(f"  [ENGINEER.PROCESS] Message: {message}")
        intent = self._detect_intent(message)
        print(f"  [ENGINEER.PROCESS] Intent: {intent}")
        
        if intent == "analyze":
            print("  [ENGINEER.PROCESS] Handling analyze...")
            result = await self._handle_analyze()
            print(f"  [ENGINEER.PROCESS] Analyze result: {result}")
            return result
        elif intent == "read_file":
            return await self._handle_read_file(message)
        elif intent == "list_directory":
            return await self._handle_list_directory(message)
        elif intent == "write_file":
            return await self._handle_write_file(message)
        elif intent == "execute_command":
            return await self._handle_execute_command(message)
        else:
            result = self._handle_unknown(message)
            print(f"  [ENGINEER.PROCESS] Unknown result: {result}")
            return result
    
    def _detect_intent(self, message: str) -> str:
        """Deteksi intent dari pesan user."""
        msg = message.lower().strip()
        print(f"  [ENGINEER.DETECT] Message lower: {msg}")
        
        if any(word in msg for word in ["analisis", "struktur", "proyek", "codebase"]):
            return "analyze"
        elif any(word in msg for word in ["baca", "lihat", "tampilkan", "isi file"]):
            return "read_file"
        elif any(word in msg for word in ["list", "folder", "direktori", "pohon"]):
            return "list_directory"
        elif any(word in msg for word in ["tulis", "buat", "edit", "ubah", "simpan"]):
            return "write_file"
        elif any(word in msg for word in ["jalankan", "exec", "run", "command"]):
            return "execute_command"
        else:
            return "unknown"
    
    async def _handle_analyze(self) -> Dict[str, Any]:
        """Tangani permintaan analisis proyek."""
        print("  [ENGINEER.ANALYZE] Starting analysis...")
        try:
            analysis = self.code_analyzer.analyze_project()
            print(f"  [ENGINEER.ANALYZE] Analysis done: {analysis.get('summary', {})}")
            tree = self.file_reader.get_project_tree(max_depth=2)
            print(f"  [ENGINEER.ANALYZE] Tree length: {len(tree)}")
            
            response_text = self._format_analysis_response(analysis, tree)
            
            return {
                "action": "direct_reply",
                "response": response_text,
                "analysis": analysis,
                "project_tree": tree
            }
        except Exception as e:
            print(f"  [ENGINEER.ANALYZE] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal menganalisis proyek: {str(e)}"
            }
    
    async def _handle_read_file(self, message: str) -> Dict[str, Any]:
        """Tangani permintaan membaca file."""
        file_path = self._extract_file_path(message)
        
        if not file_path:
            return {"action": "direct_reply", "response": "❌ File apa yang ingin dibaca? Sebutkan path-nya."}
        
        check = self.safety_guard.check_action(ActionType.READ, file_path)
        if not check.allowed:
            return {"action": "direct_reply", "response": check.message}
        
        content = self.file_reader.read_file(file_path)
        
        return {
            "action": "direct_reply",
            "response": f"📄 **{file_path}**\n\n```\n{content[:2000]}\n```\n\n_(File lengkap tersedia)_",
            "file_content": content
        }
    
    async def _handle_list_directory(self, message: str) -> Dict[str, Any]:
        """Tangani permintaan list direktori."""
        path = self._extract_path(message) or "."
        items = self.file_reader.list_directory(path, recursive=True, depth=2)
        
        return {
            "action": "direct_reply",
            "response": f"📁 **Direktori: {path}**\n\n" + "\n".join(items[:50]),
            "directory_list": items
        }
    
    async def _handle_write_file(self, message: str) -> Dict[str, Any]:
        """Tangani permintaan menulis file."""
        return {
            "action": "need_approval",
            "response": "⚠️ Engineer ingin menulis file. Fitur ini memerlukan persetujuan Anda terlebih dahulu.",
            "approval_details": {
                "type": "write_file",
                "message": message
            }
        }
    
    async def _handle_execute_command(self, message: str) -> Dict[str, Any]:
        """Tangani permintaan eksekusi command."""
        command = self._extract_command(message)
        
        if not command:
            return {"action": "direct_reply", "response": "❌ Command apa yang ingin dijalankan?"}
        
        check = self.safety_guard.check_action(ActionType.EXECUTE, command)
        if not check.allowed:
            return {"action": "direct_reply", "response": check.message}
        
        approval = self.safety_guard.get_approval_prompt(ActionType.EXECUTE, command)
        
        return {
            "action": "need_approval",
            "response": f"⚠️ Engineer ingin menjalankan:\n```\n{command}\n```\n\nSilakan setujui atau tolak.",
            "approval_details": approval
        }
    
    def _handle_unknown(self, message: str) -> Dict[str, Any]:
        """Tangani pesan yang tidak dikenali."""
        return {
            "action": "direct_reply",
            "response": (
                "🔧 **Engineer MAMET OS siap membantu.**\n\n"
                "Saya bisa:\n"
                "• 📊 **Analisis proyek** - Ketik 'analisis proyek'\n"
                "• 📄 **Baca file** - Ketik 'baca file backend/main.py'\n"
                "• 📁 **List direktori** - Ketik 'list folder'\n"
                "• ✏️ **Tulis/edit file** - Ketik 'tulis file...' (perlu persetujuan)\n"
                "• ⚡ **Jalankan command** - Ketik 'jalankan...' (perlu persetujuan)\n\n"
                "Apa yang ingin Anda lakukan?"
            )
        }
    
    def _extract_file_path(self, message: str) -> Optional[str]:
        """Ekstrak path file dari pesan."""
        import re
        patterns = [
            r'(?:baca|lihat|tampilkan|read)\s+(?:file\s+)?["\']?([^\s"\']+\.(?:py|tsx|ts|js|json|md|txt|css))["\']?',
            r'file\s+["\']?([^\s"\']+)["\']?'
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_path(self, message: str) -> Optional[str]:
        """Ekstrak path direktori dari pesan."""
        import re
        match = re.search(r'(?:folder|direktori|path)\s+["\']?([^\s"\']+)["\']?', message, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _extract_command(self, message: str) -> Optional[str]:
        """Ekstrak command dari pesan."""
        import re
        match = re.search(r'(?:jalankan|exec|run|command)\s+["\']?(.+?)["\']?$', message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def _format_analysis_response(self, analysis: Dict[str, Any], tree: str) -> str:
        """Format hasil analisis untuk respons."""
        summary = analysis.get("summary", {})
        backend = analysis.get("backend", {})
        frontend = analysis.get("frontend", {})
        
        return (
            f"📊 **Analisis Proyek MAMET OS**\n\n"
            f"**Ringkasan:**\n"
            f"• Backend: {summary.get('backend_framework', 'Unknown')}\n"
            f"• Frontend: {summary.get('frontend_framework', 'Unknown')}\n"
            f"• Total file: {summary.get('total_files', 0)}\n"
            f"• Routes: {summary.get('routes_count', 0)}\n"
            f"• Komponen: {summary.get('components_count', 0)}\n\n"
            f"**Struktur Proyek:**\n```\n{tree[:1000]}\n```\n\n"
            f"_Ketik 'list folder' untuk detail lengkap_"
        )