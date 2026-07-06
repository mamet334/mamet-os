"""
MAMET OS - Decision Engine
============================
Mengambil keputusan secara SIMBOLIK berdasarkan evidence.
"""

class DecisionEngine:
    """Mesin pengambil keputusan simbolik."""
    
    def __init__(self):
        self.thresholds = {
            "direct_reply": 0.8,
            "need_llm": 0.5,
            "need_agent": 0.3,
            "ask_clarify": 0.1
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
        # KOLOM 3 (Engineer) - SELALU butuh persetujuan untuk perubahan
        # -----------------------------------------------------------------
        if column == "kolom3":
            engineer_data = None
            for item in evidence.get("items", []):
                if item.get("source") == "engineer":
                    engineer_data = item.get("data", {})
                    break
            
            if engineer_data:
                action = engineer_data.get("action", "direct_reply")
                
                if action == "need_approval":
                    decision["action"] = "need_approval"
                    decision["message"] = engineer_data.get("response", "Membutuhkan persetujuan Anda.")
                    decision["approval_details"] = engineer_data.get("approval_details", {})
                    decision["actions_taken"] = ["engineer_analyzed", "needs_approval"]
                else:
                    decision["action"] = "direct_reply"
                    decision["message"] = engineer_data.get("response", "")
                    decision["actions_taken"] = ["engineer_responded"]
            elif intent == "command":
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
                decision["message"] = evidence.get("direct_answer", "Engineer MAMET OS siap membantu.")
                decision["actions_taken"] = ["analyzed_request"]
        
        # -----------------------------------------------------------------
        # KOLOM 1 (Pencarian Cepat) - RAG-focused
        # -----------------------------------------------------------------
        elif column == "kolom1":
            # Cek apakah RAG memberikan hasil
            rag_results = []
            for item in evidence.get("items", []):
                if item.get("source") == "rag":
                    rag_results = item.get("results", [])
                    break
            
            if rag_results:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["searched_rag", "found_results"]
                decision["rag_results"] = rag_results
            elif confidence > self.thresholds["direct_reply"]:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["found_in_cache"]
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
                decision["agent"] = "web_search"
                decision["actions_taken"] = ["no_local_knowledge", "escalating_to_agent"]
            else:
                decision["action"] = "direct_reply"
                decision["actions_taken"] = ["low_confidence"]
        
        return decision