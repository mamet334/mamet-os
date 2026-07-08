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
        emotion = self._detect_emotion(message)
        
        # Deteksi Multi-Langkah
        # Kita memisahkan string berdasarkan kata hubung, pastikan tidak memakan kata kerja (seperti 'simpan' atau 'jadikan')
        multi_step_keywords = r'(?:\s*,\s*lalu\s+|\s+lalu\s+|\s*,\s*kemudian\s+|\s+kemudian\s+|\s+setelah\s+itu\s+|\s*,\s*dan\s+)'
        is_multi_step = False
        sub_tasks = []
        msg_lower = message.lower()
        if re.search(multi_step_keywords, msg_lower):
            is_multi_step = True
            raw_tasks = re.split(multi_step_keywords, msg_lower)
            # Ambil bagian task saja
            sub_tasks = [t.strip() for t in raw_tasks if t.strip()]
        
        plan = {
            "column": column,
            "intent": intent,
            "emotion": emotion,
            "requires_structured_format": intent == "summarize",
            "is_multi_step": is_multi_step,
            "sub_tasks": sub_tasks,
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
            
        # Pola Summarize (meringkas, merangkum, resume)
        summarize_pattern = r'\b(ringkas|rangkum|resume|buatkan kesimpulan|summary|inti dari|ringkasan)\b'
        if re.search(summarize_pattern, msg):
            return "summarize"
            
        # Pola Search (pencarian dokumen atau informasi spesifik)
        search_pattern = r'\b(cari|temukan|cek dokumen|di file mana|dimana|siapa|kapan)\b'
        if re.search(search_pattern, msg):
            return "search"
            
        # Pola Question (pertanyaan tentang sesuatu)
        question_pattern = r'^(apa|bagaimana|kenapa|mengapa|apakah|bisa|bisakah)\b|\?$'
        if re.search(question_pattern, msg):
            return "question"
        
        return "chat"
        
    def _detect_emotion(self, message: str) -> str:
        """Mendeteksi emosi atau nada bicara pengguna untuk Tone Adaptation."""
        msg = message.lower().strip()
        
        # 1. Marah / Kesal
        if re.search(r'(rusak|gagal|error terus|jelek|bodoh|payah|capek|kesal)', msg) or msg.count('!') >= 2:
            return "marah/kesal"
            
        # 2. Terburu-buru
        if re.search(r'(cepat|sekarang|buru|urgent|darurat|langsung saja)', msg) or (len(msg) < 15 and msg.endswith('!')):
            return "terburu-buru"
            
        # 3. Bingung / Pusing / Putus Asa
        if re.search(r'(bingung|pusing|gak ngerti|tidak paham|tolong banget|help|nyerah|susah)', msg) or msg.count('?') >= 2:
            return "bingung/sedih"
            
        # 4. Santai / Kasual
        if re.search(r'(halo|bro|dong|sih|hehe|wkwk|haha|keren|mantap|oke|sip)', msg):
            return "santai"
            
        return "netral"
    
    def add_rule(self, column: str, steps: list, description: str = ""):
        """Tambah aturan baru (untuk ekspansi Lego)."""
        self.rules[column] = {
            "steps": steps,
            "description": description
        }