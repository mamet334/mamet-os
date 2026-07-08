# Changelog

Semua perubahan penting pada proyek ini akan dicatat di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/id/1.0.0/),
dan proyek ini menggunakan [Semantic Versioning](https://semver.org/lang/id/).

## [0.1.0] - 2026-07-06

### Ditambahkan
- Kernel Main Orchestrator dengan siklus PLAN → COLLECT → DECIDE → RESPOND
- Planning Engine berbasis aturan simbolik (tanpa LLM)
- Evidence Collector modular dengan sumber cache, user memory, RAG, engineer
- Decision Engine dengan decision tree dan confidence threshold
- Tiga kolom chat: Pencarian Cepat, Asisten Pribadi, Engineer
- Engineer Basic dengan kemampuan analisis proyek, baca file, list direktori
- Safety Guard untuk Engineer (persetujuan wajib untuk tindakan berbahaya)
- Code Analyzer untuk mendeteksi framework, routes, komponen
- File Reader untuk menjelajahi struktur proyek
- Frontend Next.js + TailwindCSS dengan UI responsif (desktop 3 kolom, mobile 1 kolom)
- Backend FastAPI + Uvicorn dengan auto-reload
- Deployment ke Vercel melalui GitHub auto-deploy
- Dokumentasi SPESIFIKASI.md (dilindungi .gitignore)

### Status Pengembangan
- Kernel: ✅ Berfungsi penuh
- Kolom 1 (Pencarian Cepat): ⚠️ Fallback (menunggu RAG)
- Kolom 2 (Asisten Pribadi): ⚠️ Fallback (menunggu User Memory)
- Kolom 3 (Engineer Basic): ✅ Analisis, baca file, list direktori
- UI 3 Kolom: ✅ Berfungsi, responsif
- Engineer Write/Execute: ⬜ Perlu persetujuan user (fitur berikutnya)


## [0.1.1] - 2026-07-06

### Ditambahkan
- RAG Engine dengan ChromaDB untuk pencarian dokumen
- Document Chunker berbasis paragraf dengan overlap 50 kata
- Embedding Engine via OpenRouter API (dengan fallback pencarian teks)
- Endpoint `/upload` untuk unggah dokumen (PDF, DOCX, TXT, MD, CSV, JSON)
- Tombol Upload di Kolom 1 (Pencarian Cepat)
- Pencarian teks sederhana saat API key tidak tersedia
- Integrasi RAG ke Evidence Collector dan Decision Engine
- Dependensi: chromadb, PyMuPDF, python-docx, python-multipart

### Diperbaiki
- Bug 500 Internal Server Error saat menampilkan hasil RAG
- Bug koneksi frontend-backend (ECONNREFUSED)
- Bug python-multipart tidak terinstal
- Bug `response` None pada `_build_response`

### Status Pengembangan
- Kolom 1 (Pencarian Cepat): ✅ Upload + pencarian berfungsi
- Kolom 2 (Asisten Pribadi): ⚠️ Fallback (menunggu User Memory)
- Kolom 3 (Engineer Basic): ✅ Analisis, baca file, list direktori

## [3.0.0-alpha.1] - 2026-07-08

### Ditambahkan
- **Layar Login & Auth (Pilar E):** Menambahkan sistem autentikasi penuh berbasis JWT (JSON Web Token) dan SQLite untuk mengamankan akses sistem dan mendukung multi-identitas.
- **Dashboard Awal:** Halaman pemantauan sistem (landing page) interaktif sebelum memasuki ruang kerja. Menampilkan indikator kesehatan Kernel, RAG, Memori Pengguna, dan anggaran limit model bahasa AI secara *real-time*.
- **Credit Berjalan:** Mekanisme *onboarding* dramatis (teks animasi vertikal) untuk menyampaikan filosofi warisan digital dan tata cara penggunaan. Berkas narasinya dapat disesuaikan pengguna melalui modifikasi pada `desktop/static/credit.txt`.
- **Restrukturisasi Routing:** Memisahkan alur masuk aplikasi menjadi SPA (Single Page Application) penuh (Login → Dashboard → Credit → Workspace/3-Kolom).
- **Desain UI/UX Modern (Level 4):** Mengaplikasikan tema *Premium Glassmorphism* (backdrop-blur-xl, bayangan cyan glowing) secara global. Menambahkan Google Fonts (Inter & JetBrains Mono) dan merombak estetika komponen dengan palet warna spesifik MAMET OS (Cyan, Purple, Amber).

### Diperbaiki
- Memperbaiki pembacaan *AI Provider* pada *endpoint* `/api/status` di `main.py` yang sebelumnya memicu galat (Status 500) saat *Dashboard Awal* memuat data. Sistem sekarang menggunakan referensi `ProviderRouter` yang tepat.
- Menambal celah galat UI Svelte (*TypeError toLocaleString*) yang memicu layar kosong secara seketika pada antarmuka Dasbor sesudah proses login disahkan. Sinkronisasi nama properti batas anggaran dari Backend ke Svelte telah diselaraskan penuh.
- Mengembalikan kecepatan animasi *Credit Berjalan* ke pengali dinamis `2.0s`, serta memodifikasi struktur matematis *keyframes* CSS (`-100% + 100vh`) dengan dipadukan ruang kosong bantalan bawah (`pb-[50vh]`). Ini menjamin guliran teks selalu berhenti dan terkunci secara akurat tepat di tengah layar berapapun tinggi tulisan/memori yang ditambahkan. Pengguna diwajibkan untuk mengklik tombol "Lewati" secara manual saat selesai.
- Menambal celah pemotongan teks (*text cut off*) pada Credit Berjalan dengan menambahkan instruksi tata letak vertikal `items-start` (*flex-start*). Ini mencegah tinggi modul teks ditarik meregang menyamai tinggi layar yang membuat algoritma laju gulir (`translateY`) menjadi kacau.
- **Merombak Arsitektur Workspace**: Beralih dari tampilan 3-Kolom serentak menjadi tata letak Panel Navigasi Kiri (*Sidebar*) dengan Layar Utama 1-Kolom. Ini memberikan kelegaan visual, ruang *chat* yang lebih lebar, dan integrasi layar *Settings* (Dashboard) yang lebih modern menyatu ke dalam kolom utama (bukan lagi *modal overlay*).

---

## [0.2.0] - 2026-07-08

### Ditambahkan
- **Ekspansi Lego (Fase 4):** Penyempurnaan `LegoRegistry` untuk mendeteksi, memuat, dan menginisialisasi script modul kustom secara dinamis dari direktori `custom_modules/` menggunakan `importlib` dan `inspect`. Penambahan kemampuan baru kini bisa dilakukan secara Plug-and-Play tanpa memodifikasi baris kode inti.
- Modul contoh `hello_lego.py` sebagai *proof of concept* berjalannya sistem pendaftaran otomatis modul Lego.

### Diperbaiki
- Sinkronisasi skrip `deep_audit.py` yang kedaluwarsa. Menyesuaikan nama langkah (*step*) dari `"check_engineer"` menjadi `"check_rag_knowledge"` agar selaras dengan arsitektur Planning Engine yang baru, serta merevisi pengujian *error handling* pada Database Agent untuk memastikan respons atas file palsu ditangani dan dibaca oleh penguji secara tepat.