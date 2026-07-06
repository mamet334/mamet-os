"""
MAMET OS - Code Analyzer (Engineer)
=====================================
Menganalisis struktur proyek: dependensi, routing, komponen.
"""

from typing import Dict, List, Any
from pathlib import Path
import re


class CodeAnalyzer:
    """Menganalisis struktur dan dependensi codebase."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analisis keseluruhan proyek."""
        return {
            "backend": self._analyze_backend(),
            "frontend": self._analyze_frontend(),
            "summary": self._generate_summary()
        }
    
    def _analyze_backend(self) -> Dict[str, Any]:
        """Analisis bagian backend."""
        backend_path = self.root_path / "backend"
        if not backend_path.exists():
            return {"status": "not found"}
        
        python_files = list(backend_path.rglob("*.py"))
        
        # Deteksi framework
        imports = set()
        for f in python_files:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    for match in re.finditer(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE):
                        imports.add(match.group(1))
            except:
                pass
        
        # Deteksi route FastAPI
        routes = []
        for f in python_files:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    for match in re.finditer(r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)', content):
                        routes.append({"method": match.group(1).upper(), "path": match.group(2), "file": str(f.relative_to(self.root_path))})
            except:
                pass
        
        return {
            "total_python_files": len(python_files),
            "framework": "FastAPI" if "fastapi" in imports else "Unknown",
            "imports": sorted(list(imports))[:20],
            "routes": routes,
            "has_orchestrator": any("orchestrator" in str(f) for f in python_files),
            "has_engineer": any("engineer" in str(f) for f in python_files)
        }
    
    def _analyze_frontend(self) -> Dict[str, Any]:
        """Analisis bagian frontend."""
        frontend_path = self.root_path / "frontend"
        if not frontend_path.exists():
            return {"status": "not found"}
        
        tsx_files = list(frontend_path.rglob("*.tsx"))
        ts_files = list(frontend_path.rglob("*.ts"))
        
        # Deteksi framework
        has_next = (frontend_path / "next.config.ts").exists()
        has_react = any("react" in str(f).lower() for f in tsx_files)
        
        # Deteksi komponen
        components = []
        for f in tsx_files:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                    for match in re.finditer(r'(?:export\s+)?(?:default\s+)?function\s+(\w+)', content):
                        components.append({"name": match.group(1), "file": str(f.relative_to(self.root_path))})
            except:
                pass
        
        return {
            "total_tsx_files": len(tsx_files),
            "total_ts_files": len(ts_files),
            "framework": "Next.js" if has_next else ("React" if has_react else "Unknown"),
            "components": components
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate ringkasan proyek."""
        backend = self._analyze_backend()
        frontend = self._analyze_frontend()
        
        return {
            "project_name": "MAMET OS",
            "backend_framework": backend.get("framework", "Unknown"),
            "frontend_framework": frontend.get("framework", "Unknown"),
            "total_files": backend.get("total_python_files", 0) + frontend.get("total_tsx_files", 0),
            "routes_count": len(backend.get("routes", [])),
            "components_count": len(frontend.get("components", []))
        }