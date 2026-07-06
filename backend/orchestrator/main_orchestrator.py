"""
MAMET OS - Main Orchestrator (KERNEL)
======================================
Jantung MAMET OS. Loop utama yang menerima input,
merencanakan, mengumpulkan bukti, memutuskan, dan merespons.

Filosofi:
- Simpel seperti kernel Linux
- Tidak bergantung LLM untuk planning/decision
- Semua modul lain dipasang ke orchestrator ini

Analog: Kernel pada sistem operasi.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Sub-modul orchestrator
# ---------------------------------------------------------------------------
from .planning_engine import PlanningEngine
from .evidence_collector import EvidenceCollector
from .decision_engine import DecisionEngine

# ---------------------------------------------------------------------------
# Kernel Class
# ---------------------------------------------------------------------------

class MainOrchestrator:
    """
    Kernel MAMET OS.
    
    Menerima input dari user melalui salah satu kolom,
    lalu menjalankan siklus:
        PLAN → COLLECT → DECIDE → RESPOND
    """
    
    def __init__(self):
        """Inisialisasi kernel dan sub-modul."""
        self.planning_engine = PlanningEngine()
        self.evidence_collector = EvidenceCollector()
        self.decision_engine = DecisionEngine()
        self.boot_time = None
        self.is_running = False
        
    async def boot(self):
        """
        Booting kernel.
        Dipanggil sekali saat server start.
        """
        self.boot_time = datetime.now()
        self.is_running = True
        
        # Inisialisasi sub-sistem
        await self.planning_engine.initialize()
        await self.evidence_collector.initialize()
        await self.decision_engine.initialize()
        
        print(f"[KERNEL] Booted at {self.boot_time}")
        print(f"[KERNEL] Planning Engine: READY")
        print(f"[KERNEL] Evidence Collector: READY")
        print(f"[KERNEL] Decision Engine: READY")
        
    async def shutdown(self):
        """
        Shutdown kernel.
        Dipanggil sekali saat server stop.
        """
        self.is_running = False
        print(f"[KERNEL] Shutdown. Uptime: {datetime.now() - self.boot_time}")
        
    async def process(
        self,
        user_id: str,
        column: str,
        message: str,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Siklus utama MAMET OS: PLAN → COLLECT → DECIDE → RESPOND.
        
        Args:
            user_id: Email user yang login
            column: Kolom chat ("kolom1", "kolom2", "kolom3")
            message: Isi pesan user
            api_key: OpenRouter API key user (opsional)
            
        Returns:
            Dict berisi response, sources, actions, approval
        """
        if not self.is_running:
            return self._error_response("Kernel belum siap. Silakan tunggu...")
        
        print(f"\n[KERNEL] ========== NEW REQUEST ==========")
        print(f"[KERNEL] User: {user_id}")
        print(f"[KERNEL] Kolom: {column}")
        print(f"[KERNEL] Message: {message[:100]}...")
        
        # -----------------------------------------------------------------
        # FASE 1: PLAN
        # Planning Engine membuat rencana tindakan secara SIMBOLIK.
        # TIDAK menggunakan LLM.
        # -----------------------------------------------------------------
        plan = await self.planning_engine.create_plan(
            user_id=user_id,
            column=column,
            message=message
        )
        print(f"[KERNEL] Plan: {plan['steps']}")
        
        # -----------------------------------------------------------------
        # FASE 2: COLLECT
        # Evidence Collector mengumpulkan bukti sesuai rencana.
        # Sumber: User Memory, RAG, Cache, atau sinyal untuk agen.
        # -----------------------------------------------------------------
        evidence = await self.evidence_collector.collect(
            user_id=user_id,
            column=column,
            plan=plan,
            api_key=api_key
        )
        print(f"[KERNEL] Evidence collected: {len(evidence.get('items', []))} items")
        print(f"[KERNEL] Confidence: {evidence.get('confidence', 0)}")
        
        # -----------------------------------------------------------------
        # FASE 3: DECIDE
        # Decision Engine memutuskan tindakan selanjutnya.
        # Juga SIMBOLIK - aturan if-then, bukan LLM.
        # -----------------------------------------------------------------
        decision = await self.decision_engine.decide(
            user_id=user_id,
            column=column,
            plan=plan,
            evidence=evidence,
            api_key=api_key
        )
        print(f"[KERNEL] Decision: {decision['action']}")
        
        # -----------------------------------------------------------------
        # FASE 4: RESPOND
        # Membangun response berdasarkan keputusan.
        # LLM hanya dipanggil JIKA Decision Engine memutuskan perlu.
        # -----------------------------------------------------------------
        response = await self._build_response(
            decision=decision,
            evidence=evidence,
            api_key=api_key
        )
        print(f"[KERNEL] Response: {response['response'][:100]}...")
        
        return response
    
    async def _build_response(
        self,
        decision: Dict[str, Any],
        evidence: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Membangun response berdasarkan keputusan Decision Engine.
        
        Keputusan yang mungkin:
        - "direct_reply": Jawab langsung dari evidence, TANPA LLM
        - "need_llm": Panggil LLM untuk generasi teks
        - "need_agent": Panggil agen tertentu
        - "need_approval": Minta persetujuan user (untuk Engineer)
        - "error": Response error
        """
        action = decision.get("action", "error")
        
        if action == "direct_reply":
            return {
                "response": evidence.get("direct_answer", "Saya tidak menemukan jawaban."),
                "sources": evidence.get("sources", []),
                "actions_taken": decision.get("actions_taken", []),
                "requires_approval": False,
                "approval_details": {}
            }
        
        elif action == "need_llm":
            # Akan diimplementasikan saat LLM tersedia
            return {
                "response": "[LLM] Fitur ini akan tersedia setelah integrasi OpenRouter.",
                "sources": evidence.get("sources", []),
                "actions_taken": decision.get("actions_taken", []),
                "requires_approval": False,
                "approval_details": {}
            }
        
        elif action == "need_agent":
            # Akan diimplementasikan saat agen tersedia
            return {
                "response": f"[AGENT] Agen '{decision.get('agent')}' akan dipanggil.",
                "sources": evidence.get("sources", []),
                "actions_taken": decision.get("actions_taken", []),
                "requires_approval": False,
                "approval_details": {}
            }
        
        elif action == "need_approval":
            return {
                "response": decision.get("message", "Membutuhkan persetujuan Anda."),
                "sources": [],
                "actions_taken": decision.get("actions_taken", []),
                "requires_approval": True,
                "approval_details": decision.get("approval_details", {})
            }
        
        else:
            return self._error_response("Tindakan tidak dikenali.")
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Response standar untuk error."""
        return {
            "response": f"❌ {message}",
            "sources": [],
            "actions_taken": [],
            "requires_approval": False,
            "approval_details": {}
        }