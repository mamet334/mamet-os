"""
MAMET OS - Planning Engine
============================
Membuat rencana tindakan secara SIMBOLIK (tanpa LLM).
"""
import re

class PlanningEngine:
    """Mesin perencana simbolik."""
    
    def __init__(self):
        self.rules = {}
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Daftarkan aturan planning default."""
        self.rules = {
            "kolom1": {
                "steps": ["check_rag", "embed_query", "search_similar", "return_results"],
                "description": "Pencarian cepat via RAG"
            },
            "kolom2": {
                "steps": ["check_user_memory", "check_rag", "check_lego_modules", "decide_if_need_agent", "respond"],
                "description": "Asisten pribadi dengan memori"
            },
            "kolom3": {
                "steps": ["check_rag_knowledge", "analyze_codebase", "plan_changes", "request_approval"],
                "description": "Engineer: analisis dan usulan perubahan"
            }
        }
    
    async def initialize(self):
        """Inisialisasi planning engine."""
        print(f"  [PLANNER] {len(self.rules)} aturan terdaftar")
    
    async def create_plan(self, user_id: str, column: str, message: str) -> dict:
        """
        Buat rencana berdasarkan kolom dan pesan user.
        """
        rule = self.rules.get(column, self.rules["kolom2"])
        intent = self._detect_intent(message)
        
        plan = {
            "column": column,
            "intent": intent,
            "steps": list(rule["steps"]),
            "original_message": message,
            "created_at": None
        }
        
        if intent == "search":
            plan["steps"].insert(0, "parse_search_query")
        elif intent == "command":
            plan["steps"].insert(0, "parse_command")
        elif intent == "question":
            plan["steps"].insert(0, "analyze_question_type")
            
        # Deteksi Sub-Agent (Fase 3)
        agent_pattern = r'\b(?:agen|agent|pakai agen|gunakan agen)(?:(?:\s+\w+)?\s+)?(database|research|web|file)\b'
        agent_match = re.search(agent_pattern, message.lower())
        if agent_match:
            plan["sub_agent"] = agent_match.group(1)
            plan["steps"].append("invoke_sub_agent")
        
        return plan
    
    def _detect_intent(self, message: str) -> str:
        """Deteksi intent yang lebih cerdas (RegEx & Pola Kalimat)."""
        msg = message.lower().strip()
        
        # Pola Command (instruksi tegas di awal kalimat)
        command_pattern = r'^(tolong\s+)?(buat|bikin|tambah|hapus|edit|ubah|perbaiki|tulis|jalankan|eksekusi)\b'
        if re.search(command_pattern, msg):
            return "command"
            
        # Pola Search (pencarian dokumen atau informasi spesifik)
        search_pattern = r'\b(cari|temukan|cek dokumen|di file mana|dimana|siapa|kapan)\b'
        if re.search(search_pattern, msg):
            return "search"
            
        # Pola Question (pertanyaan tentang sesuatu)
        question_pattern = r'^(apa|bagaimana|kenapa|mengapa|apakah|bisa|bisakah)\b|\?$'
        if re.search(question_pattern, msg):
            return "question"
        
        return "chat"
    
    def add_rule(self, column: str, steps: list, description: str = ""):
        """Tambah aturan baru (untuk ekspansi Lego)."""
        self.rules[column] = {
            "steps": steps,
            "description": description
        }