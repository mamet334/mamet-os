"""
MAMET OS - RAG Engine
=======================
Orchestrator untuk Retrieval-Augmented Generation.
Menangani upload dokumen, chunking, embedding, dan pencarian.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# ChromaDB untuk vector storage (lokal)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("[RAG] Peringatan: ChromaDB tidak tersedia. Install dengan: pip install chromadb")

from .chunker import DocumentChunker
from .embedding import EmbeddingEngine


class RAGEngine:
    """Engine RAG untuk pencarian dokumen."""
    
    def __init__(self, persist_dir: str = None, api_key: str = None):
        """
        Inisialisasi RAG Engine.
        
        Args:
            persist_dir: Direktori untuk menyimpan ChromaDB
            api_key: OpenRouter API key
        """
        self.persist_dir = persist_dir or os.path.join(os.getcwd(), "chroma_db")
        self.chunker = DocumentChunker(chunk_size=500, overlap=50)
        self.embedding_engine = EmbeddingEngine(api_key=api_key)
        self.collection = None
        
        if CHROMA_AVAILABLE:
            self._init_chromadb()
    
    def _init_chromadb(self):
        """Inisialisasi ChromaDB client dan collection."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Dapatkan atau buat collection
            self.collection = self.client.get_or_create_collection(
                name="mamet_documents",
                metadata={"description": "Dokumen MAMET OS"}
            )
            
            print(f"[RAG] ✅ ChromaDB siap di {self.persist_dir}")
            print(f"[RAG] 📊 Collection: {self.collection.count()} dokumen")
        except Exception as e:
            print(f"[RAG] ❌ Gagal inisialisasi ChromaDB: {str(e)}")
            self.collection = None
    
    def set_api_key(self, api_key: str):
        """Set API key untuk embedding."""
        self.embedding_engine.set_api_key(api_key)
    
    def add_document(
        self,
        content: str,
        filename: str,
        metadata: Dict = None
    ) -> Dict:
        """
        Tambahkan dokumen ke RAG.
        
        Args:
            content: Isi dokumen
            filename: Nama file
            metadata: Metadata tambahan
            
        Returns:
            Dict dengan status dan statistik
        """
        if not content.strip():
            return {"status": "error", "message": "Dokumen kosong"}
        
        # Buat metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "char_count": len(content)
        })
        
        # Chunking
        print(f"[RAG] Chunking dokumen: {filename}")
        chunks = self.chunker.chunk_text(content, doc_metadata)
        print(f"[RAG] 📦 {len(chunks)} chunk dibuat")
        
        if not chunks:
            return {"status": "error", "message": "Tidak ada chunk yang dihasilkan"}
        
        # Embedding
        texts = [chunk["text"] for chunk in chunks]
        print(f"[RAG] Embedding {len(texts)} chunk...")
        embeddings = self.embedding_engine.embed_documents(texts)
        
        # Simpan ke ChromaDB
        if self.collection:
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            print(f"[RAG] ✅ Dokumen tersimpan di ChromaDB")
        
        return {
            "status": "success",
            "filename": filename,
            "chunks": len(chunks),
            "char_count": len(content),
            "stored": self.collection is not None
        }
    
    def search(
        self,
        query: str,
        similarity_threshold: float = 0.65,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Cari dokumen berdasarkan query.
        Jika embedding tidak tersedia (tidak ada API key),
        gunakan pencarian teks sederhana.
        
        Args:
            query: Teks pencarian
            similarity_threshold: Ambang batas similarity (0-1)
            max_results: Maksimum hasil yang dikembalikan
            
        Returns:
            List hasil pencarian dengan metadata dan skor
        """
        if not self.collection or self.collection.count() == 0:
            print("[RAG] ⚠️ Tidak ada dokumen untuk dicari")
            return []
        
        # Cek apakah embedding engine punya API key
        if not self.embedding_engine.api_key:
            print("[RAG] ⚠️ Tidak ada API key. Menggunakan pencarian teks sederhana.")
            return self._text_search(query, max_results)
        
        # Embedding-based search
        query_embedding = self.embedding_engine.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(max_results, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance
                
                if similarity >= similarity_threshold:
                    search_results.append({
                        "id": doc_id,
                        "text": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "similarity": round(similarity, 4),
                        "source": results["metadatas"][0][i].get("filename", "unknown") if results["metadatas"] else "unknown"
                    })
        
        search_results.sort(key=lambda x: x["similarity"], reverse=True)
        print(f"[RAG] 🔍 '{query[:50]}...' → {len(search_results)} hasil (threshold: {similarity_threshold})")
        return search_results
    
    def _text_search(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Pencarian teks sederhana tanpa embedding.
        Mencari dokumen yang mengandung kata kunci query.
        """
        # Ambil semua dokumen dari collection
        try:
            all_docs = self.collection.get(
                include=["documents", "metadatas"]
            )
        except Exception as e:
            print(f"[RAG] ❌ Gagal mengambil dokumen: {e}")
            return []
        
        if not all_docs or not all_docs["ids"]:
            return []
        
        query_lower = query.lower()
        results = []
        
        for i, doc_id in enumerate(all_docs["ids"]):
            text = all_docs["documents"][i] if all_docs["documents"] else ""
            metadata = all_docs["metadatas"][i] if all_docs["metadatas"] else {}
            
            # Hitung skor relevansi sederhana: berapa kali kata kunci muncul
            text_lower = text.lower()
            score = 0
            for word in query_lower.split():
                score += text_lower.count(word)
            
            if score > 0:
                # Normalisasi skor ke 0-1
                max_possible = len(text_lower.split()) / len(query_lower.split()) if len(query_lower.split()) > 0 else 1
                normalized_score = min(score / max(1, max_possible), 1.0)
                
                results.append({
                    "id": doc_id,
                    "text": text[:300] + "..." if len(text) > 300 else text,
                    "metadata": metadata,
                    "similarity": round(normalized_score, 4),
                    "source": metadata.get("filename", "unknown")
                })
        
        # Urutkan berdasarkan skor
        results.sort(key=lambda x: x["similarity"], reverse=True)
        # Ambil maksimal max_results
        results = results[:max_results]
        
        print(f"[RAG] 📝 Text search '{query[:50]}...' → {len(results)} hasil")
        return results
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik RAG."""
        if self.collection:
            return {
                "total_documents": self.collection.count(),
                "persist_dir": self.persist_dir,
                "embedding_model": self.embedding_engine.model,
                "chunk_size": self.chunker.chunk_size,
                "similarity_threshold": 0.65
            }
        return {"status": "not_available"}
        
    def list_documents(self) -> List[str]:
        """Dapatkan daftar nama file unik yang tersimpan di RAG."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.get(include=["metadatas"])
            if not results or not results["metadatas"]:
                return []
                
            filenames = set()
            for metadata in results["metadatas"]:
                if metadata and "filename" in metadata:
                    filenames.add(metadata["filename"])
            return sorted(list(filenames))
        except Exception as e:
            print(f"[RAG] Gagal melist dokumen: {e}")
            return []
    
    def delete_document(self, filename: str) -> Dict:
        """Hapus dokumen berdasarkan nama file."""
        if not self.collection:
            return {"status": "error", "message": "ChromaDB tidak tersedia"}
        
        # Cari semua chunk dengan filename ini
        results = self.collection.get(
            where={"filename": filename}
        )
        
        if results and results["ids"]:
            self.collection.delete(ids=results["ids"])
            return {"status": "success", "deleted": len(results["ids"])}
        
        return {"status": "not_found"}