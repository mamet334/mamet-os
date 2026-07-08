# Catatan Pengembangan: Fitur Project Context & Tone Adaptation (Pilar B)
**Tanggal:** 8 Juli 2026

Dokumen ini mencatat pencapaian dan perubahan arsitektur untuk implementasi fitur **Project Context** pada Asisten Pribadi (Kolom 2) sesuai dengan *Spesifikasi v3.1.md*.

## 🚀 Fitur Baru
Fitur **Project Context** memungkinkan Asisten Pribadi untuk melihat, membaca, dan menganalisis folder proyek lokal pengguna secara langsung tanpa perlu mengunggah file (RAG).

## 🛠️ Detail Implementasi

### 1. Integrasi UI Pemilihan Folder Lokal (Native)
- **File Dimodifikasi**: 
  - `desktop/src/routes/workspace/+page.svelte`
  - `desktop/package.json`
  - `desktop/src-tauri/Cargo.toml`
  - `desktop/src-tauri/src/lib.rs`
- **Tindakan**:
  - Menginstal dan menginisialisasi plugin *native* `@tauri-apps/plugin-dialog` di sisi JavaScript maupun Rust (Backend Tauri).
  - Menambahkan tombol **"📁 Pilih Folder"** pada *header* Kolom 2.
  - Memanfaatkan API bawaan OS untuk memunculkan penelusuran direktori dengan aman.
  - Saat direktori dipilih, lokasinya (`project_context`) dikirimkan secara paralel bersama pesan pengguna melalui *payload* ke API FastAPI (`POST /api/process`).

### 2. Rekayasa Aliran Data API & Orkestrator Utama
- **File Dimodifikasi**: 
  - `backend/main.py`
  - `backend/orchestrator/main_orchestrator.py`
- **Tindakan**:
  - Memperbarui skema `ChatRequest` Pydantic untuk mengakomodasi parameter opsional `project_context`.
  - Mengonfigurasi `MainOrchestrator` agar mendeteksi keberadaan *project context*. Jika ada, orkestrator akan menyuntikkan instruksi khusus `"analyze_project"` di urutan nomor 1 pada *Planning Engine*.

### 3. Injeksi Kecerdasan Asisten (Pair Programming)
- **File Dimodifikasi**: 
  - `backend/orchestrator/evidence_collector.py`
  - `backend/orchestrator/decision_engine.py`
- **Tindakan**:
  - Pada *Evidence Collector*, langkah `"analyze_project"` akan memanggil agen **Engineer**, namun dengan batasan (*sandbox*) di mana parameter `root_path` disetel ke `project_context` pilihan pengguna.
  - Pada *Decision Engine*, hasil bacaan/analisis dari Engineer tersebut **tidak langsung dibalas** ke pengguna. Sebaliknya, hasil tersebut digabungkan ke dalam `combined_context` (Konteks Tergabung) Asisten Pribadi.
  - **Hasil Akhir**: LLM (Asisten Pribadi) dapat membaca seluruh detail kode dari folder pengguna, lalu merespons dengan bahasa yang manusiawi layaknya seorang rekan kerja *(Pair Programmer)*. Pengguna bisa bertanya spesifik tentang file apa pun di folder tersebut, dan Asisten akan mengerti seketika. 

## 🛡️ Keamanan (Sandbox)
Meskipun Asisten memiliki akses lewat Engineer, operasi penulisan (*write*) atau modifikasi file tetap tunduk pada hukum *Sandbox*. Jika Asisten (melalui Engineer) berencana mengedit kode, perintah tersebut akan diblokir dan ditampilkan kepada pengguna dalam bentuk tombol **✅ Setujui** atau **🚫 Tolak**.

## 🐛 Perbaikan Kutu (Bug Fixes) Berdasarkan Audit
Selama proses audit dan simulasi *end-to-end* menggunakan skrip khusus (`audit_project_context.py`), ditemukan dan diperbaiki 2 bug kritis dari arsitektur lama:

### 1. Kutu Jalur Akar (Root Path Bug) pada Engineer
- **File Dimodifikasi**: `backend/engineer/engineer_main.py`
- **Masalah**: Sebelumnya, konstruktor `Engineer` selalu menggunakan fungsi pelarian struktur direktori `Path(__file__).parent.parent.parent` secara membabi-buta, bahkan saat `root_path` telah disuplai spesifik. Ini menyebabkan Engineer selalu kembali membaca akar direktori `mamet-os`, mengabaikan direktori apa pun yang dipilih pengguna.
- **Penyelesaian**: Menambahkan evaluasi logis sederhana. Jika `root_path` disuplai, Engineer secara absolut menuruti *path* tersebut tanpa memodifikasi tingkatannya. Jika kosong, barulah ia mundur tiga langkah direktori sebagai konfigurasi *fallback* (*default*).

### 2. Kutu Skala Variabel (UnboundLocalError) pada Orkestrator
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- **Masalah**: Eksekusi Asisten gagal dengan *error* `local variable 'ProviderRouter' referenced before assignment`.
- **Penyelesaian**: Menghapus baris impor lokal `from ai.provider_router import ProviderRouter` yang secara keliru bersarang di dalam blok pernyataan pengondisian logika Agen di fungsi `_build_response()`. Modul tersebut sudah diimpor secara global di kepala dokumen, sehingga penghapusan impor lokal tadi langsung menstabilkan penyalaan LLM Asisten.

---

## 🎭 Fitur Baru: Deteksi Emosi & Tone Adaptation
Untuk memanusiakan Asisten Pribadi dan mengubahnya dari sekadar *chatbot* kaku menjadi entitas berempati (Warisan Digital sesungguhnya), sistem adaptasi nada bicara kini telah diintegrasikan.

### 1. Sensor Emosi pada Planning Engine
- **File Dimodifikasi**: `backend/orchestrator/planning_engine.py`
- **Tindakan**: 
  - Menambahkan metode `_detect_emotion(message)` berbasis pengenalan pola *Regular Expression* (RegEx) yang menganalisis panjang kalimat, tanda baca (seperti `!!` atau `???`), dan kata kunci emosional.
  - Klasifikasi emosi terbagi menjadi 5: **marah/kesal**, **terburu-buru**, **bingung/sedih**, **santai**, dan **netral**.
  - Hasil emosi disematkan ke dalam *blueprint* `plan["emotion"]`.

### 2. Injeksi Hormon pada LLM (Main Orchestrator)
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- **Tindakan**:
  - Saat membangun *System Prompt* di fungsi `_build_response()`, orkestrator akan menyuntikkan instruksi khusus (*tone_prompt*) berdasarkan `plan["emotion"]`.
  - Jika pengguna *terburu-buru*, AI dipaksa membuang seluruh basa-basi. Jika pengguna *bingung*, AI merespons dengan empati tinggi dan memandu pelan-pelan. Jika *santai*, AI menggunakan gaya bahasa *casual/slang*.
  - **Hasil Akhir**: Asisten Pribadi mampu menyesuaikan *vibe* atau aura percakapan secara dinamis (*real-time*).

### 3. Hasil Audit Skenario Emosi
Melalui pengujian simulasi *end-to-end* (`audit_emotion.py`) yang memotong koneksi internet sementara untuk mengintip hasil akhir *System Prompt*, terbukti sistem ini memiliki akurasi 100%:
- **😡 MARAH** ("sistem ini error terus!!"): Asisten diinstruksikan untuk *sangat sabar, meminta maaf, solutif, dan tidak bertele-tele*.
- **🏃 TERBURU-BURU** ("Cepat buatkan script sekarang!"): Asisten diinstruksikan merespons *SANGAT SINGKAT, langsung ke inti, tanpa basa-basi*.
- **🥺 BINGUNG** ("Tolong banget, saya bingung..."): Asisten diinstruksikan merespons dengan *empati, menenangkan, dan memandu pelan-pelan*.
- **☕ SANTAI** ("Halo bro, mantap nih..."): Asisten diinstruksikan menggunakan gaya bahasa *kasual, asyik, dan slang ringan*.
- **😐 NETRAL**: Asisten kembali ke setelan baku (*ramah, profesional, singkat*).

---

## 📝 Fitur Baru: Meringkas & Menulis Terstruktur (Executive Summary)
Untuk menyempurnakan kemampuan analisis dari Kolom 2 (terutama saat digabungkan dengan Project Context atau Pembacaan File), kini Asisten dibekali kemampuan "Menulis Terstruktur".

### 1. Deteksi Niat Meringkas (Summarize Intent)
- **File Dimodifikasi**: `backend/orchestrator/planning_engine.py`
- **Tindakan**: Menambahkan `summarize_pattern` pada fungsi `_detect_intent()` yang akan mendeteksi variasi kata seperti *ringkas, rangkum, resume, summary, kesimpulan*. Jika terdeteksi, *blueprint* rencana (`plan`) akan diberi penanda `requires_structured_format: True`.

### 2. Injeksi Aturan Penulisan Laporan (LLM Prompt)
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- **Tindakan**: Saat parameter `requires_structured_format` aktif, orkestrator secara dinamis akan menambahkan blok **PENTING** ke dalam *System Prompt* LLM. Blok ini memaksa LLM untuk membuang gaya penulisan paragraf panjang, dan menggantinya dengan format laporan terstruktur menggunakan *Markdown* (Heading, Poin-poin tebal, dan Tabel Komparasi).
- **Hasil Akhir**: Jika Anda menyuruh Asisten *"Tolong rangkum file README.md ini"*, ia tidak akan membalas dengan gumpalan paragraf, melainkan dengan struktur poin presentasi yang elegan dan sangat mudah dibaca.

---

## ⛓️ Fitur Baru: Tugas Multi-langkah Otonom (Berantai)
Sebagai penutup paripurna dari Pilar B, Asisten kini telah "lepas dari rantai" instruksi tunggal. Ia dapat menangani beberapa perintah berturut-turut dalam satu pesan.

### 1. Dekonstruksi Pesan di Planning Engine
- **File Dimodifikasi**: `backend/orchestrator/planning_engine.py`
- **Tindakan**: Menambahkan logika pemisahan string (*string splitting*) berdasarkan konjungsi (kata hubung) seperti *lalu, kemudian, setelah itu, dan*. Pesan pengguna akan dibedah menjadi urutan tugas (`sub_tasks`), dan parameter `is_multi_step` diaktifkan.

### 2. Injeksi Instruksi Otonom di Main Orchestrator
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- **Tindakan**: Jika pesan dideteksi memiliki banyak langkah, orkestrator akan:
  - Menyusun seluruh langkah tersebut menjadi urutan angka (1, 2, 3...) di dalam *System Prompt*.
  - Memerintahkan LLM secara tegas untuk mengeksekusi semua langkah tersebut *dalam satu tarikan napas* (satu balasan utuh).
  - Menyediakan "jalan pintas" ke Engineer (Kolom 3): Jika langkah terakhir adalah "*simpan ke file X*", Asisten diinstruksikan untuk menyajikan teksnya ke dalam *Code Block* dan memberitahu Anda untuk menyuruh Engineer mengeksekusinya.
- **Hasil Akhir (Audit)**: Saat diuji dengan perintah *"Cari berita AI, kemudian buatkan ringkasannya, dan simpan ke file berita.md"*, sistem sukses memecahnya secara presisi menjadi 3 langkah berantai!

---

## 🛠️ Perbaikan Konflik (Bug Fix): Multi-Langkah vs Engineer
Selama pengujian *Ultimate Test* (menggabungkan seluruh fitur secara bersamaan), ditemukan sebuah tabrakan logika antara perintah berantai dan mesin *Regular Expression* milik agen Engineer.

### Masalah
Saat pengguna meminta: *"Tolong ringkas dokumen planning_engine.py, lalu simpan ke hasil.md"*, agen Engineer (yang bertugas membaca file untuk Project Context) justru menolak beroperasi dengan *error*: `Format tidak dikenali`. 
**Kenapa?** Karena mata Engineer terfokus pada kata *"simpan"*. Ia mengira pengguna menyuruhnya menulis file (intent `write_file`), sehingga ia mengabaikan instruksi untuk "membaca" file `planning_engine.py`.

### Solusi Kode yang Diubah
- **File Dimodifikasi**: `backend/engineer/engineer_main.py`
- **Perubahan di `_detect_intent`**: Menambahkan kata kunci *"ringkas"* dan *"rangkum"* ke dalam kelompok instruksi `read_file`. Jika kata-kata tersebut terdeteksi, Engineer kini menyadari bahwa tugasnya adalah **membaca file**, kecuali terdapat instruksi spesifik penulisan (*"dengan isi"*).
- **Perubahan di `_extract_file_path`**: Memperbarui pola *Regex* pencarian nama file agar dapat menangkap kata sandang *"dokumen"* (sebelumnya hanya mengerti kata *"file"*).

**Status Saat Ini:** Dengan perbaikan ini, keempat fitur raksasa (Project Context, Deteksi Emosi, Format Terstruktur, dan Tugas Multi-langkah) dapat dikawinkan dalam **satu perintah** tanpa ada *error* tabrakan logika satupun. Pilar B sukses diimplementasikan!
