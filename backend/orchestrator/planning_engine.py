"""
MAMET OS - Planning Engine
============================
Membuat rencana tindakan secara SIMBOLIK (tanpa LLM).

Filosofi:
- Aturan if-then yang deterministik
- Cepat, tidak ada biaya API
- Dapat diperluas dengan aturan baru
"""

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
                "steps": ["check_user_memory", "check_rag", "decide_if_need_agent", "respond"],
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
        
        Args:
            user_id: Email user
            column: Kolom chat
            message: Pesan user
            
        Returns:
            Dict berisi langkah-langkah rencana
        """
        # Ambil aturan default untuk kolom ini
        rule = self.rules.get(column, self.rules["kolom2"])
        
        # Deteksi intent sederhana dari pesan
        intent = self._detect_intent(message)
        
        plan = {
            "column": column,
            "intent": intent,
            "steps": rule["steps"],
            "original_message": message,
            "created_at": None  # Akan diisi timestamp saat eksekusi
        }
        
        # Tambahkan langkah spesifik berdasarkan intent
        if intent == "search":
            plan["steps"].insert(0, "parse_search_query")
        elif intent == "command":
            plan["steps"].insert(0, "parse_command")
        elif intent == "question":
            plan["steps"].insert(0, "analyze_question_type")
        
        return plan
    
    def _detect_intent(self, message: str) -> str:
        """
        Deteksi intent sederhana dari pesan.
        SIMBOLIK - tidak pakai LLM.
        """
        message_lower = message.lower().strip()
        
        # Command patterns
        if any(message_lower.startswith(word) for word in ["buat", "bikin", "tambah", "hapus", "edit", "ubah"]):
            return "command"
        
        # Search patterns
        if any(word in message_lower for word in ["cari", "temukan", "dimana", "siapa", "kapan"]):
            return "search"
        
        # Question patterns
        if "?" in message_lower or any(message_lower.startswith(word) for word in ["apa", "bagaimana", "kenapa", "mengapa"]):
            return "question"
        
        # Default
        return "chat"
    
    def add_rule(self, column: str, steps: list, description: str = ""):
        """Tambah aturan baru (untuk ekspansi Lego)."""
        self.rules[column] = {
            "steps": steps,
            "description": description
        }