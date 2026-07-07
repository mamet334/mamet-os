"""
MAMET OS - Schema Mapper
========================
Mengekstrak skema (tabel, kolom, relasi) dari database.
"""

import sqlite3
import csv
import json
from typing import Dict, Any, List

class SchemaMapper:
    """Pemeta skema database menjadi format JSON standar."""
    
    @staticmethod
    def extract_schema(file_path: str, db_type: str) -> Dict[str, Any]:
        """Ekstrak skema dan sampel data."""
        if db_type == 'sqlite':
            return SchemaMapper._extract_sqlite(file_path)
        elif db_type == 'csv':
            return SchemaMapper._extract_csv(file_path)
        elif db_type == 'json':
            return SchemaMapper._extract_json(file_path)
        else:
            raise ValueError(f"Tipe database tidak didukung: {db_type}")

    @staticmethod
    def _extract_sqlite(db_path: str) -> Dict[str, Any]:
        schema = {"type": "sqlite", "tables": {}}
        
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Ambil daftar tabel
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row['name'] for row in cursor.fetchall() if row['name'] != 'sqlite_sequence']
                
                for table in tables:
                    schema["tables"][table] = {"columns": [], "sample_data": []}
                    
                    # Ambil info kolom
                    cursor.execute(f"PRAGMA table_info({table});")
                    columns = cursor.fetchall()
                    for col in columns:
                        schema["tables"][table]["columns"].append({
                            "name": col['name'],
                            "type": col['type'],
                            "is_pk": bool(col['pk'])
                        })
                        
                    # Ambil 5 sampel data
                    try:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
                        samples = cursor.fetchall()
                        schema["tables"][table]["sample_data"] = [dict(row) for row in samples]
                    except Exception as e:
                        print(f"[SCHEMA] Gagal ambil sampel {table}: {e}")
                        
        except Exception as e:
            schema["error"] = str(e)
            
        return schema

    @staticmethod
    def _extract_csv(file_path: str) -> Dict[str, Any]:
        schema = {"type": "csv", "tables": {"default": {"columns": [], "sample_data": []}}}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if reader.fieldnames:
                    schema["tables"]["default"]["columns"] = [{"name": name, "type": "string"} for name in reader.fieldnames]
                
                samples = []
                for i, row in enumerate(reader):
                    if i >= 5: break
                    samples.append(row)
                
                schema["tables"]["default"]["sample_data"] = samples
        except Exception as e:
            schema["error"] = str(e)
            
        return schema

    @staticmethod
    def _extract_json(file_path: str) -> Dict[str, Any]:
        schema = {"type": "json", "tables": {"default": {"columns": [], "sample_data": []}}}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict):
                        schema["tables"]["default"]["columns"] = [{"name": k, "type": type(v).__name__} for k, v in first_item.items()]
                        schema["tables"]["default"]["sample_data"] = data[:5]
        except Exception as e:
            schema["error"] = str(e)
            
        return schema
