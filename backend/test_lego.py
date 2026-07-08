import asyncio
from orchestrator.evidence_collector import EvidenceCollector

async def test():
    print("Inisialisasi Collector...")
    collector = EvidenceCollector()
    print("Modul yang terdaftar:")
    for mod in collector.lego_registry.get_modules():
        print("-", mod)

if __name__ == "__main__":
    asyncio.run(test())
