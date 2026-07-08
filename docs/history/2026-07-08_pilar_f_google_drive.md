# Catatan Pengembangan: Sinkronisasi Google Drive (Pilar F)
**Tanggal:** 8 Juli 2026

Dokumen ini mencatat penyelesaian tahap awal dari **Pilar F**, yaitu modul Sinkronisasi *Cloud* menggunakan Google Drive. Fitur ini merupakan syarat mutlak untuk mencapai visi MAMET OS sebagai **"Warisan Digital"**, di mana ingatan pengguna (*database* SQLite) dapat dicadangkan secara otomatis dan ditarik kembali jika terjadi kerusakan perangkat keras keras (*hardware failure*).

## 🚀 Fitur Baru: Modul `GoogleDriveSync`
- **Lokasi File**: `backend/memory/google_drive_sync.py`
- **Konsep Arsitektur**:
  1. **Autentikasi OAuth2**: Sistem menggunakan autentikasi *User-level* (bukan *Service Account*), sehingga data benar-benar disimpan di akun Google Drive pribadi pengguna (tanpa pelacakan *server* terpusat).
  2. **Isolasi Folder**: Modul secara otomatis membuat dan mencari folder bernama `MametOS_Backups` di Drive pengguna agar tidak mencampuri file pribadi lainnya.
  3. **Manajemen File Ganda (`memory.db` & `chromadb.zip`)**:
     - Sistem mendeteksi keberadaan `memory.db` lama dan menimpanya (update) jika ada.
     - Folder `chroma_db` (berisi database vektor/RAG) akan dikompresi menjadi file `chromadb_<email>.zip` secara dinamis di memori sementara, lalu diunggah ke folder yang sama.
     - Langkah ini mencegah penumpukan file ganda di Google Drive setiap kali pencadangan dijalankan.
  4. **Restore Otomatis**: Menyediakan fungsi `restore_database()` untuk menarik *database* kembali ke komputer lokal (sangat berguna jika berpindah perangkat atau menginisialisasi Warisan Digital).

## 📦 Ketergantungan (Dependencies) yang Ditambahkan
Instalasi *library* resmi dari Google:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## ⚠️ Langkah yang Membutuhkan Perhatian Pengguna (MANUAL ACTION REQUIRED)
Karena MAMET OS adalah sistem *local-first* (berjalan di mesin pengguna, bukan *cloud* milik *developer*), autentikasi tidak dapat dilakukan menggunakan *API Key* sembarangan. Anda **wajib** melakukan langkah-langkah di bawah ini satu kali untuk mengaktifkan sinkronisasi awan:

1. Kunjungi **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Buat sebuah proyek baru (misal: "Mamet OS Sync").
3. Buka menu **APIs & Services > Library**, cari **"Google Drive API"**, dan klik **Enable**.
4. Buka menu **OAuth consent screen**, pilih tipe **External**, dan isi nama aplikasinya. (Cukup isi yang wajib saja).
5. Buka menu **Credentials**, klik **Create Credentials > OAuth client ID**.
6. Pilih tipe aplikasi **"Desktop app"**.
7. Klik tombol **Download JSON** di akhir pembuatan.
8. Ganti nama file tersebut menjadi `credentials.json` dan letakkan di dalam folder `D:\SLAMET\other\mamet-os\backend\`.

Setelah file tersebut diletakkan, ketika modul dijalankan pertama kali, ia akan otomatis membuka *browser* Anda untuk meminta izin *(Login with Google)*, lalu menyimpan token sesi secara mandiri di `.mamet/<email>/token.json`.

---
*Dengan selesainya modul ini, tulang punggung Warisan Digital kini telah terbangun!*
