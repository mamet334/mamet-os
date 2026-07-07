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
        # KOLOM 3 (Engineer)
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
        # KOLOM 1 (Pencarian Cepat)
        # -----------------------------------------------------------------
        elif column == "kolom1":
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
        # KOLOM 2 (Asisten Pribadi) - MEMORI + RAG
        # -----------------------------------------------------------------
        else:
            # Cek apakah ada Sub-Agent
            sub_agent_response = None
            for item in evidence.get("items", []):
                if item.get("source") == "sub_agent":
                    sub_agent_response = item.get("response")
                    break
                    
            if sub_agent_response:
                decision["action"] = "direct_reply"
                decision["message"] = sub_agent_response
                decision["actions_taken"] = ["sub_agent_responded"]
                return decision
                
            # Cek apakah ada hasil dari Lego Module
            lego_data = None
            lego_module = None
            for item in evidence.get("items", []):
                if item.get("source") == "lego_module":
                    lego_data = item.get("data")
                    lego_module = item.get("module")
                    break
                    
            if lego_data:
                decision["action"] = "direct_reply"
                decision["message"] = str(lego_data)
                decision["actions_taken"] = [f"lego_module_executed:{lego_module}"]
                return decision
                
            # Cek apakah ada fakta dari User Memory
            memory_context = None
            memory_items = []
            for item in evidence.get("items", []):
                if item.get("source") == "user_memory":
                    memory_context = item.get("facts_context", "")
                    memory_items.append(item)
                    break
            
            # Cek hasil RAG
            rag_results = []
            for item in evidence.get("items", []):
                if item.get("source") == "rag":
                    rag_results = item.get("results", [])
                    break
            
            # Gabungkan konteks
            combined_context = []
            if memory_context:
                combined_context.append(memory_context)
            if rag_results:
                rag_text = "\n".join([r["text"][:200] for r in rag_results[:3]])
                combined_context.append(f"Informasi relevan:\n{rag_text}")
            
            if combined_context:
                decision["action"] = "need_llm"
                decision["actions_taken"] = ["found_memory", "found_rag"]
                decision["combined_context"] = "\n\n".join(combined_context)
            elif confidence > self.thresholds["need_agent"]:
                decision["action"] = "need_llm"
                decision["actions_taken"] = ["partial_match", "need_llm_generation"]
            else:
                # Confidence rendah tapi tetap butuh LLM untuk respons personal
                decision["action"] = "need_llm"
                decision["actions_taken"] = ["low_confidence", "need_llm_generation"]
        
        return decision