# Riwayat Perubahan: Manajemen RAG Nirkode & Resolusi Path Sub-Agent
**Tanggal**: 9 Juli 2026

## Latar Belakang Masalah
Pada pengujian MAMET OS v3.1 di malam hari, ditemukan dua buah celah hambatan (*friction*) dalam pengalaman pengguna (UX) yang berkaitan dengan agen-agen intelijen dan manajemen memori:

1. **Sub-Agent Buta Folder (Blind Path Resolution)**: 
   Agen `File Analysis` dan `Database Explorer` sering kali melaporkan *"File tidak ditemukan"* ketika pengguna menyuruhnya membaca dokumen. Akar masalahnya adalah agen tersebut secara naif hanya mencari *file* di direktori tempat *backend* dijalankan (`os.getcwd()`), dan mengabaikan variabel `project_context` yang sudah dikirimkan secara cerdas oleh antarmuka pengguna (UI) melalui tombol "Pilih Folder".

2. **RAG Database Tersandera (No-Code RAG Management)**:
   Pengguna berhasil mengunggah dokumen ke pangkalan data vektor ChromaDB (RAG), namun tidak memiliki cara praktis untuk **melihat isi** atau **menghapus** dokumen yang salah unggah. Karena RAG menyimpan data dalam bentuk vektor biner, pengguna tidak bisa menghapusnya dari Windows Explorer biasa. Dibutuhkan antarmuka teks instan di Kolom 3 (Engineer).

## Resolusi & Perubahan Kode

### 1. Injeksi "Smart Fallback" di `evidence_collector.py`
Logika penemuan berkas (*file discovery*) pada `_invoke_sub_agent` direnovasi total. Alih-alih hanya berpatokan pada satu titik, agen kini dibekali tiga lapis insting pencarian:
- **Lapis 1 (Prioritas):** Mencari di dalam `plan.get("project_context")` (direktori yang dipilih pengguna di antarmuka web).
- **Lapis 2:** Mencari di dalam folder mesin (lokal `backend/`).
- **Lapis 3 (Insting Panjat):** Mencari di akar utama proyek (`os.path.dirname(os.getcwd())`).

### 2. Ekspansi `rag_engine.py` (ChromaDB)
Menambahkan dua pilar metode baru ke dalam arsitektur RAG:
- `delete_document(filename)`: Mengeksekusi `collection.delete()` berdasarkan nama file.
- `list_documents()`: Menarik seluruh `metadatas` dari vektor dan memerasnya menjadi `set()` untuk mendapatkan daftar nama *file* unik.

### 3. Pemberdayaan Engineer Agent (`engineer_main.py`)
Membangun "jembatan bahasa manusia" di Kolom 3 agar *user* bisa mengeksekusi kedua metode RAG di atas tanpa menyentuh *database*:
- **Intent `list_rag`**: Dipicu oleh kalimat *"daftar dokumen"* atau *"lihat dokumen rag"*.
- **Intent `delete_rag`**: Dipicu oleh kalimat *"hapus <nama_file>"*.
  - *Bugfix tambahan*: Regex (*Regular Expression*) penyaring nama *file* direlaksasi agar mampu menangkap spasi (contoh: `"diinas pendidikan.txt"`) dengan ekstensi `.txt`/`.pdf`.

## Dampak (Impact)
1. **Navigasi Mulus:** Pengguna kini bisa menyuruh agen AI membaca dokumen apa pun di luar folder *backend* selama folder tersebut telah dipilih di layar "Pilih Folder", membuktikan bahwa MAMET OS kini 100% *Directory-Aware*.
2. **Kemandirian RAG:** Pangkalan data *Retrieval-Augmented Generation* kini bersifat transparan dan dapat dihapus/dibersihkan secara saksama langsung dari terminal *chat* Kolom 3. Sistem tidak lagi "menawan" memori masa lalu yang sudah tak relevan.
