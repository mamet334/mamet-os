"""
MAMET OS - Usage Tracker
==========================
Mencatat setiap panggilan LLM/Embedding untuk budget control.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class UsageTracker:
    """Tracker pemakaian AI provider."""
    
    def __init__(self, email: str = "default"):
        self.email = email
        base_dir = os.path.join(os.path.expanduser("~"), ".mamet", email)
        os.makedirs(base_dir, exist_ok=True)
        self.db_path = os.path.join(base_dir, "memory.db")
        self._init_database()
    
    def _init_database(self):
        """Buat tabel usage_logs dan budget_caps jika belum ada."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model TEXT,
                    tokens_in INTEGER DEFAULT 0,
                    tokens_out INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    operation TEXT DEFAULT 'chat',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budget_caps (
                    provider TEXT PRIMARY KEY,
                    monthly_cap REAL DEFAULT 100000,
                    is_active INTEGER DEFAULT 1
                )
            """)
            # Insert default caps jika belum ada
            for provider in ["openrouter", "openai", "grok", "gemini"]:
                conn.execute(
                    "INSERT OR IGNORE INTO budget_caps (provider, monthly_cap) VALUES (?, ?)",
                    (provider, 100000)
                )
            conn.commit()
    
    def log_usage(
        self,
        provider: str,
        model: str = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost: float = 0.0,
        operation: str = "chat"
    ):
        """Catat pemakaian."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO usage_logs (provider, model, tokens_in, tokens_out, cost, operation) VALUES (?, ?, ?, ?, ?, ?)",
                (provider, model, tokens_in, tokens_out, cost, operation)
            )
            conn.commit()
    
    def get_usage(
        self,
        provider: str = None,
        period: str = "monthly"
    ) -> Dict:
        """
        Dapatkan statistik pemakaian.
        
        Args:
            provider: Nama provider (None = semua)
            period: "daily", "weekly", "monthly"
            
        Returns:
            Dict dengan total cost dan detail
        """
        now = datetime.now()
        
        if period == "daily":
            since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            since = now - timedelta(days=7)
        else:  # monthly
            since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        query = """
            SELECT provider, SUM(cost) as total_cost, SUM(tokens_in) as total_tokens_in, 
                   SUM(tokens_out) as total_tokens_out, COUNT(*) as request_count
            FROM usage_logs
            WHERE timestamp >= ?
        """
        params = [since]
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        query += " GROUP BY provider"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            
            result = {
                "period": period,
                "since": since.isoformat(),
                "providers": {}
            }
            
            total_cost = 0
            for row in rows:
                result["providers"][row["provider"]] = {
                    "total_cost": round(row["total_cost"], 2),
                    "total_tokens_in": row["total_tokens_in"],
                    "total_tokens_out": row["total_tokens_out"],
                    "request_count": row["request_count"]
                }
                total_cost += row["total_cost"]
            
            result["total_cost"] = round(total_cost, 2)
            return result
    
    def get_budget_status(self, provider: str = None) -> Dict:
        """
        Cek status budget vs cap.
        
        Returns:
            Dict dengan status per provider
        """
        monthly_usage = self.get_usage(period="monthly")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if provider:
                rows = conn.execute(
                    "SELECT provider, monthly_cap FROM budget_caps WHERE provider = ?",
                    (provider,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT provider, monthly_cap FROM budget_caps"
                ).fetchall()
            
            result = {"providers": {}, "total_budget_used": 0, "total_budget_cap": 0}
            
            for row in rows:
                prov = row["provider"]
                cap = row["monthly_cap"]
                used = monthly_usage.get("providers", {}).get(prov, {}).get("total_cost", 0)
                percentage = (used / cap * 100) if cap > 0 else 0
                
                status = "ok"
                if percentage >= 100:
                    status = "exceeded"
                elif percentage >= 80:
                    status = "warning"
                elif percentage >= 50:
                    status = "half"
                
                result["providers"][prov] = {
                    "monthly_cap": cap,
                    "used": round(used, 2),
                    "remaining": round(cap - used, 2),
                    "percentage": round(percentage, 1),
                    "status": status
                }
                
                result["total_budget_used"] += used
                result["total_budget_cap"] += cap
            
            result["total_budget_used"] = round(result["total_budget_used"], 2)
            
            return result
    
    def set_budget_cap(self, provider: str, monthly_cap: float):
        """Set budget cap untuk provider."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO budget_caps (provider, monthly_cap, is_active) VALUES (?, ?, 1)",
                (provider, monthly_cap)
            )
            conn.commit()
    
    def check_budget_available(self, provider: str) -> bool:
        """Cek apakah budget masih tersedia."""
        status = self.get_budget_status(provider=provider)
        prov_status = status.get("providers", {}).get(provider, {})
        return prov_status.get("status") != "exceeded"