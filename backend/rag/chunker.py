"""
MAMET OS - Document Chunker
=============================
Memecah dokumen menjadi chunk yang siap di-embedding.
Menjaga makna dokumen dengan chunking berbasis struktur.
"""

import re
from typing import List, Dict


class DocumentChunker:
    """Memecah dokumen menjadi chunk."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Pecah teks menjadi chunk dengan overlap.
        
        Args:
            text: Teks dokumen
            metadata: Metadata dokumen (nama file, dll.)
            
        Returns:
            List chunk dengan metadata
        """
        metadata = metadata or {}
        chunks = []
        
        # Bersihkan teks
        text = text.strip()
        if not text:
            return chunks
        
        # Pecah berdasarkan paragraf dulu
        paragraphs = self._split_by_paragraph(text)
        
        # Gabung paragraf jadi chunk dengan ukuran tertentu
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            # Jika paragraf sendiri sudah lebih besar dari chunk_size,
            # pecah berdasarkan kalimat
            if len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, metadata, chunk_index))
                    chunk_index += 1
                    current_chunk = ""
                
                sub_chunks = self._split_long_paragraph(para)
                for sub in sub_chunks:
                    chunks.append(self._create_chunk(sub, metadata, chunk_index))
                    chunk_index += 1
                continue
            
            # Jika ditambah paragraf ini masih muat
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                # Simpan chunk saat ini
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk.strip(), metadata, chunk_index))
                    chunk_index += 1
                
                # Mulai chunk baru dengan overlap
                if self.overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-self.overlap:]
                    current_chunk = overlap_text + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        # Simpan chunk terakhir
        if current_chunk.strip():
            chunks.append(self._create_chunk(current_chunk.strip(), metadata, chunk_index))
        
        return chunks
    
    def _split_by_paragraph(self, text: str) -> List[str]:
        """Pecah teks berdasarkan paragraf."""
        # Split berdasarkan baris kosong
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """Pecah paragraf panjang menjadi chunk lebih kecil."""
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) <= self.chunk_size:
                current += sentence + " "
            else:
                if current:
                    chunks.append(current.strip())
                
                # Jika kalimat sendiri lebih panjang, potong paksa
                if len(sentence) > self.chunk_size:
                    for i in range(0, len(sentence), self.chunk_size - self.overlap):
                        chunks.append(sentence[i:i+self.chunk_size].strip())
                else:
                    current = sentence + " "
        
        if current.strip():
            chunks.append(current.strip())
        
        return chunks
    
    def _create_chunk(self, text: str, metadata: Dict, index: int) -> Dict:
        """Buat chunk dengan metadata."""
        return {
            "text": text,
            "index": index,
            "char_count": len(text),
            "metadata": {
                **metadata,
                "chunk_index": index
            }
        }