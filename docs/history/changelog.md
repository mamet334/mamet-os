# MAMET OS - Sejarah Pembuatan Fondasi & Changelog

Folder dan dokumen ini didedikasikan untuk melacak rekam jejak pembuatan dasar fondasi (Kernel) MAMET OS beserta perbaikan bug dan peningkatan sistem (upgrade). 

Ini adalah bagian dari prinsip *Self-Evolving*, di mana setiap perubahan struktural yang dibuat oleh Engineer dicatat secara sistematis.

---

## [v3.1.0-alpha.1] - 2026-07-09

### 🏥 Implementasi Pilar G (Health Monitoring & Auto-Recovery)

**1. Backup Eksternal (Flashdisk) & Pemulihan (G1 & G4)**
- **File Dibuat**: `backend/engineer/disk_detector.py`
- Menambahkan modul `DiskDetector` untuk deteksi otomatis *removable drive* dan mengeksekusi sinkronisasi dengan `robocopy`/`rsync`.
- Mengubah fungsi `rollback_to()` di `sandbox.py` agar mengekstrak *zip* `auto_backup_` langsung ke dalam lintasan `~/.mamet/`, menjadikan tombol *Rollback* Svelte berfungsi ganda untuk sistem kode maupun *database* tanpa konflik penimpaan file proyek.

**2. Integritas Database & Auto-Backup Harian (G2 & G3)**
- **File Dimodifikasi**: `backend/memory/user_memory.py`, `backend/orchestrator/main_orchestrator.py`
- Menyisipkan `PRAGMA integrity_check;` yang dieksekusi asinkron saat proses *boot* Kernel.
- Membuat *Background Task* (`_idle_checker`) di *Orchestrator* untuk mendeteksi status diam selama 5 menit. Saat terpenuhi, sistem akan membuat cadangan otomatis (*auto-backup*) dari pangkalan data memori ke dalam format `auto_backup_YYYYMMDD_HHMMSS.zip`.

**3. Penambahan Antarmuka Health Monitoring (Frontend)**
- **File Dimodifikasi**: `desktop/src/routes/workspace/+page.svelte`
- Menyuntikkan blok *UI Health Monitoring & Recovery* pada area *Dashboard Command Center*. Pengguna kini bisa secara *real-time* memonitor kesehatan (Sehat/Rusak) dari *Database*, mengeksekusi pencadangan ke *Flashdisk*, serta melakukan pemulihan secara 1-Klik dari daftar log *Rollback*.

### 🛡️ Audit Fungsionalitas Pilar G (Backend)

**1. Penambalan Bug Unicode (UnicodeEncodeError) pada Console Windows**
- **File Dimodifikasi**: `backend/ai/provider_router.py`
- **Detail Perbaikan**: Saat eksekusi `audit_pilar_g.py`, ditemukan error kritis 500 pada `/api/status` akibat enkoding `❌` dan `✅` di *logging server* yang tidak didukung *charmap* Windows. 
- **Resolusi**: Semua emoji pada `ProviderRouter` telah dikonversi ke teks standar (`[ERROR]` dan `[OK]`), memastikan API berjalan stabil 100%.

### ☁️ Implementasi Pilar F (Cloud Sync & Legacy Wizard)

**1. Modul Google Drive & Endpoint Warisan Digital (F1 & F2)**
- **File Dibuat/Dimodifikasi**: `backend/engineer/google_drive_sync.py`, `backend/main.py`
- Merancang kelas `GoogleDriveSync` berbasis *OAuth2 InstalledAppFlow* untuk memfasilitasi integrasi *Google Drive* yang bersih tanpa memaksa pengguna mengonfigurasi *Google Cloud Console* manual. Token disimpan terisolasi di memori per-email (`~/.mamet/{email}/token.json`).
- Membuka endpoint kontrol `/api/legacy/activate` (pemicu proses *login browser*) dan `/api/legacy/status` (pelacak metrik kesuksesan sinkronisasi awan/cloud).

**2. Integrasi Auto-Backup Harian (Simbiosis F & G)**
- **File Dimodifikasi**: `backend/engineer/sandbox.py`
- Menyuntikkan jembatan pemanggilan `.sync_to_cloud()` tepat di penghujung eksekusi `daily_auto_backup()`. Setiap ZIP pangkalan data memori (Pilar G) kini diamankan ganda ke Google Drive pengguna secara mutlak.

**3. Antarmuka Legacy Wizard (Svelte)**
- **File Dimodifikasi**: `desktop/src/routes/workspace/+page.svelte`
- Menyematkan seksi baru *Cloud Sync & Legacy Wizard* di *Dashboard Command Center*. Panel interaktif menyediakan pelacakan waktu nyata dari sinkronisasi awan, sekaligus gerbang utama tombol **🛡️ Aktifkan Warisan Digital**.

**4. Audit & Validasi Fungsional (Pilar F)**
- **Eksekusi**: Meluncurkan pengujian mendalam via skrip `audit_pilar_f.py`.
- **Hasil**: Sistem terbukti tangguh `100%`. Logika pendeteksian titik buta (*fail-safe*) untuk status *unconfigured* serta pembacaan berkas autentikasi OAuth Google berjalan murni dan mulus pada *FastAPI Endpoint* tanpa secercah *error* sekalipun.

---

## [v3.0.0-alpha.1] - 2026-07-08

### 🚀 Implementasi Spesifikasi V3 (Pilar E: Onboarding & UI)

**1. Sistem Autentikasi (Backend)**
- **File Dibuat/Dimodifikasi**: `backend/auth/auth_handler.py`, `backend/main.py`
- Membangun modul *handler* menggunakan **SQLite**, enkripsi sandi **bcrypt**, dan **JWT (JSON Web Token)**.
- Mengekspos endpoint baru `/api/register` dan `/api/login` untuk mengunci dan memisahkan identitas pengguna secara terisolasi.
- Menambahkan endpoint `/api/status` untuk menyuplai data metrik kesehatan sistem secara *real-time* ke *dashboard* Svelte.

**2. Layar Login & Dashboard Awal (Frontend)**
- **File Dibuat**: `desktop/src/routes/+page.svelte`, `desktop/src/routes/dashboard/+page.svelte`
- Merestrukturisasi *routing* SvelteKit. Halaman utama (root) kini disetel sebagai **Layar Login**.
- Halaman **Dashboard Awal** dibuat untuk menampilkan status sistem (Koneksi Kernel, AI Provider, Dokumen RAG, Fakta Memori, dan status Budget AI).
- Mengamankan aliran sesi dengan memanfaatkan `localStorage` untuk menampung JWT.

**3. Credit Berjalan (Onboarding Dramatis)**
- **File Dibuat**: `desktop/src/routes/credit/+page.svelte`, `desktop/static/credit.txt`
- Mengimplementasikan animasi teks bergulir (*cinematic text crawl*) menggunakan transisi murni Svelte dan CSS.
- Narasi (filosofi, tutorial 3 Kolom, pesan warisan) ditarik dari file statis eksternal (`credit.txt`) sehingga pengguna dapat mengubah narasinya sendiri tanpa memodifikasi kode UI.
- Aplikasi ruang kerja "3 Kolom" dipindahkan dengan aman dari direktori utama (root) menuju `desktop/src/routes/workspace/+page.svelte`.

**4. Perombakan Total Desain UI/UX (Level 4 - Glassmorphism Premium)**
- **File Dimodifikasi**: `desktop/tailwind.config.js`, `desktop/src/app.css`, `desktop/src/app.html`, seluruh `+page.svelte`
- **Konfigurasi Global**: Menyuntikkan Google Fonts (Inter & JetBrains Mono) pada level HTML. Memperluas konfigurasi Tailwind dengan palet warna khusus (`mamet-cyan`, `mamet-purple`, `mamet-amber`), animasi `fade-in`, dan utilitas kaca kustom (Glass).
- **Pembuatan Utility Classes**: Mendefinisikan `@layer components` di `app.css` untuk kelas `.glass-panel`, `.glass-input`, `.glass-btn-primary`, dan `.cyan-glow`.
- **Implementasi Estetika Premium**: Mengganti palet generik `bg-gray-900` dan `bg-gray-800` menjadi latar belakang transparan (memanfaatkan *radial gradient* tubuh dokumen), memberlakukan blur kaca mendalam (`backdrop-blur-xl`), efek pantulan cahaya neon (Cyan `#00dbe9`), serta *custom scrollbar*.
- **Penyempurnaan Ruang Kerja (Workspace)**: Gelembung obrolan (*chat bubbles*) kini menggunakan desain semi-transparan bergaya holografik. Area input juga didesain ulang agar lebih minimalis dengan fokus nyala (*ring glow*) saat diketik.

### 🛡️ Audit Fungsionalitas Pilar E (Backend)

**1. Temuan Masalah pada Endpoint Status (`/api/status`)**
- Saat pengujian (`audit_pilar_e.py`), endpoint utama pendaftaran dan login berhasil memproduksi dan memvalidasi JWT. Namun, panggilan ke `/api/status` memicu *crash* internal (Status 500) dengan pesan: `ModuleNotFoundError: No module named 'config'`.
- **Akar Masalah**: *Backend* berusaha mengimpor `ProviderConfig` dari lintasan yang tidak ada di dalam arsitektur sistem saat membaca status *AI Provider* yang aktif.

**2. Perbaikan Kode (Routing API)**
- **File Dimodifikasi**: `backend/main.py`
- Menghapus logika pemanggilan modul `config` fiktif.
- Menggantinya dengan memanggil `ProviderRouter` secara langsung dari `ai.provider_router` untuk mengekstrak nama model bahasa aktif.
- **Kode yang digunakan**:
  ```python
  from ai.provider_router import ProviderRouter
  router = ProviderRouter(email)
  provider = router.get_active_provider()
  provider_name = provider.name if provider else "Tidak ada"
  ```
- **Status Akhir**: Metrik *Dashboard* (Kernel, Dokumen RAG, Fakta Memori, *Budget* AI, dan Status *Backup*) berhasil ditarik sempurna dengan respons kode 200 OK. Aplikasi 100% aman memblokir akses pengguna tak berizin (401 Unauthorized) pada sesi login.

### 🛡️ Temuan Tambahan (Frontend Svelte)

**1. Bug Layar Kosong (Blank Screen) Pasca Login**
- Saat uji coba secara nyata melalui peramban (*browser*), setelah pengguna berhasil login, *Dashboard Awal* gagal dimuat (layar kosong) akibat galat pada sisi klien (*Client-side Error*): `TypeError: can't access property "toLocaleString", $.get(...).budget.total_cost is undefined`.
- **Akar Masalah**: Ketidakcocokan antara nama variabel yang dikirimkan oleh API FastAPI dengan yang dibaca oleh *Frontend* Svelte. Svelte berusaha memanggil `total_cost` dan `monthly_cap`, padahal respons `UsageTracker` dari Backend secara aktual mengirimkan data dengan skema `total_budget_used` dan `total_budget_cap`.

**2. Resolusi Kode (Svelte UI)**
- **File Dimodifikasi**: `desktop/src/routes/dashboard/+page.svelte`
- Menyesuaikan penamaan variabel pada blok render UI agar selaras dengan skema JSON dari API (`total_budget_used` dan `total_budget_cap`).
- Menyuntikkan lapisan keselamatan tambahan berupa operator validasi absolut (`!== undefined`) sebelum mengeksekusi format angka `toLocaleString('id-ID')`. Upaya pencegahan ini bertujuan meredam potensi UI lumpuh seandainya *Backend* mengalami kegagalan transmisi nominal di masa depan.

**3. Pembekuan Akhir Animasi Credit Berjalan**
- **File Dimodifikasi**: `desktop/src/routes/credit/+page.svelte`
- Mengembalikan durasi animasi (*crawl*) ke statis (`40s`) agar tidak terasa terlalu lambat.
- Mengubah algoritma *keyframes* CSS agar teks tidak bergulir hingga hilang (`opacity: 0` pada `-200vh`). Animasi kini dikunci (`forwards`) untuk berhenti secara permanen menggunakan formula matematis absolut: `transform: translateY(calc(-100% + 100vh))`. Dipadukan dengan bantalan bawah (*padding-bottom*) sebesar `50vh`, teks akan secara mutlak dan sempurna terkunci tepat di tengah layar berapapun tinggi halamannya.
- **Penyelesaian Bug Pemotongan Teks**: Menambahkan utilitas `items-start` pada *parent div* Flexbox (Tailwind). Sebelumnya, teks terpotong sangat jauh dari akhir karena tinggi komponen dipaksa ditarik meregang (*stretch*) menyamai tinggi layar induk (`h-full`), sehingga persentase perhitungan pergerakan 100% meleset. Teks sekarang berhasil digulir dari awal sampai kalimat paling akhir.

**4. Refaktor Antarmuka Workspace (Panel Sidebar & Tampilan 1-Kolom)**
- **File Dimodifikasi**: `desktop/src/routes/workspace/+page.svelte`
- Menghapus tata letak *grid* 3-kolom simultan yang tadinya membuat layar terasa penuh sesak.
- Mengimplementasikan navigasi **Panel Samping (Sidebar)** permanen di sebelah kiri yang menampung tombol pilihan untuk masuk ke masing-masing pilar: Pencarian Cepat, Asisten Pribadi, Engineer, dan Pengaturan.
- Panel *Dashboard/Settings* yang sebelumnya menggunakan *Overlay Modal* telah diintegrasikan langsung sebagai salah satu rute di kolom utama.
- Layar obrolan (*Chat Area*) kini memiliki **1 Kolom Penuh** (mengambil seluruh sisa ruang layar). Hal ini memberikan ruang baca dan penulisan (*textarea*) yang jauh lebih luas, lega, dan nyaman di mata pengguna.
- **Penyelesaian Bug (Stuck Loading Tab Pengaturan):** Memperbaiki respons skema JSON pada modul *budget* di Svelte. Sebelumnya tab Pengaturan macet akibat mencoba membaca properti `tokens_in` yang tidak disediakan oleh API `get_budget_status()`. Variabel tersebut telah diubah menjadi kalkulasi `remaining` dan `status` sesuai respons API.

---

## [v0.6.0] - 2026-07-08

### 🚀 Integrasi Fase 4 (Ekspansi Lego & Modul Dinamis)

**1. Arsitektur Dynamic Loading (Lego Registry)**
- **File Dimodifikasi**: `backend/lego_modules/lego_registry.py`
- Merombak `LegoRegistry` dengan menambahkan metode `load_plugins()`. Menggunakan modul bawaan Python (`importlib.util` dan `inspect`) untuk memindai direktori plugin secara dinamis, mengekstrak kelas yang merupakan turunan dari `LegoModule`, lalu menginisialisasi dan mendaftarkannya secara otomatis tanpa perlu registrasi manual (*hardcode*).

**2. Pengikatan Pemuatan Modul di Inti Sistem**
- **File Dimodifikasi**: `backend/orchestrator/evidence_collector.py`
- Menanamkan pemanggilan `load_plugins()` saat `LegoRegistry` diinisialisasi dalam `EvidenceCollector`. Direktori target disetel secara absolut ke `backend/custom_modules/`. Dengan demikian, semua modul kustom langsung aktif dan dapat diakses oleh orkestrator.

**3. Pembuatan Skrip Uji Coba & Modul Bukti Konsep (PoC)**
- **File Dibuat**: `backend/custom_modules/hello_lego.py` & `backend/test_lego.py`
- Membuat modul *dummy* `HelloLego` untuk memverifikasi bahwa registrasi dinamis berfungsi sempurna. Pengujian terbukti berhasil mendeteksi dan memuat modul tanpa error, menegaskan kapabilitas penuh dari arsitektur *Plug-and-Play*.

### 🛡️ Audit Keseluruhan (End-to-End System Audit)

**1. Temuan Masalah pada Skrip Audit (`deep_audit.py`)**
- Saat melakukan audit ulang keseluruhan pasca Ekspansi Lego, ditemukan pesan kegagalan palsu (*false negatives*) pada dua komponen:
  1. **Planning Engine**: Dilaporkan "Langkah yang dihasilkan tidak sesuai".
  2. **Database Agent**: Dilaporkan "Gagal menangani file palsu".

**2. Perbaikan Skrip Audit Kedaluwarsa**
- **File Dimodifikasi**: `deep_audit.py`
- **Detail Perbaikan**:
  - *Planning Engine*: Mengubah parameter ekspektasi langkah Kolom 3 dari `"check_engineer"` menjadi `"check_rag_knowledge"`. Hal ini disesuaikan karena arsitektur *Planning Engine* yang baru telah di-*update* untuk menggunakan `check_rag_knowledge` sebelum memanggil Engineer.
  - *Database Agent*: Menambahkan kondisi untuk menerima tangkapan *error* `"tidak ditemukan"` pada hasil respons saat mendeteksi *file path* palsu. *Database Agent* sebenarnya berfungsi sempurna mencegah file palsu dengan melempar `FileNotFoundError`, namun skrip audit sebelumnya terlalu kaku dan hanya mencari kalimat spesifik `"tidak dikenali"`.
- **Status Akhir**: Skrip audit berhasil berjalan 100% tanpa menemukan *error* pada alur *Planning*, *Decision*, *Evidence Collection*, *Agents*, maupun *Lego Registry*. Sistem dikonfirmasi sehat.

---

## [v0.5.0] - 2026-07-07

### 🚀 Integrasi Fase 3 (Sub-Agent & Database Detector)

**1. Pemasangan Agent Selector (UI Svelte)**
- **File Dimodifikasi**: `desktop/src/routes/+page.svelte`
- Merealisasikan spesifikasi "Pemilihan Agen Manual" dengan menambahkan menu *dropdown* di antarmuka Kolom 2. Pengguna kini dapat memilih agen spesifik secara eksplisit: *Database Explorer*, *File Analysis*, *Web Search*, atau *Research*.
- Meneruskan data agen yang dipilih (`selectedAgent`) ke dalam *payload* komunikasi ke *backend* via `POST /api/process`.

**2. Penyesuaian Endpoint Komunikasi API**
- **File Dimodifikasi**: `backend/main.py`
- Menambahkan properti opsional `agent: Optional[str] = None` ke dalam *schema* `ChatRequest` FastAPI agar dapat menerima sinyal pemilihan agen dari antarmuka Svelte.

**3. Injeksi Agen ke dalam Planning Engine**
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- Memodifikasi siklus *Orchestrator* agar menangkap parameter `agent` dari UI.
- *Orchestrator* kini secara otomatis menyuntikkan nama agen ke dalam memori perencana (`plan["sub_agent"] = agent`) dan menambahkan langkah prosedural `"invoke_sub_agent"` tanpa memaksa pengguna mengetik instruksi agen secara manual di kolom *chat*.

**4. Audit Arsitektur (End-to-End Simulation)**
- **Artefak**: `audit_report_phase3.md` & `test_phase3.py`
- Melakukan verifikasi lintasan data (*git diff*) untuk membuktikan *state binding* (`bind:value={selectedAgent}`) dari UI Svelte benar-benar terhubung secara absolut ke interceptor parameter pada *Main Orchestrator*.
- Mengeksekusi simulasi buta (tanpa UI) yang membuktikan bahwa `DatabaseDetector` dan `SchemaMapper` berfungsi penuh; sukses mengklasifikasikan file, mengiris 5 baris sampel data pertama, dan membungkusnya sebagai JSON di dalam *Prompt* yang dieksekusi oleh Agen.

---

## [v0.4.7] - 2026-07-07

### 🔗 Integrasi UI Fase 2 (Command Center & Rollback)

**1. Ekstensi Endpoint FastAPI (Backend)**
- **File Dimodifikasi**: `backend/main.py`
- Menghubungkan fitur tersembunyi Fase 2 ke antarmuka dengan menambahkan tiga *endpoint* krusial:
  - `GET /api/budget`: Menarik data limit dan pemakaian AI dari `UsageTracker` (SQLite).
  - `GET /api/backups`: Menarik riwayat pencadangan (*backup* zip) dari `EngineerSandbox`.
  - `POST /api/rollback`: Mengeksekusi penimpaan sistem otomatis dari riwayat *backup* jika terjadi kerusakan.

**2. Pembangunan Command Center Panel (UI Svelte)**
- **File Dimodifikasi**: `desktop/src/routes/+page.svelte`
- Mendesain layar modal interaktif (dengan *glassmorphism* dan mode gelap premium) yang diakses melalui tombol "Dashboard Panel".
- **Seksi Budget**: Menampilkan visualisasi persentase pengeluaran API, daftar limit, status pemakaian (Aktif/Habis), serta riwayat token masuk/keluar per *AI Provider*.
- **Seksi Rollback**: Menampilkan daftar jejak perubahan (versi ZIP) yang diciptakan otomatis oleh sistem perlindungan Sandbox, dilengkapi tombol "🔄 Rollback" untuk memulihkan sistem secara instan.

**3. Resolusi Svelte TypeScript**
- Memperbaiki peringatan tipe variabel tak dikenal (`unknown type`) pada iterasi antarmuka Svelte menggunakan injeksi _type assertions_ mutakhir (`{@const d = data as any}`).
- Melalui *deep execution audit*, memastikan kode mendapatkan `0 errors` saat tahap verifikasi `npm run check`.

---

## [v0.4.6] - 2026-07-07

### 🚀 Transisi UI Desktop (Svelte 5 + Tauri)

**1. Inisialisasi Ekosistem Desktop (`desktop/`)**
- Membangun fondasi frontend baru menggunakan **Svelte 5** dan **Tauri 2.0** sebagai pengganti kerangka kerja *Next.js* lama yang disiapkan khusus untuk menjadi aplikasi mandiri berkinerja tinggi (*native window*).
- Menambahkan **TailwindCSS v3** dan desain kustom mode gelap premium untuk antarmuka tiga kolom.

**2. Pembaruan Logika 3 Kolom & State Management**
- **File Dimodifikasi**: `desktop/src/routes/+page.svelte`
- Sepenuhnya menerjemahkan UI lama ke ekosistem Svelte 5, menggunakan fitur mutakhir `$state()` (Runes) untuk penanganan UI yang instan. 
- Menjaga utuh logika jembatan komunikasi (tombol setujui/tolak) yang dikirim ke *backend* beserta *API Key*.

**3. Penambahan Endpoint Upload di FastAPI**
- **File Dimodifikasi**: `backend/main.py`
- Menemukan dan memperbaiki *missing link* di mana *backend* sebelumnya tidak memiliki penerima unggahan file.
- Menambahkan rute `@app.post("/api/upload")` (menggunakan modul `python-multipart` & `UploadFile`) yang langsung menyambungkan dokumen yang diunggah dari antarmuka Svelte 5 ke `RAGEngine` Python untuk di-*chunk* dan disimpan.

**4. Validasi Komunikasi Endpoint**
- **File Dibuat**: `test_api_endpoints.py`
- Menjalankan uji tembak simulasi HTTP *TestClient* untuk membuktikan *pipeline* obrolan (`/api/process`) dan unggah dokumen (`/api/upload`) dari sisi UI Svelte ke *Kernel FastAPI* bekerja selaras tanpa *error*.

---

## [v0.4.5] - 2026-07-07

### 🛠️ Resolusi Hutang Teknis (Architectural Fixes)

**1. Revitalisasi Eksekusi Sub-Agent (Ghost Agents Fixed)**
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- **Detail Perbaikan**: Merombak logika aksi `"need_agent"`. Orkestrator kini secara dinamis menginisialisasi kelas agen yang relevan (misal: `DatabaseExplorerAgent`, `WebSearchAgent`), menyuntikkan *Provider Router* AI, lalu mengeksekusi metode `process()`. Respons nyata dari agen sekarang berhasil diteruskan ke pengguna.

**2. Perbaikan Antarmuka Persetujuan (UI Approval Fixed)**
- **File Dimodifikasi**: `frontend/src/app/page.tsx`
- **Detail Perbaikan**: Logika tombol persetujuan UI telah dibuat dinamis. Kini tombol secara cerdas mengekstrak `task_id` dari payload *backend* (contoh: 4921) dan mengirimkan *command* presisi `"setujui 4921"`. Alur eksekusi perlindungan *Sandbox Engineer* kembali berjalan normal dan bebas dari *race condition*.

**3. Pengkabelan Ulang Frontend-Backend (Frontend Disconnect Fixed)**
- **File Dimodifikasi**: `frontend/src/app/page.tsx`
- **Detail Perbaikan**: Memindahkan target *fetch* komunikasi *chat* dari rute statis bawaan Next.js (`/api/chat`) ke *endpoint* mandiri FastAPI (`http://127.0.0.1:8000/api/process`). Jembatan komunikasi *real-time* dan transparan antara UI dengan Kernel MAMET OS akhirnya terwujud penuh.

---

## [v0.4.4] - 2026-07-07

### ⚠️ Identifikasi Hutang Teknis (Architectural Blind Spots)

**1. Penemuan Cacat pada Eksekusi Sub-Agent (Ghost Agents)**
- **Detail**: Saat orkestrator memutuskan `need_agent`, eksekusi berhenti pada pengembalian teks *"[AGENT] Agen akan dipanggil."* tanpa pernah benar-benar memanggil agen (seperti `FileAnalysisAgent` atau `DatabaseExplorerAgent`). Arsitektur agen Fase 3 saat ini masih "hantu" (pajangan) yang belum teraliri listrik eksekusi dari orkestrator utama.

**2. Kelumpuhan Antarmuka Persetujuan (Broken UI Approval)**
- **Detail**: Perbaikan konflik *race condition* (yang memerlukan `setujui <task_id>`) tidak diiringi dengan pembaruan *Frontend*. Akibatnya, tombol UI "✅ Setujui & Deploy" di Next.js masih mengirim teks statis `"setujui"`, menyebabkan seluruh alur eksekusi Engineer (Kolom 3) menjadi lumpuh karena ditolak oleh *Backend*.

**3. Isolasi Jalur Komunikasi UI (Frontend Disconnect)**
- **Detail**: Meskipun *FastAPI server* (`backend/main.py`) telah dibangun dengan matang di *localhost*, UI Next.js masih belum dihubungkan. UI masih menembak titik temu lamanya (`/api/chat` bawaan Next.js) sehingga *Backend* Python sepenuhnya terisolasi dari pengguna.

---

## [v0.4.3] - 2026-07-07

### 🛡️ Audit & Penambalan Sistem (System Audit)

**1. Penambalan Bug "UserMemory object has no attribute '_get_connection'"**
- **File Dimodifikasi**: `backend/memory/user_memory.py`
- **Detail Perbaikan**: 
  - Saat melakukan audit, ditemukan bahwa fungsi `_get_connection()` terhapus saat penerapan penambalan sebelumnya.
  - Mengembalikan struktur fungsi tersebut agar Mode WAL (Write-Ahead Logging) SQLite bisa berjalan sempurna tanpa mengganggu alur *Forgetting Mechanism* dan penulisan riwayat *chat*.

**2. Verifikasi 6 Penambalan Kritis (Lulus Audit 100%)**
- Telah dibuat dan dieksekusi skrip `test_6_patches.py` untuk mensimulasikan beban kerja:
  - Eksekusi *Race Condition* berhasil ditahan dengan sistem `task_id` unik.
  - *Storage Leak* berhasil dihentikan (folder hanya menyimpan tepat 5 file `.zip`).
  - *Data Sandbox* (Kolom 2) sukses merestorasi data CSV yang dirusak agen.
  - *Timer* waktu eksekusi telah berhasil muncul di setiap interaksi obrolan.

---

## [v0.4.2] - 2026-07-07

### 🚀 Peningkatan & Perbaikan Kritis (Production-Ready Fixes)

**1. FastAPI API Server (Jembatan Localhost)**
- **File Baru**: `backend/main.py`
- **Detail Perubahan**: 
  - Membangun *endpoint* HTTP menggunakan FastAPI (`/api/process`) untuk menjembatani komunikasi UI (Next.js) dengan Kernel MAMET OS.
  - Memungkinkan aplikasi diakses dari UI secara *real-time* via localhost tanpa kehilangan portabilitas.

**2. Penawar Database Locked (SQLite WAL Mode)**
- **File Dimodifikasi**: `backend/memory/user_memory.py`
- **Detail Perubahan**: 
  - Menolak transisi ke PostgreSQL demi menjaga filosofi portabilitas MAMET OS.
  - Mengaktifkan `PRAGMA journal_mode=WAL;` dan menyetel *timeout* pada koneksi SQLite. Hal ini mencegah *error "database is locked"* saat proses ekstraksi memori latar belakang dan pembacaan *chat* terjadi secara paralel.

**3. Resolusi Konflik Eksekusi Engineer (Race Condition)**
- **File Dimodifikasi**: `backend/engineer/engineer_main.py`
- **Detail Perubahan**: 
  - Mengubah `.pending_command` tunggal menjadi sistem penomoran *task_id* unik (misal: `.pending_4921`).
  - Mencegah perintah eksekusi tumpang tindih jika pengguna membuka banyak *tab* atau mengetik dengan sangat cepat.
  - Pengguna kini menyetujui menggunakan sintaks spesifik: `setujui 4921`.

**4. Penutupan Kebocoran Storage Sandbox (Auto-Cleanup)**
- **File Dimodifikasi**: `backend/engineer/sandbox.py`
- **Detail Perubahan**: 
  - Membuat fungsi `_cleanup_old_backups(keep=5)`.
  - Secara otomatis menghapus file `.zip` *rollback* yang paling usang, menjaga harddisk dari *storage leak* yang bisa membuat komputer penuh tanpa disadari.

**5. Transparansi Waktu Proses Kernel**
- **File Dimodifikasi**: `backend/orchestrator/main_orchestrator.py`
- **Detail Perubahan**: 
  - Menyisipkan fitur pelacakan waktu eksekusi (`time.time()`).
  - Menambahkan laporan `⏱️ [Waktu proses: X.XX detik]` di akhir setiap respons sistem, memberikan indikator jelas bagi pengguna saat menunggu proses (karena sistem belum menggunakan metode *Streaming*).

**6. Data Sandbox untuk Kolom 2**
- **File Baru**: `backend/memory/data_sandbox.py`
- **Detail Perubahan**: 
  - Membangun mekanisme *backup/restore* untuk melindungi data base (SQLite/CSV) pengguna pribadi saat Agen AI (Kolom 2) mencoba memodifikasi atau menghapus data.
  
---

## [v0.4.1] - 2026-07-07

### 🐛 Perbaikan Bug (Bug Fixes)

**1. Penyambungan Jalur Pipa Modul Lego ke Orkestrator Utama**
- **File Dimodifikasi**: `planning_engine.py`, `evidence_collector.py`, `decision_engine.py`
- **Detail Perbaikan**: 
  - **Identifikasi Bug**: Pada versi *v0.4.0*, kerangka kerja *LegoModule* dan *LegoRegistry* telah diciptakan, namun terjadi kebocoran arsitektur (*architectural gap*): *Registry* tersebut sama sekali tidak terhubung ke *Pipeline* pernapasan utama MAMET OS.
  - **Penyelesaian**:
    1. Menyisipkan langkah `"check_lego_modules"` ke dalam logika *Planner* untuk Kolom 2.
    2. Menginisialisasi `LegoRegistry` di dalam *Evidence Collector* dan menjalankan iterasi deteksi `can_handle()` ke setiap modul Lego yang terpasang setiap kali ada percakapan masuk.
    3. Memperbarui *Decision Engine* agar memberikan respons prioritas (*confidence 1.0*) jika suatu Modul Lego berhasil mengambil alih percakapan.
  - **Status**: Arsitektur Lego kini 100% *Plug-and-Play* tanpa memerlukan modifikasi *hardcode* (*bypass*) tambahan di *Main Orchestrator*.

---

## [v0.4.0] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Arsitektur Ekspansi Lego & Legacy Mode (Fase 4)**
- **Folder Baru**: `backend/lego_modules/`
- **File Dimodifikasi**: `backend/memory/user_memory.py`
- **Detail Perubahan**: 
  - **Lego Architecture**: Membuat standar *interface* `base_lego.py` (`LegoModule`) dan manajernya di `lego_registry.py`. Kini, MAMET OS resmi menjadi ekosistem terbuka di mana *user* (atau Engineer) bisa memasang modul custom (*IoT*, kontrol perangkat, API eksternal) semudah memasang balok Lego, tanpa harus merusak orkestrator inti.
  - **Legacy Mode (Warisan Digital)**: Membangun mekanisme pengunci memori (*Memory Lock*) di `user_memory.py`. Jika `legacy_mode` diaktifkan, sistem database fakta akan masuk ke mode *Read-Only*. Fakta tidak akan dihapus, diubah, maupun kedaluwarsa. Hebatnya lagi, *context builder* LLM akan berubah peran dari "Asisten Pribadi" menjadi "Representasi / Kloning" dari sang pemilik memori. Ini merealisasikan visi utama MAMET OS sebagai kapsul waktu/warisan digital.

---

## [v0.3.3] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Peningkatan FileAnalysisAgent (PDF, Word, Excel)**
- **File Dimodifikasi**: `backend/agents/file_analysis_agent.py`
- **Detail Perubahan**: 
  - **Dukungan Format Modern**: Menambahkan *parser* internal untuk langsung membaca file `.pdf` (via PyPDF2), `.docx` (via python-docx), dan `.xlsx/.csv` (via pandas).
  - **Penghapusan Batas Token (Pemotongan)**: Mengabulkan dilema batas pemotongan. Sistem sekarang **tidak akan memotong file** meskipun ukurannya raksasa. Asumsinya, *user* menggunakan LLM modern dengan *Context Window* raksasa (seperti Gemini 1.5 Pro dengan 2 juta token atau Claude 3.5).
  - **Proteksi Dependensi**: Jika *library* pembaca (seperti `pandas` atau `PyPDF2`) belum diinstal di laptop/server pengguna, agen tidak akan *crash*, melainkan dengan cerdas memberi tahu perintah `pip install` yang spesifik di chat.

---

## [v0.3.2] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Finalisasi Fungsionalitas Pasukan Sub-Agent (Fase 3)**
- **File Dimodifikasi**: `file_analysis_agent.py`, `research_agent.py`, `web_search_agent.py`
- **Detail Perubahan**: 
  - **`FileAnalysisAgent`**: Kini benar-benar berfungsi! Agen bisa membaca *path* file (seperti `.txt`, `.md`, dll) yang dimasukkan pengguna, menangani batas *token* secara otomatis (memotong file jika kepanjangan), dan mengirim isinya ke LLM untuk dianalisis dan diringkas.
  - **`ResearchAgent`**: Bukan sekadar tanya jawab biasa lagi. Prompt telah diperkuat (*structured prompting*) sehingga agen ini dipaksa menghasilkan dokumen riset ala akademis yang terdiri dari: Ringkasan Eksekutif, Analisis Utama, Pro/Kontra, dan Kesimpulan.
  - **`WebSearchAgent`**: Telah dihidupkan dengan integrasi internet nyata! Agen akan meminta LLM mengekstrak kata kunci pencarian, memanggil **API Wikipedia** via `urllib` (tanpa dependensi eksternal), membersihkan tag HTML dari cuplikan hasil pencarian (*snippets*), dan merangkum hasil internet tersebut untuk disajikan kepada pengguna.

---

## [v0.3.1] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Implementasi Arsitektur Sub-Agent (Fase 3)**
- **Folder**: `backend/agents/`
- **File Dibuat**: `base_agent.py`, `database_explorer_agent.py`, `research_agent.py`, `web_search_agent.py`, `file_analysis_agent.py`
- **Detail Perubahan**: 
  - Membuat *interface* standar `BaseAgent` untuk menyeragamkan cara kerja seluruh agen spesialis.
  - Menghidupkan **`DatabaseExplorerAgent`**: Agen ini kini dapat menerima file database, mengirimkannya ke `DatabaseDetector` dan `SchemaMapper` yang baru kita buat, menyatukan hasilnya dengan prompt yang rapi, dan mendelegasikannya ke LLM untuk menjawab pertanyaan natural dari pengguna berdasarkan data nyata.
  - Memodifikasi `planning_engine.py` untuk mengenali kalimat perintah agen (misal: "pakai agen database untuk cek...").
  - Memodifikasi `main_orchestrator.py` (alur eksekusi Kolom 2) untuk membajak siklus normal (*bypass decision*) dan langsung meneruskan kontrol kepada *Database Explorer Agent* secara mulus.

---

## [v0.3.0] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Implementasi Otomasi Database Detector (Fase 3)**
- **Folder**: `backend/database_detector/`
- **File Baru Diisi**: `detector.py`, `schema_mapper.py`, `query_builder.py`
- **Detail Perubahan**: 
  - Mengisi struktur *blank canvas* Fase 3 dengan algoritma pendeteksi *database* otomatis.
  - **`DatabaseDetector`**: Mampu mendeteksi secara otomatis apakah sebuah file itu CSV, JSON, atau SQLite (bahkan bisa membaca *Magic Bytes* SQLite jika ekstensinya tidak valid).
  - **`SchemaMapper`**: Menggunakan teknik *introspection* (seperti `PRAGMA table_info` di SQLite dan membaca *headers* di CSV) untuk memetakan nama kolom, tipe data, status *Primary Key*, dan otomatis menarik 5 baris data pertama (*sample data*) sebagai konteks untuk LLM nantinya.
  - **`QueryBuilder`**: Telah disiapkan *class* kerangka yang nantinya akan bertugas menerjemahkan *Natural Language* menjadi bahasa SQL/Filter dengan bantuan *Provider Router* AI.

---

## [v0.2.3] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Integrasi API Budget Control Dashboard (Fase 2 D)**
- **File**: `backend/main.py`
- **Fungsi**: `get_budget(user_id: str)`
- **Detail Perubahan**: 
  - Menambahkan *endpoint* baru `@app.get("/api/budget")` di `main.py` untuk menjembatani Frontend (`BudgetDashboard.tsx`) dengan SQLite `usage_logs` via `ProviderRouter`.
  - Endpoint ini memanggil `router.get_budget_status()` yang menghitung penggunaan dana secara real-time dan memberikan peringatan (status: `ok`, `half`, `warning`, `exceeded`) jika biaya panggilan LLM/Embedding sudah melampaui batas anggaran bulanan.
  - Sekarang jika Anda menekan tombol "💰 Budget" di UI utama, data yang tampil bukan lagi memunculkan pesan error, melainkan grafik penggunaan anggaran sesungguhnya (Realisasi target Fase 2 D).

---

## [v0.2.2] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Integrasi UI Engineer Sandbox (Fase 2 C)**
- **File**: `frontend/src/app/page.tsx`
- **Komponen**: `ChatColumn`
- **Detail Perubahan**: 
  - Kolom 3 (Engineer) sekarang tidak hanya menampilkan teks mentah, tetapi mendukung **Alur Persetujuan Sandbox (Approval Flow)** secara interaktif.
  - Saat backend memberikan *flag* `requires_approval: true` (seperti saat Engineer ingin mengubah kode atau mengeksekusi perintah terminal), UI akan memunculkan tombol aksi **"✅ Setujui & Deploy"** dan **"🚫 Tolak"** tepat di bawah cuplikan kode (*diff*).
  - Menambahkan fungsi `handleAction(actionText)` yang secara otomatis menangani *state* tombol, lalu mengirimkan perintah `setujui` atau `tolak` ke backend melalui *event* klik semu (*synthetic click*) pada tombol kirim.
  - Ini adalah realisasi fitur pengaman (Safety Guard) tertinggi di mana tidak ada eksekusi berbahaya yang berjalan tanpa izin eksplisit di *Frontend*.

---

## [v0.2.1] - 2026-07-07

### 🚀 Peningkatan (Upgrades)

**1. Perbaikan Deteksi Intent (Planning Engine)**
- **File**: `backend/orchestrator/planning_engine.py`
- **Fungsi**: `_detect_intent(self, message: str) -> str`
- **Detail Perubahan**: 
  - Menambahkan `import re` di *top-level*.
  - Mengubah logika kaku `message.startswith(...)` menjadi *Regular Expression* (RegEx) yang jauh lebih cerdas.
  - *Code snippet*: Menambahkan `command_pattern = r'^(tolong\s+)?(buat|bikin|tambah|hapus|edit|ubah|perbaiki|tulis|jalankan|eksekusi)\b'`.
  - Mampu mendeteksi pola pencarian dokumen (`search_pattern`) dan pertanyaan mendetail (`question_pattern`) berdasarkan konteks kalimat, bukan sekadar letak kata.

**2. Mekanisme Forgetting di Kernel (Main Orchestrator)**
- **File**: `backend/orchestrator/main_orchestrator.py`
- **Fungsi**: `boot(self)`
- **Detail Perubahan**: 
  - Menambahkan eksekusi `UserMemory(email="default").cleanup_expired_facts()` di dalam siklus *booting* kernel.
  - Ini memastikan setiap kali MAMET OS dinyalakan, ia akan membersihkan tabel SQLite `facts` di mana nilai `expires_at` sudah lewat batas hari ini, lalu menandainya sebagai `is_active = 0`.

**3. Integrasi Ekstraksi Fakta Asinkron (User Memory - Fase 2 A)**
- **File**: `backend/orchestrator/main_orchestrator.py`
- **Fungsi**: `_save_conversation()` dan fungsi baru `_extract_and_save_facts()`
- **Detail Perubahan**:
  - Di dalam `_save_conversation`, menambahkan filter logika: `if column == "kolom2" and api_key:` untuk memicu ekstraksi *hanya* jika terjadi percakapan asisten pribadi.
  - Memanfaatkan `asyncio.create_task(self._extract_and_save_facts(...))` agar pemanggilan LLM berjalan di *background* tanpa menghalangi *response* cepat UI ke pengguna (Non-blocking).
  - Menginstansiasi `FactExtractor` dan menyimpan hasil *parsing* JSON (*confidence* & *fact*) ke dalam SQLite lewat metode `memory.add_fact()`.

### 🔧 Perbaikan (Bug Fixes & Refactoring)

**Penghapusan Dynamic Imports (Mencegah Runtime Crash)**
- **File yang Diubah**:
  1. `backend/orchestrator/main_orchestrator.py` (pada fungsi `_save_conversation` dan `_build_response`)
  2. `backend/orchestrator/evidence_collector.py` (pada fungsi `_get_rag_engine`, `_check_user_memory`, dan `_check_engineer`)
- **Detail Perubahan**:
  - Mencabut instruksi impor lokal (seperti `from memory.user_memory import UserMemory`, `from rag.rag_engine import RAGEngine`, dan `from engineer.engineer_main import Engineer`) dari dalam *scope* metode/fungsi.
  - Memindahkannya ke bagian atas dokumen (*top-level import*).
  - *Tujuan Teknis*: Modul-modul ini sangat krusial. Jika terjadi *Circular Import* atau modul gagal dibaca, *error* harus terjadi tepat saat `boot()` dijalankan, sehingga arsitek dapat langsung memperbaikinya, bukan tersembunyi hingga *user* menge-klik tombol obrolan.

---

## [v0.2.0] - Fondasi Awal (Fase 1)
- **Implementasi Kernel Simbolik**: Sistem berjalan tanpa wajib memanggil LLM. Dibuatnya alur siklus: `Planning Engine` -> `Evidence Collector` -> `Decision Engine`. LLM hanya digunakan sebagai generator akhir jika dinilai perlu.
- **Arsitektur Modular (Lego)**: Memisahkan antarmuka antar AI, Database, Memori, dan Engine Pencarian dalam struktur `backend/`.
- **Integrasi UI 3 Kolom**: Next.js React yang mengelompokkan RAG (Kolom 1), Asisten Pribadi (Kolom 2), dan Engineer (Kolom 3).
