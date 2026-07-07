```markdown
# MAMET OS v2.0 — Spesifikasi Teknis Lengkap (Personal Edition)

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
│                (Deployed via GitHub → Vercel)                 │
├──────────────────────────────────────────────────────────────┤
│          [Login: Email + API Key OpenRouter Pribadi]          │
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

## Spesifikasi Detail Fase 2

### A. User Memory (SQLite) — Ekstraksi Fakta & Forgetting

**Tujuan:** MAMET OS mengenal user secara personal, menyimpan fakta, dan bisa melupakan informasi usang.

**Database:**
- SQLite lokal di `~/.mamet/{email}/memory.db`
- Tabel `facts`: `id, fact, source, confidence, created_at, expires_at, is_active`
- Tabel `preferences`: `key, value, updated_at`
- Tabel `conversations`: `id, column, message, response, timestamp`
- **Multi-identitas:** Ganti email login = ganti folder memory.db

**Ekstraksi Fakta:**
- Setiap selesai percakapan di Kolom 2, LLM (provider aktif) diminta mengekstrak fakta baru tentang user (nama, pekerjaan, preferensi, dll.) dengan confidence score (0.0 - 1.0).
- Fakta disimpan ke tabel `facts` dengan `confidence` hasil ekstraksi.
- Fakta confidence rendah tetap disimpan, tapi tidak digunakan untuk respons otomatis.

**Forgetting:**
- Fakta dengan `expires_at` yang sudah lewat akan dihapus otomatis oleh job harian.
- Fakta kontradiktif (confidence < threshold) ditandai `is_active=false`.
- User bisa menghapus fakta manual dari UI Settings.

**Integrasi:**
- Evidence Collector akan mengecek `_check_user_memory()` sebelum ke RAG.
- Kolom 2 menampilkan fakta yang diingat jika user bertanya "apa yang kamu tahu tentang saya?".

**Implementasi File:**
- `backend/memory/user_memory.py` — class `UserMemory`
- `backend/memory/fact_extractor.py` — panggil LLM untuk ekstraksi fakta

---

### B. Multi-Provider AI Abstraction

**Tujuan:** User bisa memilih dan mengganti provider AI dari UI, bertahap.

**Interface Standar:**
```python
class AIProvider(ABC):
    name: str
    def chat(self, messages: List[Dict], model: str) -> str
    def embed(self, texts: List[str]) -> List[List[float]]
```

**Provider yang Diimplementasikan Bertahap:**
1. OpenRouter (bungkus ke interface)
2. OpenAI
3. Grok
4. Gemini

**Konfigurasi:**
- Tabel `providers`: `name, api_key_encrypted, is_active, priority`
- Fallback otomatis jika provider gagal
- UI: halaman Settings untuk kelola provider

**Implementasi File:**
- `backend/ai/provider_router.py` — abstraction layer
- `backend/ai/providers/openrouter_provider.py`
- `backend/ai/providers/openai_provider.py`
- `backend/ai/providers/grok_provider.py`
- `backend/ai/providers/gemini_provider.py`

---

### C. Engineer Write/Execute + Dua Sandbox + Rollback (Langsung Lengkap)

**Tujuan:** Engineer bisa menulis dan mengeksekusi kode dengan aman tanpa over-engineering.

**Dua Sandbox:**
```
Folder Proyek MametOS/
├── workspace/        ← Sandbox A: Engineer bekerja bebas
├── review/           ← Sandbox B: Hasil direplikasi untuk review user
├── live/             ← Production: hanya di-update setelah approval
└── rollback/         ← Backup sebelum setiap perubahan
```

**Alur Kerja:**
1. User minta perubahan → Engineer kerjakan di `workspace/`
2. Selesai → hasil dicopy ke `review/`, diff ditampilkan ke user
3. User review dan test di `review/`
4. User approve → `live/` di-update, backup disimpan di `rollback/` (zip dengan timestamp)
5. User tolak → `workspace/` dikosongkan, `review/` dihapus

**Rollback:**
- Setiap kali `live/` akan diubah, folder `live/` di-zip dan disimpan di `rollback/` dengan nama `backup_YYYYMMDD_HHMMSS.zip`
- User bisa restore kapan saja dari UI Engineer (pilih file zip, klik "Rollback")

**Safety Guard yang Ada:**
- Semua tindakan destructive (write, delete, execute) wajib menampilkan diff dan minta persetujuan eksplisit
- Audit log append-only mencatat setiap perubahan
- Path whitelist + no-exec

**Implementasi File:**
- `backend/engineer/sandbox.py` — mengelola workspace, review, live, rollback
- `backend/engineer/executor.py` — menjalankan command dengan safety guard (sudah ada, ditingkatkan)
- UI Kolom 3: tombol "Review", "Approve", "Rollback"

---

### D. Budget Control Dashboard

**Tujuan:** User bisa memantau dan membatasi biaya AI.

**Pencatatan:**
- Setiap panggilan LLM/Embedding dicatat ke SQLite tabel `usage_logs`:
  `provider, model, tokens_in, tokens_out, cost, timestamp`
- Cost dihitung berdasarkan pricing masing-masing provider

**Dashboard UI:**
- Menampilkan biaya: hari ini, minggu ini, bulan ini
- Per provider (OpenRouter, OpenAI, Grok, Gemini)
- Progress bar terhadap budget cap bulanan

**Budget Cap:**
- User bisa set budget cap per provider (default Rp 100.000/bulan)
- Jika cap tercapai, provider otomatis dinonaktifkan
- Notifikasi di UI saat mencapai 50%, 80%, 100% budget

**Implementasi File:**
- `backend/ai/usage_tracker.py` — mencatat setiap panggilan
- Frontend: komponen `BudgetDashboard.tsx`

---

## API Key Per User (Lego Credential)

- Setiap user login dengan email
- API key untuk setiap provider disimpan terenkripsi (AES-256) di SQLite
- Terisolasi penuh: user A tidak bisa pakai key user B
- User bisa mengelola key dari UI Settings

---

## Deployment & Hosting

| Aspek | Keputusan |
|-------|-----------|
| Platform | **Desktop app** via Tauri + Svelte 5 (web mode Next.js untuk development) |
| Repository | GitHub |
| Hosting (dev) | Vercel (auto-deploy dari GitHub) |
| Database | SQLite + ChromaDB (lokal) |
| Debugging | Browser DevTools + Vercel logs + Sentry |
| Packaging | .exe (Windows) via PyInstaller + Tauri bundler |

---

## Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Frontend | Tauri + Svelte 5 + TailwindCSS + shadcn/ui (Next.js untuk development) |
| Database | SQLite + ChromaDB |
| AI | OpenRouter, OpenAI, Grok, Gemini (via abstraction layer) |
| Auth | Email + password (JWT), API key terenkripsi per user |
| Packaging | .exe (Windows) via PyInstaller + Tauri bundler |

---

## Arsitektur Lego — Standar Interface

Setiap modul mengikuti interface standar agar plug-and-play:
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class LegoModule(ABC):
    """Interface standar untuk semua modul MAMET OS."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nama unik modul."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versi modul."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """Modul lain yang diperlukan."""
        return []
    
    @abstractmethod
    def can_handle(self, input_data: Dict[str, Any]) -> bool:
        """Apakah modul ini bisa menangani input?"""
        pass
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Proses utama modul."""
        pass
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validasi output."""
        return True
    
    def rollback(self) -> None:
        """Kembalikan state jika gagal."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Status modul saat ini."""
        return {"name": self.name, "version": self.version, "active": True}
```

---

## Rencana Pengembangan

### Fase 0: Fondasi + Engineer Basic ✅ (Selesai)
### Fase 1: Kolom 1 - Pencarian Cepat ✅ (Selesai)
### Fase 2: User Memory + Multi-Provider AI + Sandbox Ganda (Target berikutnya)
- A. User Memory (SQLite) dengan ekstraksi fakta & forgetting
- B. Multi-Provider AI Abstraction (OpenRouter, OpenAI, Grok, Gemini)
- C. Engineer Write/Execute + Dua Sandbox + Rollback
- D. Budget Control Dashboard

### Fase 3: Sub-agent + Database Detector
### Fase 4: Ekspansi Lego + Legacy Mode

---

## Yang Akan Dihadapi (Tantangan & Realita)

1. **Integrasi Python-Tauri tidak plug-and-play** — perlu lifecycle management, bundling Python runtime, port conflict handling. Saran: mulai mode developer dulu, bundling setelah stabil.
2. **Ketergantungan pada LLM cloud** — tanpa internet, Kolom 1 dan 2 lumpuh. Belum ada fallback model lokal yang setara. Solusi jangka panjang: Integrasi Ollama sebagai opsi offline.
3. **User Memory bisa jadi "tempat sampah pintar"** — fakta kontradiktif, ekstraksi tidak akurat. Butuh mekanisme forgetting & conflict resolution. Saran: mulai dengan fakta bertanggal kedaluwarsa.
4. **Engineer self-upgrade sangat berbahaya** — risiko kerusakan akumulatif, circular dependency. Saran: Engineer hanya mengubah folder proyek, bukan core MAMET OS.
5. **UI 3 kolom bisa membingungkan pengguna awam** — notifikasi tersebar, konteks berpindah-pindah. Saran: sediakan mode 1 kolom sebagai default.
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
2. Embedding murah (~Rp 1/pencarian)
3. LLM Ringan (Mistral 7B) (~Rp 15/respons)
4. LLM Menengah (Llama 3 70B) (~Rp 150/respons)
5. LLM Kuat (GPT-4o) (~Rp 500/respons)

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
- UI 3 Kolom (Next.js): ✅
- User Memory: ⬜ (Fase 2 berikutnya)
- Multi-Provider AI: ⬜ (Fase 2 berikutnya)
- Dua Sandbox + Rollback: ⬜ (Fase 2 berikutnya)
- Engineer Write/Execute: ⬜ (Fase 2 berikutnya)
- Budget Dashboard: ⬜ (Fase 2 berikutnya)

---

## Prinsip Utama
- **Fleksibel**: Komponen independen, plug-and-play (Lego)
- **Universal**: Berjalan di laptop, HP (via Termux), robot (Raspberry Pi)
- **Milik sendiri**: Email + API key pribadi, data terisolasi
- **Adaptif**: Sistem bisa mendeteksi dan beradaptasi dengan data baru
- **Hemat**: LLM hanya alat bantu terakhir, kernel berjalan simbolik
- **Self-Evolving**: Engineer bisa membantu membangun dan memperbaiki
```