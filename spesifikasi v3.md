```markdown
# MAMET OS v3.0 — Spesifikasi Teknis Lengkap (Personal Edition)

## Visi
MAMET OS adalah **asisten pribadi lokal** yang tumbuh bersama pengguna, mampu mengingat, mencari, membantu coding, dan menjelajah internet. Tujuan akhirnya adalah menjadi **warisan digital** — aplikasi utuh yang bisa diwariskan dan terus hidup membantu orang yang ditinggalkan.

## Filosofi Desain
- **Full Custom Control**: Semua bisa diatur sendiri (AI provider, database, folder kerja).
- **Lokal & Portabel**: Semua data di harddisk, satu folder, bisa dicopy.
- **Multi-Identitas**: Ganti akun email = ganti seluruh memori dan database.
- **Self-Evolving**: Engineer bisa membantu mengembangkan aplikasi ini sendiri.
- **Warisan Digital**: Aplikasi ini sendiri adalah warisan, bukan cuma isinya.

---

## Arsitektur Sistem

### 1. MAMET Core (Python)
Backend yang berjalan sebagai server lokal (`localhost`), berisi:
- **Kernel Orchestrator** dengan siklus simbolik PLAN → COLLECT → DECIDE → RESPOND
- **Evidence Collector** multi-sumber (cache, memory, RAG, Engineer) dengan confidence score
- **Decision Engine** berbasis decision tree, bukan LLM (hemat biaya, transparan)
- **RAG Engine** (ChromaDB) untuk pencarian dokumen semantik
- **User Memory** (SQLite) untuk fakta personal, preferensi, konteks
- **Engineer** untuk analisis kode, write/execute dengan safety guard
- **LLM Provider Router** untuk multi-provider AI (OpenRouter, OpenAI, Grok, Gemini)

### 2. MAMET Shell (UI)
Frontend 3 kolom:
- **Kolom 1**: Pencarian Cepat (RAG) — threshold similarity, ambil semua > threshold
- **Kolom 2**: Asisten Pribadi — User Memory + sub-agent + LLM
- **Kolom 3**: Engineer — self-maintenance, coding, approval wajib

Setiap kolom punya notifikasi mandiri, tidak mengganggu kolom lain.

### 3. Database
- **SQLite**: User memory, fakta, preferensi, log percakapan, registry modul
- **ChromaDB**: Vector embedding dokumen (mode persistent di folder lokal)
- Keduanya disimpan di folder `~/.mamet/` (atau `%APPDATA%/MametOS/` di Windows)
- **Multi-identitas**: Setiap email login punya folder database terpisah

### 4. Sistem Keamanan (Pertahanan Berlapis)
- **Lapis 1**: Sandbox filesystem dengan path whitelist, no-exec, user terbatas
- **Lapis 2**: Pembatasan jaringan (firewall aplikasi lokal, whitelist domain)
- **Lapis 3**: Static analysis kode (Bandit, ESLint) sebelum approval
- **Lapis 4**: ClamAV untuk scan file upload
- **Lapis 5**: Verifikasi integritas modul Lego (tanda tangan digital)
- **Lapis 6**: Backup & rollback otomatis sebagai jaring pengaman terakhir

---

## Arsitektur Modular (Lego System)

```
┌──────────────────────────────────────────────────────────────┐
│                     MAMET OS - Main Orchestrator              │
│                (Local Desktop App via Tauri + Svelte 5)       │
├──────────────────────────────────────────────────────────────┤
│          [Login: Email + Password]                             │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Kolom 1  │  │   Kolom 2    │  │      Kolom 3         │   │
│  │Pencarian│  │   Asisten    │  │     Engineer         │   │
│  │ Cepat   │  │   Pribadi    │  │  Self-Maintenance    │   │
│  └────┬─────┘  └──────┬───────┘  └──────────┬───────────┘   │
│       │               │                     │               │
│  ┌────┴───────────────┴─────────────────────┴───────────┐   │
│  │              PLUGGABLE MODULES (LEGO)                │   │
│  ├──────────┬──────────┬──────────┬──────────┬─────────┤   │
│  │ RAG      │ User     │ Agent    │ Database │ Model   │   │
│  │ Engine   │ Memory   │ Pool     │ Detector │ Router  │   │
│  └──────────┴──────────┴──────────┴──────────┴─────────┘   │
│  ┌──────────┬──────────┬──────────┬────────────────────┐   │
│  │ File     │ Internet │ Code     │ Custom Modules     │   │
│  │ System   │ Gateway  │ Engine   │ (user-defined)     │   │
│  └──────────┴──────────┴──────────┴────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**Filosofi Lego:** Setiap modul berdiri sendiri dengan interface standar. Bisa ditambah, dilepas, diganti, dan dikustomisasi per user.

---

## Spesifikasi Tiga Kolom

### Kolom 1: Pencarian Cepat

| Atribut | Spesifikasi |
|---------|-------------|
| Fungsi utama | Mencari informasi dari dokumen yang diunggah user |
| Sumber data | **Hanya RAG** |
| Akses memori percakapan | **TIDAK** |
| Embedding | Multi-provider (OpenAI, Gemini, OpenRouter) |
| Top-k | **Similarity threshold** — ambil semua chunk > threshold, tidak dipotong |
| Output | Hasil pencarian + kutipan sumber (nama file, halaman, potongan teks) |
| Upload dokumen | PDF, DOCX, TXT, MD, CSV, JSON via drag & drop / tombol |

**Alur kerja:**
```
User query → Embed query via provider aktif → Cari di ChromaDB dengan threshold similarity → 
Ambil semua chunk di atas threshold → Tampilkan hasil + sumber dokumen
```

**Untuk data besar (contoh: 500+ pegawai ASN):**
- Threshold similarity misal 0.65
- Jika 70 chunk relevan, semua 70 ditampilkan
- Pagination di UI untuk navigasi
- Filter tambahan opsional (nama, NIP, unit kerja) untuk mempersempit

### Kolom 2: Asisten Pribadi

| Atribut | Spesifikasi |
|---------|-------------|
| Fungsi utama | Membantu pekerjaan user, mengenal user secara personal |
| Sumber data | User Memory + RAG + Internet (via sub-agent) + Database terdeteksi |
| Sub-agent | Dipilih **MANUAL** oleh user |
| Pemahaman makna | Harus bisa memahami makna percakapan (intent, konteks, emosi) |
| Folder kerja | Hanya folder yang dipilih user (sandboxing ketat) |

**Sub-agent yang tersedia:**
- **Research**: Riset mendalam multi-langkah (Internet + RAG)
- **Web Search**: Mencari informasi terkini di web
- **File Analisis**: Membaca, menganalisis file dalam folder kerja
- **Database Explorer**: Membaca/menulis database yang terdeteksi

**User Memory:**
- Profil pengguna (nama, preferensi, pengaturan)
- Riwayat percakapan lengkap dengan summarization periodik
- Fakta penting yang diekstrak otomatis dari percakapan
- Mekanisme forgetting untuk informasi usang atau kontradiktif

### Kolom 3: Engineer (Self-Maintenance)

| Atribut | Spesifikasi |
|---------|-------------|
| Fungsi utama | Memperbaiki, memperbarui, dan membangun MAMET OS |
| Sumber pengetahuan | RAG internal + Database + Kode sistem + Internet (fallback) |
| Persetujuan user | **WAJIB** untuk semua perubahan |
| Target | **POWERFULL** |

**Kemampuan Powerfull:**
- Analisis kode menyeluruh (baca seluruh codebase, pahami dependensi)
- Multi-file refactoring dengan analisis dampak
- Database manipulation (migrasi, optimasi, backup/restore)
- Self-patching dari log error
- Testing otomatis setelah perubahan
- Rollback cerdas jika perubahan gagal
- Dua Sandbox + Rollback untuk keamanan maksimal

---

## Database Detector Otomatis (Lego DB)

Mendeteksi, memetakan, dan membuat interface otomatis untuk database baru.

**Cara kerja:**
```
User upload/connect database baru
        │
        ▼
┌─────────────────────────┐
│  DATABASE DETECTOR      │
│  (Auto-scanning)        │
├─────────────────────────┤
│ 1. Deteksi tipe         │  CSV, JSON, Excel, PostgreSQL, MySQL, SQLite
│ 2. Baca struktur        │  Header, tipe data, relasi
│ 3. Mapping otomatis     │  Buat interface standar
│ 4. Registrasi           │  Daftarkan sebagai Lego Module
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  DATABASE INTERFACE     │
│  (Auto-generated)       │
├─────────────────────────┤
│ • Tabel yang tersedia   │
│ • Kolom per tabel       │
│ • Tipe data             │
│ • Relasi                │
│ • Sample data (5 rows)  │
└───────────┬─────────────┘
            │
   ┌────────┴────────┐
   ▼                 ▼
Kolom 1 (RAG)    Kolom 2 (Asisten)
• Baca DB        • Baca/Tulis/Edit DB
• Search via     • Query natural language
  embedding      • Analisis data
                 • Laporan otomatis
```

**Kemampuan setelah terdeteksi:**
- Baca data (otomatis)
- Tulis data baru (dengan konfirmasi)
- Edit data (dengan konfirmasi)
- Hapus data (konfirmasi eksplisit)
- Query bahasa alami → SQL

---

## Multi-Provider AI

### Interface Standar
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class AIProvider(ABC):
    name: str
    
    @abstractmethod
    def chat(self, messages: List[Dict], model: str) -> str: ...
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]: ...
```

### Provider yang Didukung (Bertahap)
1. **OpenRouter** (sudah ada, tinggal bungkus ke interface)
2. **OpenAI**
3. **Grok**
4. **Gemini**

### Konfigurasi
- Setiap provider punya API key terenkripsi sendiri (AES-256)
- Disimpan di tabel `providers`: `name, api_key_encrypted, is_active, priority`
- Prioritas dan fallback otomatis: jika provider 1 gagal, coba provider 2
- Budget cap per provider
- UI Settings untuk tambah/hapus provider, pilih default, lihat status

---

## Pilar Pengembangan

### Pilar A: Kecerdasan & Memori

**A1. Mekanisme Forgetting yang Lebih Cerdas**
- **Konflik Fakta**: Jika LLM mengekstrak fakta baru yang bertentangan dengan fakta lama (confidence tinggi vs rendah), sistem otomatis nonaktifkan yang lama dan catat alasannya.
- **Fakta Bertanggal**: Setiap fakta punya `expires_at`. Fakta tentang "pekerjaan saat ini" mungkin kedaluwarsa lebih cepat daripada "nama lengkap".
- **User Review**: Di dashboard, user bisa melihat daftar fakta yang diingat dan menghapus yang tidak relevan.

**A2. Offline LLM (Ollama)**
- Integrasi Ollama sebagai provider lokal opsional.
- Kalau internet mati, MAMET OS fallback ke model lokal.
- User bisa memilih model Ollama mana yang dipakai (Llama 3, Mistral, dll).
- Prioritas provider: Lokal (gratis) → Cloud (berbayar).

**A3. Memori Kontekstual**
- Tidak hanya mengingat fakta, tapi juga **konteks percakapan**.
- Jika user minggu lalu membahas "proyek A", minggu ini Asisten bisa merujuk: "Lanjutan dari proyek A yang kemarin..."
- Summarization otomatis untuk percakapan panjang.

---

### Pilar B: Pendalaman Kolom 2 & 3

**B1. Asisten Pribadi yang Lebih Empatik**
- Deteksi nada emosi (senang, sedih, frustrasi) dari pesan user.
- Respons disesuaikan: lebih hangat saat user sedih, lebih profesional saat serius.
- Tidak over-engineered: cukup 3-4 tone (friendly, professional, comforting, direct).

**B2. Engineer Multi-file & Testing**
- Engineer tidak hanya menulis satu file, tapi bisa refactor banyak file sekaligus.
- Setelah menulis kode, Engineer otomatis menjalankan testing (kalau ada test script).
- Kalau test gagal, Engineer memberi tahu dan menawarkan perbaikan.

**B3. Asisten sebagai "Teman Diskusi"**
- Mode brainstorming: Asisten memberikan pertanyaan balik, bukan hanya jawaban.
- Mode ringkasan harian: setiap pagi, Asisten memberi ringkasan aktivitas kemarin.

---

### Pilar C: Agen & Otomatisasi

**C1. Database Explorer yang Lebih Pintar**
- Natural language → SQL yang lebih akurat.
- Bisa JOIN tabel otomatis berdasarkan relasi yang terdeteksi.
- Bisa membuat visualisasi sederhana (chart) dari data.

**C2. File Analysis yang Lebih Dalam**
- Selain baca file, agen bisa **membandingkan** dua file.
- Bisa membaca gambar (OCR) jika diperlukan.
- Bisa membaca file ZIP dan menganalisis isinya.

**C3. Web Search yang Lebih Agresif**
- Tidak hanya Wikipedia, tapi juga crawling halaman web umum.
- Bisa merangkum beberapa sumber sekaligus.
- Deteksi berita hoax atau informasi tidak valid (confidence flag).

---

### Pilar D: Keamanan & Stabilitas

**D1. Unit Test & Integration Test**
- Setiap modul punya test sendiri.
- Sebelum deploy ke live, Engineer wajib menjalankan test.
- Test report ditampilkan di dashboard.

**D2. Stress Test & Error Recovery**
- Simulasi banyak request bersamaan.
- Simulasi file besar (100MB+) di-upload.
- Simulasi database besar (1 juta baris).
- Kalau backend crash, frontend harus tahu dan memberi tahu user dengan jelas (bukan freeze).

**D3. Error Logging & Monitoring**
- Semua error tercatat di log.
- Dashboard menampilkan jumlah error dalam 24 jam terakhir.
- User bisa kirim log error ke Engineer untuk dianalisis.

---

### Pilar E: Dashboard Awal & Onboarding (Credit Berjalan)

**E1. Layar Login**
- Email + Password (atau magic link).
- Opsi "Ingat saya" untuk melewati login berikutnya.
- Register untuk user baru.

**E2. Dashboard Awal (Setelah Login)**
- Info sistem real-time: Kernel, AI Provider, RAG, Memory, Engineer, Backup, Budget.
- Tombol aksi: 🎬 Tentang MAMET OS, 🚀 Masuk ke 3 Kolom, ⚙️ Pengaturan, 🚪 Keluar.

**E3. Credit Berjalan (Tentang MAMET OS)**
- Layar hitam penuh, teks naik dari bawah ke atas.
- Konten: Filosofi → Tutorial 3 Kolom → Tips → Pesan Warisan.
- Tombol "Lewati" untuk langsung masuk.
- Narasi disimpan di file terpisah (`assets/credit.txt`) agar mudah diedit.

**E4. Adaptasi Berdasarkan Pengguna**
- Power user: Dashboard bisa dilewati (langsung 3 kolom).
- User baru: Dashboard selalu muncul dengan penjelasan.
- User bisa pilih mode: [Expert] [Standard] di Settings.

---

## Spesifikasi Detail Dashboard Awal & Credit Berjalan

### Alur Pengguna

```
User membuka MAMET OS
        │
        ▼
┌─────────────────────┐
│   LAYAR LOGIN       │
│                     │
│  Email: [________]  │
│  Password: [_____]  │
│                     │
│  [Masuk] [Daftar]   │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────────────────────────┐
│           DASHBOARD AWAL                      │
│                                              │
│  "Selamat datang, [Nama User]."              │
│                                              │
│  ┌──────────── STATUS SISTEM ────────────┐  │
│  │ Kernel       : ✅ Tersambung          │  │
│  │ AI Provider  : ✅ OpenRouter aktif    │  │
│  │ RAG          : 📊 12 dokumen, 85 chk │  │
│  │ User Memory  : 🧠 34 fakta           │  │
│  │ Engineer     : 🔧 Siap               │  │
│  │ Backup       : 📦 5 backup           │  │
│  │ Budget       : 💰 Rp 2.500/100rb     │  │
│  └───────────────────────────────────────┘  │
│                                              │
│     [🎬 Tentang MAMET OS]                    │
│     [🚀 Masuk ke 3 Kolom]                    │
│     [⚙️ Pengaturan]    [🚪 Keluar]           │
└──────────────────────────────────────────────┘
          │
          ▼ (klik 🎬)
┌──────────────────────────────────────────────┐
│          CREDIT BERJALAN                     │
│          (layar hitam, teks naik)            │
│                                              │
│  Cerita filosofi + tutorial 3 kolom         │
│  + tips penggunaan + pesan warisan          │
│                                              │
│  [⏭️ Lewati]                                 │
└──────────────────────────────────────────────┘
          │
          ▼ (klik 🚀 atau selesai credit)
┌──────────────────────────────────────────────┐
│           3 KOLOM MAMET OS                   │
│           (seperti sekarang)                 │
└──────────────────────────────────────────────┘
```

### Contoh Narasi Credit Berjalan (Cerita + Tutorial)

```
MAMET OS lahir dari sebuah ide sederhana...

Bahwa teknologi seharusnya tidak hanya membantu,
tetapi juga mengingat.

Bahwa sebuah aplikasi tidak hanya menjawab pertanyaan,
tetapi juga tumbuh bersama pemiliknya.

Dan pada akhirnya,
bisa diwariskan kepada mereka yang kita cintai.

---

SEKARANG, BAGAIMANA CARA MENGGUNAKANNYA?

MAMET OS punya tiga ruang kerja.
Kami menyebutnya "Tiga Kolom".

🔍 Kolom Kiri: PENCARIAN CEPAT
Di sini kamu bisa mencari dokumen yang sudah kamu unggah.
Klik tombol Upload, masukkan file,
lalu ketik kata kunci untuk menemukan isinya.
Semakin banyak dokumen, semakin pintar pencariannya.

🤖 Kolom Tengah: ASISTEN PRIBADI
Ini adalah teman ngobrolmu.
Dia akan mengingat siapa kamu, apa yang kamu suka,
dan membantumu mencari informasi di internet.
Cukup ketik apa yang kamu pikirkan.

🔧 Kolom Kanan: ENGINEER
Ini adalah mekanik pribadi MAMET OS.
Dia bisa memperbaiki sistem, membuat fitur baru,
bahkan menulis kode untukmu.
Tapi tenang, dia tidak akan berbuat apa-apa
tanpa izinmu terlebih dahulu.

---

TIPS UNTUK KAMU

📎 Upload dokumen di Kolom Kiri,
lalu cari informasinya dengan kata kunci.

💬 Ngobrol santai di Kolom Tengah,
semakin sering ngobrol, semakin dia mengenalmu.

🛠️ Kalau ada yang rusak atau ingin sesuatu yang baru,
minta tolong ke Engineer di Kolom Kanan.

💰 Pantau biaya AI di tombol "Budget" di pojok kanan atas.
Kamu bisa atur batas maksimal biaya per bulan.

🔄 Kalau Engineer melakukan kesalahan,
kamu bisa kembalikan sistem ke kondisi sebelumnya
lewat fitur Rollback.

---

MAMET OS bukan sekadar aplikasi.
Ia adalah catatan perjalanan pikiranmu.

Setiap percakapan, setiap dokumen, setiap fakta
yang ia ingat tentangmu...

Akan terus hidup di sini.

Untukmu.
Untuk mereka yang kamu tinggalkan.

---

Dibangun oleh [Nama Pembuat].
2026.
```

### Kebutuhan Teknis Dashboard & Login

| Komponen | Teknologi | Status |
|----------|-----------|--------|
| Layar Login | Svelte 5 + form | Belum dibuat |
| Dashboard Awal | Svelte 5 + API status | Belum dibuat |
| Credit Berjalan | Animasi CSS/JS + teks dari file `assets/credit.txt` | Belum dibuat |
| Endpoint status sistem | FastAPI `/api/status` | Belum dibuat |
| Auth (register/login) | SQLite + JWT | Belum dibuat |

---

## Yang Akan Dihadapi (Tantangan & Realita)

1. **Integrasi Python-Tauri tidak plug-and-play** — perlu lifecycle management, bundling Python runtime, port conflict handling. Saran: mulai mode developer dulu, bundling setelah stabil.
2. **Ketergantungan pada LLM cloud** — tanpa internet, Kolom 1 dan 2 lumpuh. Belum ada fallback model lokal yang setara. Solusi jangka panjang: Integrasi Ollama sebagai opsi offline.
3. **User Memory bisa jadi "tempat sampah pintar"** — fakta kontradiktif, ekstraksi tidak akurat. Butuh mekanisme forgetting & conflict resolution. Saran: mulai dengan fakta bertanggal kedaluwarsa.
4. **Engineer self-upgrade sangat berbahaya** — risiko kerusakan akumulatif, circular dependency. Saran: Engineer hanya mengubah folder proyek, bukan core MAMET OS.
5. **UI 3 kolom bisa membingungkan pengguna awam** — notifikasi tersebar, konteks berpindah-pindah. Saran: Dashboard awal + credit berjalan sebagai onboarding.
6. **Distribusi & update tidak otomatis** — perlu installer per OS, mekanisme auto-updater. Saran: mulai dari Windows, gunakan Tauri updater.

---

## Keamanan & Privasi

| Aspek | Kebijakan |
|-------|-----------|
| Autentikasi | Email + password (JWT, HTTP-only cookie) |
| API key | Terenkripsi per user (AES-256), tidak dibagi |
| Data user | Terisolasi penuh per email (Row-level security) |
| Izin Engineer | Semua perubahan wajib persetujuan user, dengan rollback |
| File system | Sandboxing ketat, path whitelist |
| Upload file | Scan ClamAV sebelum diproses |
| Database | SQLCipher untuk enkripsi SQLite |

---

## Strategi Penghematan Multi-Provider

**Hirarki Pemakaian (dari termurah):**
1. Template/Cached Response (GRATIS)
2. Ollama Lokal (GRATIS)
3. Embedding murah (~Rp 1/pencarian)
4. LLM Ringan (Mistral 7B) (~Rp 15/respons)
5. LLM Menengah (Llama 3 70B) (~Rp 150/respons)
6. LLM Kuat (GPT-4o) (~Rp 500/respons)

**Fitur Kontrol Budget:**
- Dashboard real-time pemakaian biaya
- Budget cap bulanan per provider (default Rp 100.000)
- Notifikasi 50%, 80%, 100%
- Mode Hemat (nonaktifkan LLM, hanya embedding + template)
- Persetujuan untuk panggilan LLM mahal

---

## Status Saat Ini (per 7 Juli 2026)
- Kernel Orchestrator: ✅
- RAG Engine + Upload: ✅
- Engineer Basic (read-only): ✅
- UI 3 Kolom (Svelte 5 + Tauri): ✅
- User Memory: ✅
- Multi-Provider AI: ✅
- Dua Sandbox + Rollback: ✅
- Engineer Write/Execute: ✅
- Budget Dashboard: ✅
- Login & Dashboard Awal: ⬜ (Spesifikasi v3)
- Credit Berjalan: ⬜ (Spesifikasi v3)
- Offline LLM (Ollama): ⬜ (Pilar A)
- Unit/Stress Test: ⬜ (Pilar D)

---

## Prinsip Utama
- **Fleksibel**: Komponen independen, plug-and-play (Lego)
- **Universal**: Berjalan di laptop, HP (via Termux), robot (Raspberry Pi)
- **Milik sendiri**: Email + API key pribadi, data terisolasi
- **Adaptif**: Sistem bisa mendeteksi dan beradaptasi dengan data baru
- **Hemat**: LLM hanya alat bantu terakhir, kernel berjalan simbolik
- **Self-Evolving**: Engineer bisa membantu membangun dan memperbaiki
```