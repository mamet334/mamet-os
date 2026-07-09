"""
MAMET OS - Engineer Main
==========================
Orchestrator Engineer. Menghubungkan semua modul Engineer
dan menyediakan interface ke Main Orchestrator.
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional

from .file_reader import FileReader
from .code_analyzer import CodeAnalyzer
from .safety_guard import SafetyGuard, ActionType


class Engineer:
    """Engineer Basic - Jantung self-maintenance MAMET OS."""
    
    def __init__(self, root_path: str = None):
        if root_path:
            self.root_path = Path(root_path)
        else:
            self.root_path = Path(__file__).parent.parent.parent
            
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
        elif intent == "review":
            return self.review_changes()
        elif intent == "approve":
            return self.approve_changes(message)
        elif intent == "reject":
            return self.reject_changes(message)
        elif intent == "rollback":
            # Ekstrak nama file backup dari pesan
            filename_match = re.search(r'backup_\d{8}_\d{6}\.zip', message)
            if filename_match:
                return self.rollback_to_backup(filename_match.group())
        elif intent == "create_backup":
            return self._handle_create_backup()
        elif intent == "list_backups":
            return self.list_backups()
        elif intent == "delete_rag":
            return self._handle_delete_rag(message)
        elif intent == "list_rag":
            return self._handle_list_rag()
        else:
            result = self._handle_unknown(message)
            print(f"  [ENGINEER.PROCESS] Unknown result: {result}")
            return result
    
    def _detect_intent(self, message: str) -> str:
        """Deteksi intent dari pesan user."""
        msg = message.lower().strip()
        print(f"  [ENGINEER.DETECT] Message lower: {msg}")
        
        if any(word in msg for word in ["buat backup", "bikin backup", "cadangkan"]):
            return "create_backup"
        elif any(word in msg for word in ["analisis", "struktur", "proyek", "codebase"]):
            return "analyze"
        elif any(word in msg for word in ["baca", "lihat", "tampilkan", "isi file", "ringkas", "rangkum"]):
            # Cek apakah pesan lebih condong ke penulisan (ada instruksi isi)
            if "dengan isi" in msg or "content:" in msg:
                return "write_file"
            return "read_file"
        elif any(word in msg for word in ["list", "folder", "direktori", "pohon"]):
            return "list_directory"
        elif any(word in msg for word in ["tulis", "buat", "edit", "ubah", "simpan"]):
            return "write_file"
        elif any(word in msg for word in ["jalankan", "exec", "run", "command"]):
            return "execute_command"
        elif any(word in msg for word in ["review", "diff", "tinjau"]):
            return "review"
        elif any(word in msg for word in ["setujui", "approve", "deploy"]):
            return "approve"
        elif any(word in msg for word in ["tolak", "reject", "batal"]):
            return "reject"
        elif any(word in msg for word in ["rollback", "kembalikan", "restore"]):
            return "rollback"
        elif any(word in msg for word in ["backup", "cadangan"]):
            return "list_backups"
        elif any(word in msg for word in ["hapus rag", "hapus dokumen", "delete rag", "hapus"]):
            # Cek jika pesan mengandung ekstensi file umum (sebagai pengaman tambahan jika hanya bilang 'hapus')
            if "hapus" in msg and re.search(r'\.[a-z0-9]+', msg):
                return "delete_rag"
            elif any(w in msg for w in ["rag", "dokumen"]):
                return "delete_rag"
        elif any(word in msg for word in ["list rag", "daftar rag", "daftar dokumen", "lihat dokumen rag", "isi rag"]):
            return "list_rag"
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
            
    def _handle_delete_rag(self, message: str) -> Dict[str, Any]:
        """Tangani permintaan penghapusan dokumen RAG."""
        import re
        # Ekstrak nama file dari pesan, dukung spasi
        filename_match = re.search(r'(?:hapus rag|hapus dokumen|delete rag|hapus)\s+["\']?(.*?\.([a-zA-Z0-9]+))["\']?\b', message, re.IGNORECASE)
        if not filename_match:
            return {"action": "direct_reply", "response": "❌ Sebutkan nama file dokumen yang ingin dihapus. Contoh: `hapus dokumen laporan.pdf`"}
            
        filename = filename_match.group(1)
        try:
            from rag.rag_engine import RAGEngine
            rag = RAGEngine()
            result = rag.delete_document(filename)
            if result.get("status") == "success":
                return {"action": "direct_reply", "response": f"✅ Dokumen **{filename}** berhasil dihapus dari database RAG."}
            else:
                return {"action": "direct_reply", "response": f"❌ Dokumen **{filename}** tidak ditemukan di database RAG."}
        except Exception as e:
            return {"action": "direct_reply", "response": f"❌ Gagal menghapus dokumen RAG: {str(e)}"}
            
    def _handle_list_rag(self) -> Dict[str, Any]:
        """Tangani permintaan untuk melihat isi RAG."""
        try:
            from rag.rag_engine import RAGEngine
            rag = RAGEngine()
            docs = rag.list_documents()
            stats = rag.get_stats()
            
            if not docs:
                return {"action": "direct_reply", "response": "📭 Database RAG saat ini kosong. Belum ada dokumen yang diunggah."}
                
            response = f"📚 **Database RAG (Total {stats.get('total_documents', 0)} chunks)**\n\n"
            response += "Berikut adalah daftar dokumen yang tersimpan:\n"
            for i, doc in enumerate(docs, 1):
                response += f"{i}. `{doc}`\n"
                
            response += "\n_Gunakan perintah `hapus dokumen <nama_file>` untuk menghapus._"
            return {"action": "direct_reply", "response": response}
        except Exception as e:
            return {"action": "direct_reply", "response": f"❌ Gagal melist dokumen RAG: {str(e)}"}
    
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
        """Tangani permintaan menulis file (mendukung multi-file)."""
        import re
        
        # 1. Cek pola multi-file berstruktur FILE: path \n ``` \n content \n ```
        multi_file_pattern = r'FILE:\s*([^\s]+)\s*\n*```(?:[a-zA-Z0-9_]+)?\n(.*?)\n```'
        matches = re.findall(multi_file_pattern, message, re.DOTALL | re.IGNORECASE)
        
        from engineer.sandbox import EngineerSandbox
        sandbox = EngineerSandbox()
        
        if matches:
            results = []
            files_written = []
            
            for file_path, content in matches:
                # Cek keamanan per file
                check = self.safety_guard.check_action(ActionType.WRITE, file_path)
                if not check.allowed:
                    return {"action": "direct_reply", "response": f"❌ Keamanan: {check.message} untuk {file_path}"}
                
                res = sandbox.write_file(file_path.strip(), content)
                results.append(res)
                files_written.append(file_path.strip())
            
            return {
                "action": "need_approval",
                "response": f"✅ {len(files_written)} file ditulis ke workspace:\n" + "\n".join([f"- `{f}`" for f in files_written]) + "\n\nLanjutkan ke review?",
                "approval_details": {
                    "type": "write_multi_file",
                    "files": files_written,
                    "sandbox_results": results
                }
            }
            
        # 2. Fallback ke single-file legacy (Tulis file X dengan isi: Y)
        path_match = re.search(
            r'(?:tulis|buat|write)\s+(?:file\s+)?["\']?([^\s"\']+\.\w+)["\']?',
            message,
            re.IGNORECASE
        )
        
        if not path_match:
            return {
                "action": "direct_reply",
                "response": "❌ Format tidak dikenali. Gunakan: 'tulis file path/ke/file.py dengan isi: ...' atau format multi-file 'FILE: path...'"
            }
        
        file_path = path_match.group(1)
        
        content_match = re.search(
            r'(?:dengan\s+isi|content)\s*:\s*(.+)',
            message,
            re.IGNORECASE | re.DOTALL
        )
        content = content_match.group(1).strip() if content_match else ""
        
        check = self.safety_guard.check_action(ActionType.WRITE, file_path)
        if not check.allowed:
            return {"action": "direct_reply", "response": check.message}
            
        try:
            result = sandbox.write_file(file_path, content)
            
            return {
                "action": "need_approval",
                "response": f"✅ File ditulis ke workspace:\n```\n{content[:500]}\n```\n\nLanjutkan ke review?",
                "approval_details": {
                    "type": "write_file",
                    "file_path": file_path,
                    "content": content,
                    "sandbox_result": result
                }
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal menulis file: {str(e)}"
            }
    
    async def _handle_execute_command(self, message: str) -> Dict[str, Any]:
        """Tangani permintaan eksekusi command - perlu persetujuan."""
        command = self._extract_command(message)
        
        if not command:
            return {
                "action": "direct_reply",
                "response": "❌ Command apa yang ingin dijalankan? Gunakan: 'jalankan pip install x'"
            }
        
        # Cek keamanan
        check = self.safety_guard.check_action(ActionType.EXECUTE, command)
        if not check.allowed:
            return {"action": "direct_reply", "response": check.message}
        
        approval = self.safety_guard.get_approval_prompt(ActionType.EXECUTE, command)
        
        # Simpan command ke file pending unik agar menghindari konflik paralel
        import random
        task_id = str(random.randint(1000, 9999))
        sandbox_dir = self.root_path / ".sandbox"
        sandbox_dir.mkdir(exist_ok=True)
        (sandbox_dir / f".pending_{task_id}").write_text(command, encoding="utf-8")
        
        return {
            "action": "need_approval",
            "response": f"⚠️ Engineer ingin menjalankan:\n```\n{command}\n```\n\nSilakan setujui dengan mengetik: **setujui {task_id}**",
            "approval_details": {
                "type": "execute_command",
                "command": command,
                "task_id": task_id,
                "approval_prompt": approval
            }
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
                "• ✏️ **Tulis/edit file** - Ketik 'tulis file...' atau tempelkan blok `FILE: path`\n"
                "• ⚡ **Jalankan command** - Ketik 'jalankan...' (perlu persetujuan)\n"
                "• 🔍 **Review perubahan** - Ketik 'review'\n"
                "• ✅ **Setujui perubahan** - Ketik 'setujui'\n"
                "• 🚫 **Tolak perubahan** - Ketik 'tolak'\n"
                "• 💾 **Buat Backup Manual** - Ketik 'buat backup'\n"
                "• 🔄 **Rollback** - Ketik 'rollback' atau 'rollback backup_20260707_120000.zip'\n"
                "• 📦 **List backup** - Ketik 'backup'\n\n"
                "Apa yang ingin Anda lakukan?"
            )
        }
    
    def _handle_create_backup(self) -> Dict[str, Any]:
        """Menangani permintaan pembuatan backup secara manual."""
        try:
            from engineer.sandbox import EngineerSandbox
            sandbox = EngineerSandbox(str(self.root_path))
            
            backup_name = sandbox.create_backup()
            return {
                "action": "direct_reply",
                "response": f"✅ **Backup berhasil dibuat!**\n\nFile tersimpan sebagai: `{backup_name}`\nKetik 'rollback {backup_name}' jika Anda ingin kembali ke titik ini kapan saja."
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal membuat backup manual: {str(e)}"
            }
    
    def _extract_file_path(self, message: str) -> Optional[str]:
        """Ekstrak path file dari pesan."""
        patterns = [
            r'(?:baca|lihat|tampilkan|read|ringkas|rangkum)\s+(?:dokumen\s+|file\s+)?["\']?([^\s"\']+\.(?:py|tsx|ts|js|json|md|txt|css))["\']?',
            r'(?:dokumen|file)\s+["\']?([^\s"\']+)["\']?'
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_path(self, message: str) -> Optional[str]:
        """Ekstrak path direktori dari pesan."""
        match = re.search(
            r'(?:folder|direktori|path)\s+["\']?([^\s"\']+)["\']?',
            message,
            re.IGNORECASE
        )
        if match:
            return match.group(1)
        return None
    
    def _extract_command(self, message: str) -> Optional[str]:
        """Ekstrak command dari pesan."""
        match = re.search(
            r'(?:jalankan|exec|run|command)\s+["\']?(.+?)["\']?$',
            message,
            re.IGNORECASE
        )
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
    
    # ---------- Fungsi Baru untuk Sandbox & Rollback ----------
    
    def review_changes(self) -> Dict[str, Any]:
        """Tampilkan diff antara workspace/review dan live."""
        try:
            from engineer.sandbox import EngineerSandbox
            sandbox = EngineerSandbox()
            
            # Pindahkan workspace ke review dulu
            sandbox.move_to_review()
            
            # Dapatkan diff
            diff = sandbox.get_diff()
            
            return {
                "action": "need_approval",
                "response": diff,
                "approval_details": {
                    "type": "review_changes",
                    "diff": diff
                }
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal review: {str(e)}"
            }
    
    def approve_changes(self, message: str = "") -> Dict[str, Any]:
        """Setujui perubahan (bisa file review atau pending command) dan deploy."""
        try:
            sandbox_dir = self.root_path / ".sandbox"
            pending_files = list(sandbox_dir.glob(".pending_*"))
            
            # Cek apakah ada ID spesifik di pesan
            match = re.search(r'setujui\s+(\d{4})', message, re.IGNORECASE)
            target_file = None
            
            if match:
                task_id = match.group(1)
                target_file = sandbox_dir / f".pending_{task_id}"
                if not target_file.exists():
                    return {"action": "direct_reply", "response": f"❌ Task ID {task_id} tidak ditemukan atau sudah dieksekusi."}
            elif pending_files:
                if len(pending_files) == 1:
                    target_file = pending_files[0]
                else:
                    return {"action": "direct_reply", "response": f"⚠️ Ada {len(pending_files)} eksekusi tertunda. Harap spesifik, misal: 'setujui 1234'"}
                    
            if target_file and target_file.exists():
                command = target_file.read_text(encoding="utf-8").strip()
                target_file.unlink()
                
                from engineer.executor import Executor
                # Eksekusi langsung di project root karena user sudah setuju
                executor = Executor(workspace_dir=str(self.root_path))
                res = executor.execute(command)
                
                if res['status'] == 'success':
                    return {
                        "action": "direct_reply",
                        "response": f"✅ Eksekusi `{command}` berhasil:\n```\n{res['stdout']}\n```"
                    }
                else:
                    return {
                        "action": "direct_reply",
                        "response": f"❌ Eksekusi `{command}` gagal:\n```\n{res['stderr']}\n```"
                    }
            
            # Jika tidak ada pending command, berarti ini persetujuan write_file
            from engineer.sandbox import EngineerSandbox
            sandbox = EngineerSandbox(str(self.root_path))
            
            result = sandbox.approve_to_live()
            
            return {
                "action": "direct_reply",
                "response": f"✅ Perubahan file disetujui! {result['message']}\n\nBackup telah dibuat di folder rollback."
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal approve: {str(e)}"
            }
    
    def reject_changes(self, message: str = "") -> Dict[str, Any]:
        """Tolak perubahan (file review atau pending command)."""
        try:
            sandbox_dir = self.root_path / ".sandbox"
            pending_files = list(sandbox_dir.glob(".pending_*"))
            
            match = re.search(r'tolak\s+(\d{4})', message, re.IGNORECASE)
            if match:
                task_id = match.group(1)
                target = sandbox_dir / f".pending_{task_id}"
                if target.exists():
                    target.unlink()
                    return {"action": "direct_reply", "response": f"🚫 Eksekusi task {task_id} dibatalkan."}
            elif pending_files:
                for f in pending_files:
                    f.unlink()
                return {"action": "direct_reply", "response": "🚫 Semua eksekusi tertunda dibatalkan."}
                
            from engineer.sandbox import EngineerSandbox
            sandbox = EngineerSandbox(str(self.root_path))
            
            result = sandbox.reject_changes()
            
            return {
                "action": "direct_reply",
                "response": f"🚫 Perubahan ditolak. {result['message']}"
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal reject: {str(e)}"
            }
    
    def rollback_to_backup(self, filename: str) -> Dict[str, Any]:
        """Rollback ke backup tertentu."""
        try:
            from engineer.sandbox import EngineerSandbox
            sandbox = EngineerSandbox(str(self.root_path))
            
            result = sandbox.rollback_to(filename)
            
            return {
                "action": "direct_reply",
                "response": f"🔄 {result['message']}\n\nSistem telah dikembalikan ke {filename}"
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal rollback: {str(e)}"
            }
    
    def list_backups(self) -> Dict[str, Any]:
        """List backup yang tersedia."""
        try:
            from engineer.sandbox import EngineerSandbox
            sandbox = EngineerSandbox(str(self.root_path))
            
            backups = sandbox.list_backups()
            
            if not backups:
                return {
                    "action": "direct_reply",
                    "response": "📦 Belum ada backup."
                }
            
            lines = ["📦 **Backup Tersedia:**\n"]
            for b in backups[:10]:
                size_kb = b['size'] / 1024
                lines.append(f"- {b['filename']} ({size_kb:.1f} KB)")
            
            return {
                "action": "direct_reply",
                "response": "\n".join(lines)
            }
        except Exception as e:
            return {
                "action": "direct_reply",
                "response": f"❌ Gagal list backup: {str(e)}"
            }