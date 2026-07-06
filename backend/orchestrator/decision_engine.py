"""
MAMET OS - Decision Engine
============================
Mengambil keputusan secara SIMBOLIK berdasarkan evidence.

Filosofi:
- Pohon keputusan (decision tree), bukan LLM
- Deterministik dan dapat di-debug
- Confidence threshold menentukan tindakan
"""

class DecisionEngine:
    """Mesin pengambil keputusan simbolik."""
    
    def __init__(self):
        self.thresholds = {
            "direct_reply": 0.8,  # Confidence > 0.8 → jawab langsung
            "need_llm": 0.5,      # Confidence 0.5-0.8 → butuh LLM
            "need_agent": 0.3,    # Confidence 0.3-0.5 → butuh agen
            "ask_clarify": 0.1    # Confidence < 0.1 → minta klarifikasi
        }
    
    async def initialize(self):
        """Inisialisasi decision engine."""
        print(f"  [DECISION] Thresholds: {self.thresholds}")
    
    async def decide(
        self,
        user_id: str,
        column: str,
        plan: dict,
        evidence: dict,
        api_key: str = None
    ) -> dict:
        """
        Putuskan tindakan selanjutnya.
        
        Args:
            user_id: Email user
            column: Kolom chat
            plan: Rencana
            evidence: Evidence yang dikumpulkan
            api_key: OpenRouter API key
            
        Returns:
            Dict berisi keputusan
        """
        confidence = evidence.get("confidence", 0)
        intent = plan.get("intent", "chat")
        
        decision = {
            "action": None,
            "agent": None,
            "message": None,
            "actions_taken": [],
            "approval_details": {}
        }
        
        # -----------------------------------------------------------------
        # KOLOM 3 (Engineer) - SELALU butuh persetujuan
        # -----------------------------------------------------------------
        if column == "kolom3":
            # Engineer selalu minta persetujuan untuk perubahan
            if intent == "command":
                decision["action"] = "need_approval"
                decision["message"] = "Saya akan membuat perubahan berikut. Silakan tinjau dan setujui."
                decision["approval_details"] = {
                    "type": "code_change",
                    "plan": plan,
                    "evidence": evidence
                }
                decision["actions_taken"] = ["analyzed_request", "prepared_plan"]
            else:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["analyzed_request"]
        
        # -----------------------------------------------------------------
        # KOLOM 1 (Pencarian Cepat) - RAG-focused
        # -----------------------------------------------------------------
        elif column == "kolom1":
            if confidence > self.thresholds["direct_reply"]:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["searched_rag", "found_results"]
            elif confidence > self.thresholds["need_llm"]:
                decision["action"] = "need_llm"
                decision["actions_taken"] = ["searched_rag", "need_better_answer"]
            else:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["no_results_found"]
        
        # -----------------------------------------------------------------
        # KOLOM 2 (Asisten Pribadi) - Memori + Agen
        # -----------------------------------------------------------------
        else:
            if confidence > self.thresholds["direct_reply"]:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["found_in_memory_or_rag"]
            elif confidence > self.thresholds["need_llm"]:
                decision["action"] = "need_llm"
                decision["actions_taken"] = ["partial_match", "need_llm_generation"]
            elif confidence > self.thresholds["need_agent"]:
                decision["action"] = "need_agent"
                decision["agent"] = "web_search"  # Default agent
                decision["actions_taken"] = ["no_local_knowledge", "escalating_to_agent"]
            else:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["low_confidence"]
        
        return decision