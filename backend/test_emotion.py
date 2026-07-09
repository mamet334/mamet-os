import asyncio
import sys
import os
sys.path.append(os.getcwd())
from orchestrator.planning_engine import PlanningEngine

async def test():
    p = PlanningEngine()
    
    plan1 = await p.create_plan('user', 'kolom2', 'Aduh saya bingung sekali tolong bantu!')
    print(f"Emosi 1: {plan1['emotion']}")
    print(f"Multi-step 1: {plan1['is_multi_step']}")
    
    plan2 = await p.create_plan('user', 'kolom2', 'Tolong cepat analisis file ini lalu buatkan laporannya, dan rangkum semuanya segera!')
    print(f"Emosi 2: {plan2['emotion']}")
    print(f"Multi-step 2: {plan2['is_multi_step']}")
    print(f"Sub-tasks 2: {plan2['sub_tasks']}")

asyncio.run(test())
