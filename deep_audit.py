import sys
import os
import asyncio
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "backend"))

async def deep_audit():
    print("="*60)
    print("🛠️  DEEP AUDIT: MAMET OS KERNEL & COMPONENTS  🛠️")
    print("="*60)
    
    issues = []
    
    # 1. PLANNER AUDIT
    print("\n[1] Memeriksa Planning Engine...")
    try:
        from orchestrator.planning_engine import PlanningEngine
        planner = PlanningEngine()
        await planner.initialize()
        plan1 = await planner.create_plan("test", "kolom1", "Apa itu?")
        plan2 = await planner.create_plan("test", "kolom2", "Namaku slamet.")
        plan3 = await planner.create_plan("test", "kolom3", "list folder")
        
        if "check_rag" in plan1['steps'] and "check_user_memory" in plan2['steps'] and "check_engineer" in plan3['steps']:
            print("  ✅ Planning Engine: Routing dinamis berfungsi sempurna.")
        else:
            issues.append("Planning Engine: Langkah yang dihasilkan tidak sesuai.")
    except Exception as e:
        issues.append(f"Planning Engine Error: {e}")

    # 2. COLLECTOR AUDIT
    print("\n[2] Memeriksa Evidence Collector & Dependencies...")
    try:
        from orchestrator.evidence_collector import EvidenceCollector
        collector = EvidenceCollector()
        await collector.initialize()
        
        # Test fake plan
        plan = {"steps": ["check_user_memory"]}
        ev = await collector.collect("test", "kolom2", plan)
        if "items" in ev:
            print("  ✅ Evidence Collector: Dapat mengeksekusi step dengan aman.")
        else:
            issues.append("Evidence Collector: Gagal memproduksi items.")
    except Exception as e:
        issues.append(f"Evidence Collector Error: {e}")

    # 3. DECISION ENGINE AUDIT
    print("\n[3] Memeriksa Decision Engine...")
    try:
        from orchestrator.decision_engine import DecisionEngine
        decision = DecisionEngine()
        await decision.initialize()
        
        ev_mock = {"items": [{"source": "user_memory", "data": {"context": "Halo"}}], "confidence": 0.6}
        dec = await decision.decide("test", "kolom2", {"steps":[]}, ev_mock)
        if "action" in dec:
            print(f"  ✅ Decision Engine: Keputusan diambil -> {dec['action']}")
        else:
            issues.append("Decision Engine: Tidak mengembalikan action.")
    except Exception as e:
        issues.append(f"Decision Engine Error: {e}")

    # 4. AGENTS AUDIT
    print("\n[4] Memeriksa Ekosistem Sub-Agent (Deep Execution)...")
    try:
        from agents.file_analysis_agent import FileAnalysisAgent
        from agents.research_agent import ResearchAgent
        from agents.web_search_agent import WebSearchAgent
        from agents.database_explorer_agent import DatabaseExplorerAgent
        
        # Mock Provider
        class MockProvider:
            def chat(self, messages): return "Mock LLM Response"
        
        provider = MockProvider()
        fa = FileAnalysisAgent(provider=provider, user_id="test")
        ra = ResearchAgent(provider=provider, user_id="test")
        ws = WebSearchAgent(provider=provider, user_id="test")
        db = DatabaseExplorerAgent(provider=provider, user_id="test")
        
        print(f"  ✅ Seluruh agen berhasil diinisialisasi: {fa.name}, {ra.name}, {ws.name}, {db.name}")
        
        # Test eksekusi Database Agent tanpa file_path
        res_db_empty = await db.process("tolong analisa", {})
        if "membutuhkan *path* file" in res_db_empty:
             print("  ✅ Database Agent: Berhasil memblokir eksekusi tanpa file_path.")
        else:
             issues.append("Database Agent: Tidak menangani ketiadaan file_path dengan benar.")
             
        # Test eksekusi Database Agent dengan file_path palsu
        res_db_fake = await db.process("analisa", {"file_path": "fake.csv"})
        if "tidak dikenali" in res_db_fake:
             print("  ✅ Database Agent: Detektor database berfungsi menolak file palsu.")
        else:
             issues.append("Database Agent: Gagal menangani file palsu.")
             
    except Exception as e:
        issues.append(f"Agents Error: {e}")

    # 5. DATABASE DETECTOR AUDIT
    print("\n[5] Memeriksa Database Detector & Schema Mapper (Deep Execution)...")
    try:
        from database_detector.detector import DatabaseDetector
        from database_detector.schema_mapper import SchemaMapper
        
        dd = DatabaseDetector()
        sm = SchemaMapper()
        
        # Buat dummy CSV
        dummy_csv = project_root / "audit_dummy.csv"
        dummy_csv.write_text("id,name,age\n1,Budi,20")
        
        db_type = dd.detect_type(str(dummy_csv))
        if db_type == "csv":
            schema = sm.extract_schema(str(dummy_csv), db_type)
            if "name" in str(schema):
                print("  ✅ Database Detector: Berhasil membaca struktur CSV dummy.")
            else:
                issues.append("Database Detector: Gagal memetakan skema.")
        else:
            issues.append("Database Detector: Gagal mendeteksi CSV.")
            
        dummy_csv.unlink()
    except Exception as e:
        issues.append(f"Database Detector Error: {e}")

    # 6. LEGO REGISTRY AUDIT
    print("\n[6] Memeriksa Arsitektur Lego Modules...")
    try:
        from lego_modules.lego_registry import LegoRegistry
        registry = LegoRegistry()
        print("  ✅ Lego Registry: Berhasil di-load.")
    except Exception as e:
        issues.append(f"Lego Registry Error: {e}")
        
    print("\n" + "="*60)
    if not issues:
        print("🎉 STATUS AUDIT: 100% SEHAT. TIDAK DITEMUKAN MASALAH.")
    else:
        print("⚠️ DITEMUKAN MASALAH PADA SISTEM:")
        for issue in issues:
            print(f"  - {issue}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(deep_audit())
