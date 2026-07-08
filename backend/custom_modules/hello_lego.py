from lego_modules.base_lego import LegoModule
from typing import Dict, Any

class HelloLego(LegoModule):
    @property
    def name(self) -> str:
        return "HelloLego"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    def can_handle(self, input_data: Dict[str, Any]) -> bool:
        return input_data.get("intent") == "hello_lego"
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": "Hello dari Custom Module Lego!"}
