"""
MAMET OS - LLM Provider Router
===============================
Abstraction layer untuk multi-provider AI dengan budget control.
"""

import os
import sqlite3
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Interface standar untuk semua provider AI."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict], model: str = None) -> str:
        pass
    
    @abstractmethod
    def embed(self, texts: List[str], model: str = None) -> List[List[float]]:
        pass


class ProviderRouter:
    """Router untuk mengelola multiple AI providers dengan budget control."""
    
    def __init__(self, email: str = "default"):
        self.email = email
        self.providers: Dict[str, AIProvider] = {}
        self._init_database()
        self._load_providers()
    
    def _init_database(self):
        """Inisialisasi tabel providers di SQLite."""
        base_dir = os.path.join(os.path.expanduser("~"), ".mamet", self.email)
        os.makedirs(base_dir, exist_ok=True)
        
        self.db_path = os.path.join(base_dir, "memory.db")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS providers (
                    name TEXT PRIMARY KEY,
                    api_key_encrypted TEXT,
                    is_active INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 1
                )
            """)
            conn.commit()
    
    def _load_providers(self):
        """Muat provider dari database."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT name, api_key_encrypted, is_active, priority FROM providers ORDER BY priority"
            ).fetchall()
            
            for row in rows:
                name, key_encrypted, is_active, priority = row
                if is_active and key_encrypted:
                    self._init_provider(name, key_encrypted)
    
    def _init_provider(self, name: str, api_key: str):
        """Inisialisasi provider berdasarkan nama."""
        try:
            if name == "openrouter":
                from ai.providers.openrouter_provider import OpenRouterProvider
                self.providers[name] = OpenRouterProvider(api_key)
                print(f"[ROUTER] [OK] Provider '{name}' siap")
        except Exception as e:
            print(f"[ROUTER] [ERROR] Gagal inisialisasi provider '{name}': {e}")
    
    def add_provider(self, name: str, api_key: str, priority: int = 1):
        """Tambah provider baru."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO providers (name, api_key_encrypted, is_active, priority) VALUES (?, ?, 1, ?)",
                (name, api_key, priority)
            )
            conn.commit()
        
        self._init_provider(name, api_key)
    
    def get_active_provider(self) -> Optional[AIProvider]:
        """Dapatkan provider aktif pertama."""
        for provider in self.providers.values():
            return provider
        return None
    
    def chat(self, messages: List[Dict], model: str = None) -> str:
        """Kirim chat ke provider aktif dengan fallback otomatis dan budget checking."""
        provider = self.get_active_provider()
        if provider is None:
            raise Exception("Tidak ada AI provider yang aktif.")
        
        # Cek budget
        tracker = self._get_tracker()
        if not tracker.check_budget_available(provider.name):
            raise Exception(f"Budget untuk {provider.name} telah habis bulan ini.")
        
        # Hitung token kasar (4 chars ≈ 1 token)
        input_text = " ".join([m.get("content", "") for m in messages])
        tokens_in = max(1, len(input_text) // 4)
        
        try:
            response = provider.chat(messages, model)
            tokens_out = max(1, len(response) // 4)
            
            # Hitung biaya (estimasi kasar)
            cost = self._estimate_cost(provider.name, model, tokens_in, tokens_out)
            
            # Catat pemakaian
            tracker.log_usage(
                provider=provider.name,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost=cost,
                operation="chat"
            )
            
            return response
        except Exception as e:
            raise e
    
    def embed(self, texts: List[str], model: str = None) -> List[List[float]]:
        """Embed teks dengan provider aktif + budget checking."""
        provider = self.get_active_provider()
        if provider is None:
            return [[0.0] * 768 for _ in texts]
        
        # Cek budget
        tracker = self._get_tracker()
        if not tracker.check_budget_available(provider.name):
            print(f"[ROUTER] Budget untuk {provider.name} habis. Menggunakan zeros.")
            return [[0.0] * 768 for _ in texts]
        
        # Hitung token kasar
        all_text = " ".join(texts)
        tokens_in = max(1, len(all_text) // 4)
        
        try:
            result = provider.embed(texts, model)
            
            cost = self._estimate_cost(provider.name, model, tokens_in, 0)
            
            tracker.log_usage(
                provider=provider.name,
                model=model,
                tokens_in=tokens_in,
                tokens_out=0,
                cost=cost,
                operation="embed"
            )
            
            return result
        except Exception as e:
            print(f"[ROUTER] Embed error: {e}")
            return [[0.0] * 768 for _ in texts]
    
    def _get_tracker(self):
        """Dapatkan UsageTracker instance."""
        from ai.usage_tracker import UsageTracker
        return UsageTracker(email=self.email)
    
    def _estimate_cost(self, provider: str, model: str, tokens_in: int, tokens_out: int) -> float:
        """Estimasi biaya berdasarkan pricing kasar (dalam Rupiah per 1M tokens)."""
        pricing = {
            "openrouter": {
                "mistralai/mistral-7b-instruct": (500, 500),
                "openai/gpt-4o": (10000, 30000),
                "nomic-embed-text": (100, 0)
            },
            "openai": {
                "gpt-4o": (10000, 30000),
                "gpt-3.5-turbo": (2000, 6000)
            }
        }
        
        default_pricing = (1000, 2000)
        
        prov_pricing = pricing.get(provider, {})
        model_pricing = prov_pricing.get(model, default_pricing) if model else default_pricing
        
        input_cost = (tokens_in / 1_000_000) * model_pricing[0]
        output_cost = (tokens_out / 1_000_000) * model_pricing[1]
        
        return round(input_cost + output_cost, 6)
    
    def get_budget_status(self) -> Dict:
        """Dapatkan status budget semua provider."""
        tracker = self._get_tracker()
        return tracker.get_budget_status()
    
    def set_budget_cap(self, provider: str, monthly_cap: float):
        """Set budget cap."""
        tracker = self._get_tracker()
        tracker.set_budget_cap(provider, monthly_cap)