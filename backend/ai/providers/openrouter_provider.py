"""
MAMET OS - OpenRouter Provider
===============================
Implementasi AIProvider untuk OpenRouter API.
"""

import requests
from typing import List, Dict
from ai.provider_router import AIProvider

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_EMBED_URL = "https://openrouter.ai/api/v1/embeddings"


class OpenRouterProvider(AIProvider):
    """Provider untuk OpenRouter API."""
    
    @property
    def name(self) -> str:
        return "openrouter"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def chat(self, messages: List[Dict], model: str = None) -> str:
        # Model default yang gratis
        model = model or "openai/gpt-4o-mini"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "MAMET OS"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            OPENROUTER_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def embed(self, texts: List[str], model: str = None) -> List[List[float]]:
        model = model or "nomic-embed-text"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "MAMET OS"
        }
        
        payload = {
            "model": model,
            "input": texts
        }
        
        response = requests.post(
            OPENROUTER_EMBED_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return [item["embedding"] for item in data.get("data", [])]