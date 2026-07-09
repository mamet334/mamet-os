
```markdown
# MAMET OS v3.1 — Spesifikasi Teknis Lengkap (Final)

## Visi
MAMET OS adalah **asisten pribadi lokal** yang tumbuh bersama pengguna, 
mampu mengingat, mencari, membantu coding, dan menjelajah internet. 
Tujuan akhirnya adalah menjadi **warisan digital** — aplikasi utuh yang 
bisa diwariskan dan terus hidup membantu orang yang ditinggalkan.

**Prinsip Kunci:** Email adalah identitas. Ganti email = ganti seluruh memori. 
Untuk mengakses warisan digital, penerima harus login dengan **email pemilik asli**.

---

## 1. Identitas & Peran Tiga Kolom (Final)

| Kolom | Peran | Kata Kunci | Fitur Unggulan |
|-------|-------|------------|----------------|
| 🔍 **Pencarian Cepat** | Upload & retrieval dokumen | **Upload & Cari** | Satu-satunya pintu upload ke RAG |
| 🤖 **Asisten Pribadi** | Teman diskusi, teman kerja | **Diskusi & Kolaborasi** | Project Context, Deteksi Emosi, Sub-agent |
| 🔧 **Engineer** | Mekanik pribadi MAMET OS | **Self-Maintenance** | Hanya mengurus kode MAMET OS sendiri |

**Aturan:**
- Upload dokumen hanya di Kolom 1.
- Kolom 2 dan 3 bisa membaca hasil RAG, tidak bisa menambah.
- Kolom 2 memiliki fitur **Project Context** (lihat folder proyek pengguna).
- Kolom 3 hanya mengurus kode MAMET OS sendiri, bukan proyek pengguna.

---

## 2. Desain UI Modern (Level 4)

### Prinsip Dasar
- **Glassmorphism Premium:** `backdrop-blur-xl`, border `white/10`, bayangan berwarna aksen.
- **Micro-interactions:** `hover:scale-102`, `active:scale-95`, animasi fade-in.
- **Tipografi:** Inter (UI) + JetBrains Mono (kode). Hierarki jelas.
- **Palet Warna:** Cyan (`#00dbe9`) utama, Purple (`#e9b3ff`) sekunder, Amber (`#ffb950`) peringatan.

### Komponen Utama
- **Sidebar:** `glass-panel`, lebar `w-64`, item aktif dengan cyan glow.
- **Dashboard Awal:** Grid statistik, tombol "Masuk ke 3 Kolom" besar dan glowing.
- **Input Chat:** `rounded-full`, `bg-white/5`, tombol kirim bulat di dalamnya.
- **Pesan:** User (cyan background, rata kanan), Asisten (abu transparan, rata kiri).

**Level UI:** Level 4 (Modern Premium). Level 5 (Experimental/Cinematic) adalah future UI.

---

## 3. Fitur: Project Context (Asisten Pribadi)

**Tujuan:** Asisten bisa melihat, membaca, berdiskusi, dan mengedit file di folder proyek pengguna 
tanpa harus mengunggah ke RAG.

**Cara Kerja:**
1. Tombol "📂 Pilih Folder" di header Kolom 2 (hanya desktop via Tauri).
2. Pengguna memilih folder proyek.
3. Asisten dapat: list struktur, baca file, analisis kode, edit file (dengan persetujuan).
4. Keamanan: hanya folder yang dipilih, sandboxing, persetujuan wajib untuk menulis.

---

## 4. Peta Pengembangan Asisten Pribadi

| Prioritas | Fitur | Status |
|-----------|-------|--------|
| 1 | Project Context | ⬜ Selanjutnya |
| 2 | Deteksi Emosi & Tone Adaptation | ⬜ Pilar B |
| 3 | Meringkas & Menulis Terstruktur | ⬜ |
| 4 | Tugas Multi-langkah Otonom | ⬜ |
| 5 | Belajar dari Kebiasaan | ⬜ |

---

## 5. Pilar yang Sudah & Belum

| Pilar | Topik | Status |
|-------|-------|--------|
| A | Kecerdasan & Memori (Offline LLM/Ollama) | 🔌 Kran siap, ditunda |
| B | Pendalaman Asisten (Empati, Multi-file Engineer) | ⬜ |
| C | Agen & Otomatisasi (Sub-agent, DB Explorer) | ✅ Sebagian besar |
| D | Keamanan & Stabilitas (Unit/Stress Test) | ⬜ |
| E | Dashboard Awal & Credit Berjalan | ✅ Selesai |

---

## 6. Strategi Backup & Sinkronisasi (Tiga Lapis + Manual)

| Lapis | Tempat | Isi | Otomatis? | Lindungi dari? |
|-------|--------|-----|-----------|----------------|
| 🔑 **Kode** | **GitHub** | Kode MAMET OS, struktur, logika | ✅ (git push/pull) | Laptop rusak, kode hilang |
| ☁️ **Data Pribadi** | **Google Drive** | memory.db, chroma_db, API key (terenkripsi AES-256) | ✅ (auto sync via modul) | Laptop rusak, ingatan hilang |
| 💾 **Backup Lokal** | **Folder `rollback/`** | Kode + Data pribadi lengkap | ✅ (sebelum perubahan Engineer) | Kesalahan Engineer |
| 💿 **Backup Manual** | **Flashdisk / Harddisk Eksternal** | Seluruh folder MAMET OS | ❌ (manual, periodik) | Semua — laptop hilang, bencana |

**Penjelasan:**
- **GitHub:** Hanya kode. Data pribadi dikecualikan via `.gitignore` (`user_data/`).
- **Google Drive:** Data pribadi terenkripsi. Sinkronisasi otomatis via modul `google_drive_sync.py`.
- **Rollback Lokal:** Setiap kali Engineer akan mengubah sistem, backup ZIP dibuat di folder `rollback/`.
- **Backup Manual:** Salin seluruh folder `mamet-os` ke media eksternal.

---

## 7. Teknis Backup ke Flashdisk (Incremental Sync)

**Tujuan:** Menyimpan salinan persis folder MAMET OS ke flashdisk tanpa menumpuk file 
yang tidak berubah, dan tanpa mengganggu file/folder lain di flashdisk.

### Metode: `robocopy` (Windows) atau `rsync` (Linux/macOS)

**Sumber:** `D:\SLAMET\other\mamet-os\`  
**Tujuan:** `E:\Backup\MametOS\` (folder khusus di flashdisk)

### Perintah (Windows - Command Prompt):
```cmd
robocopy D:\SLAMET\other\mamet-os E:\Backup\MametOS /MIR
```

**Penjelasan:**
- `/MIR` (Mirror): Membuat folder tujuan menjadi cerminan persis dari sumber.
  - File baru/berubah di sumber → disalin ke tujuan.
  - File dihapus di sumber → dihapus di tujuan.
  - File yang tidak berubah → dilewati (tidak disalin ulang).
- Hanya folder `E:\Backup\MametOS` yang terpengaruh. File/folder lain di `E:\` tetap aman.

### Perintah (Linux/macOS):
```bash
rsync -av --delete /home/user/mamet-os/ /media/flashdisk/Backup/MametOS/
```

**Keuntungan:**
- Backup pertama mungkin lambat (salin semua). Backup berikutnya hanya hitungan detik.
- Tidak menumpuk file duplikat di flashdisk.
- Folder tujuan selalu sama persis dengan folder sumber.

---

## 8. Visi Warisan Digital (Final)

1. **Bangun MAMET OS** dengan semua ingatan Anda di dalamnya.
2. **Backup berkala** ke flashdisk menggunakan `robocopy` / `rsync`.
3. **Simpan flashdisk** di tempat aman.
4. **Berikan kepada penerima** bersama kredensial login (email + password Anda).
5. **Penerima login dengan email Anda** → semua ingatan Anda terbuka.
6. **Asisten melanjutkan "hidup" Anda**, membantu penerima seperti ia membantu Anda.

**Catatan:** Jika penerima login dengan emailnya sendiri, MAMET OS akan membuat akun baru 
yang kosong. Ingatan Anda hanya bisa diakses dengan email dan password Anda.

---

## 9. Status Saat Ini (per 8 Juli 2026)
- Kernel Orchestrator: ✅
- RAG Engine + Upload: ✅
- Engineer Write/Execute + Sandbox + Rollback: ✅
- UI 3 Kolom (Svelte 5 + Tauri): ✅
- User Memory (SQLite): ✅
- Multi-Provider AI: ✅
- Budget Dashboard: ✅
- Dashboard Awal + Credit Berjalan: ✅
- Login & Registrasi: ✅
- Project Context: ⬜ (berikutnya)
- Google Drive Sync: ⬜ (Pilar F baru)
- Unit/Stress Test: ⬜ (Pilar D)

---

## 10. Prinsip Utama
- **Fleksibel**: Komponen independen, plug-and-play (Lego)
- **Universal**: Berjalan di laptop, HP (via Termux), robot (Raspberry Pi)
- **Milik sendiri**: Email + API key pribadi, data terisolasi
- **Adaptif**: Sistem bisa mendeteksi dan beradaptasi dengan data baru
- **Hemat**: LLM hanya alat bantu terakhir, kernel berjalan simbolik
- **Self-Evolving**: Engineer bisa membantu membangun dan memperbaiki
```

SPESIFIKASI MAMET OS v3.1 — Tambahan & Penyempurnaan

Pendahuluan

Dokumen ini melengkapi Spesifikasi v3.0 yang sudah ada. Berisi keputusan hasil diskusi tentang: peran tiga kolom, desain UI modern, fitur Project Context, peta pengembangan Asisten Pribadi, dan keputusan strategis lainnya.

---

1. Identitas & Peran Tiga Kolom (Final)

Kolom Peran Kata Kunci Fitur Unggulan
🔍 Pencarian Cepat Upload & retrieval dokumen Upload & Cari Satu-satunya pintu upload ke RAG
🤖 Asisten Pribadi Teman diskusi, teman kerja Diskusi & Kolaborasi Project Context, Deteksi Emosi, Sub-agent
🔧 Engineer Mekanik pribadi MAMET OS Self-Maintenance Hanya mengurus kode MAMET OS sendiri

Prinsip Utama:

· Upload hanya ada di Kolom 1. Kolom 2 dan 3 tidak boleh memiliki fitur upload ke RAG.
· Kolom 2 dan 3 bisa membaca hasil RAG, tapi tidak bisa menambah ke RAG.
· Kolom 2 boleh memiliki lampiran di chat (file sementara untuk analisis), bukan upload.
· Ketiga kolom adalah identitas MAMET OS yang tidak boleh dihilangkan.

---

2. Spesifikasi Desain UI Modern (Level 4)

2.1 Prinsip Dasar

· Kedalaman & Nuansa: Gunakan transparansi, blur, dan border halus. Tidak ada warna solid.
· Responsif & Hidup: Setiap tombol, link, dan card harus memberikan feedback visual (hover, active).
· Hierarki Jelas: Ukuran, warna, dan gaya font yang kontras untuk judul, teks tubuh, dan label teknis.

2.2 Komponen Utama

Komponen Gaya
Sidebar glass-panel, lebar w-64, item aktif dengan aksen cyan glow dan border kanan
Dashboard Awal Grid statistik 3 kolom, glass card, tombol "Masuk ke 3 Kolom" besar dan glowing
Input Chat rounded-full, latar bg-white/5, inner shadow, tombol kirim bulat di dalamnya
Pesan User Rata kanan, bg-cyan-900/20, border border-cyan-500/20, animasi fade-in
Pesan Asisten Rata kiri, bg-white/5, border border-white/10, animasi fade-in
Tombol Aksi Gradien halus, shadow berwarna aksen, hover:scale-102, active:scale-95
Loading Skeleton text atau pulsing dots, bukan teks "Memproses..."

2.3 Palet Warna

Peran Warna Penggunaan
Aksen Utama (Cyan) #00dbe9 Tombol utama, tab aktif, fokus input, ikon Engineer
Aksen Sekunder (Purple) #e9b3ff Ikon Asisten, notifikasi
Aksen Tersier (Amber) #ffb950 Peringatan budget, ikon Pencarian Cepat
Latar Utama #131313 Background aplikasi
Latar Panel rgba(0,0,0,0.4) + blur(24px) Glassmorphism

2.4 Tipografi

· Display (48px, bold): Judul halaman
· Headline (32px, semibold): Judul seksi
· Body (16px, regular, line-height 1.7): Teks isi
· Label/Code (14px, monospace): Data teknis — gunakan JetBrains Mono

2.5 Level UI

Posisi MAMET OS saat ini adalah Level 4 (Modern Premium) — setara dengan Linear, Vercel Dashboard, Claude AI.
Level 5 (Experimental/Cinematic) adalah Future UI yang tidak relevan untuk aplikasi produktivitas seperti MAMET OS.

---

3. Fitur: Project Context (Asisten Pribadi)

3.1 Tujuan

Memberikan kemampuan kepada Asisten (Kolom 2) untuk melihat, membaca, berdiskusi, dan mengedit file di dalam folder proyek pribadi user, tanpa harus mengunggah file ke RAG.

3.2 Bukan Upload, Bukan Engineer

 Upload (Kolom 1) Engineer (Kolom 3) Project Context (Kolom 2)
Tujuan Menyimpan ke RAG Memperbaiki MAMET OS Membantu pekerjaan user
Target Dokumen Kode MAMET OS Folder proyek pribadi
Menulis? Tidak Ya, dengan izin Ya, dengan izin
Dicari ulang? Ya (via RAG) Tidak Tidak

3.3 Cara Kerja

1. Tombol "📂 Pilih Folder" di header Kolom 2 (hanya muncul di desktop via Tauri)
2. User memilih folder dari dialog sistem
3. Nama folder ditampilkan di header Kolom 2
4. Asisten sekarang bisa:
   · Membaca struktur folder
   · Membaca file spesifik
   · Menganalisis kode dan berdiskusi
   · Menulis/mengedit file (dengan persetujuan)
5. Keamanan: Hanya folder yang dipilih, sandboxing, persetujuan wajib untuk menulis

3.4 Kebutuhan Teknis

Komponen Perubahan
UI (Svelte) Tombol "📂 Pilih Folder" di header Kolom 2
State projectPath di $state()
Backend Field opsional project_path di /chat
Evidence Collector Method _check_project_context()
Safety Guard Path whitelist sesuai folder yang dipilih

---

4. Peta Pengembangan Asisten Pribadi

4.1 Kemampuan yang Sudah Ada (✅)

· Ngobrol + memori pengguna
· Mencari di RAG + internet (Web Search Agent)
· Membaca file (PDF, DOCX, CSV)
· Analisis data (Database Explorer)
· Research Agent multi-langkah
· Legacy Mode (kerangka)

4.2 Urutan Pengembangan Selanjutnya

Prioritas Fitur Keterangan
1 Project Context Fondasi kolaborasi dengan folder proyek
2 Deteksi Emosi & Tone Adaptation Membuat Asisten terasa "hidup"
3 Meringkas & Menulis Terstruktur Fitur paling sering dipakai pengguna
4 Tugas Multi-langkah Otonom Rantai agen untuk tugas kompleks
5 Belajar dari Kebiasaan Adaptasi berdasarkan rutinitas user

4.3 Yang Sengaja Ditinggalkan (Saat Ini)

· Input/output suara: Butuh resource besar, tidak sebanding dengan prioritas lain.

---

5. Pilar yang Sudah Dikerjakan & Belum

Pilar Topik Status
A Kecerdasan & Memori (Offline LLM/Ollama) 🔌 Kran siap, implementasi ditunda
B Pendalaman Asisten (Empati, Multi-file Engineer) ⬜ Belum (prioritas selanjutnya)
C Agen & Otomatisasi (Sub-agent, DB Explorer, Web Crawling) ✅ Sebagian besar sudah
D Keamanan & Stabilitas (Unit/Stress Test) ⬜ Belum (setelah Pilar B)
E Dashboard Awal & Credit Berjalan ✅ Selesai (v3.0.0-alpha.1)

---

6. Keputusan Strategis (Hasil Diskusi)

1. ✅ Upload hanya di Kolom 1. Kolom 2 dan 3 tidak boleh upload ke RAG.
2. ✅ Kolom 2 punya fitur "Project Context" (pilih folder kerja).
3. ✅ Kolom 3 khusus memperbaiki MAMET OS, bukan proyek user.
4. ✅ Offline LLM (Ollama) ditunda — kran Provider Router sudah siap.
5. ✅ Input suara ditunda — tidak prioritas.
6. ✅ UI Enhancement ke Level 4 (Modern Premium) — Level 5 adalah Future UI.
7. ✅ Tiga kolom adalah identitas MAMET OS yang tidak boleh dihilangkan.
8. ✅ Dashboard Awal + Credit Berjalan sudah menjadi gerbang masuk.


---

SPESIFIKASI MAMET OS v3.1 — Tambahan Pilar G & Penyempurnaan Pilar F

Pilar G: Health Monitoring & Auto-Recovery

G1. Tombol Backup ke Flashdisk (1-Klik)

Tujuan: Memungkinkan pengguna (termasuk penerima warisan yang awam) mencadangkan seluruh folder MAMET OS ke flashdisk hanya dengan satu klik.

Lokasi di UI: Dashboard Awal, bagian bawah panel Status Sistem.

Komponen Teknis:

Komponen Detail
Deteksi flashdisk Modul backend/engineer/disk_detector.py — mendeteksi removable drive yang tersambung (Windows: GetLogicalDrives, Linux: /media/, macOS: /Volumes/)
Dialog pemilihan folder Hanya muncul saat pertama kali. Pengguna memilih folder tujuan di flashdisk. Path disimpan di preferences User Memory.
Eksekusi backup robocopy (Windows) atau rsync (Linux/macOS) dijalankan di belakang layar via subprocess
Progres Tampilkan indikator loading: "Sedang mencadangkan... X file diproses"
Notifikasi selesai "✅ Backup selesai. X file baru, Y file diperbarui, Z file tidak berubah."

Perilaku:

· Backup pertama: menyalin semua file. Mungkin lambat.
· Backup berikutnya: hanya menyalin yang berubah. Cepat (hitungan detik).
· Tidak menyentuh file/folder lain di flashdisk. Hanya folder MametOS yang terpengaruh.
· Jika flashdisk tidak terdeteksi, tombol berwarna abu-abu dan bertuliskan "💾 Colokkan Flashdisk".

---

G2. Integrity Check Saat Booting

Tujuan: Mendeteksi kerusakan database (memory.db) sedini mungkin, setiap kali MAMET OS dinyalakan.

Komponen Teknis:

Komponen Detail
Lokasi kode backend/memory/user_memory.py — method check_integrity()
Waktu eksekusi Dipanggil saat MainOrchestrator.boot()
Perintah SQLite PRAGMA integrity_check;
Hasil "ok" Tidak ada notifikasi. Sistem boot normal.
Hasil "error" Tampilkan peringatan merah di Dashboard: "⚠️ Database rusak terdeteksi. Segera pulihkan dari backup."

Integrasi dengan Dashboard:

· API endpoint GET /api/status menambahkan field database: "healthy" atau database: "corrupt".
· Dashboard membaca field ini dan menampilkan indikator yang sesuai.

---

G3. Auto-Backup Harian

Tujuan: Membuat salinan database secara otomatis setiap hari, tanpa menunggu Engineer bekerja.

Komponen Teknis:

Komponen Detail
Lokasi kode backend/engineer/sandbox.py — method daily_auto_backup()
Pemicu Dijalankan saat MAMET OS idle (tidak ada request selama 5 menit) dan sudah lewat 24 jam sejak backup terakhir
Isi backup Folder user_data/ di-zip dengan nama auto_backup_YYYYMMDD_HHMMSS.zip
Lokasi simpan Folder rollback/
Retensi Hanya menyimpan 7 backup terbaru. Yang lebih lama dihapus otomatis.

Notifikasi (opsional): Setelah backup selesai, catat di log: [AUTO-BACKUP] 2026-07-08 02:00:00 — Sukses (3.2 MB).

---

G4. Tombol "Pulihkan dari Backup"

Tujuan: Memungkinkan pengguna memulihkan database yang rusak hanya dengan satu klik, tanpa perlu membuka folder atau mengetik perintah.

Lokasi di UI: Dashboard Awal, di bawah indikator status database.

Komponen Teknis:

Komponen Detail
Dialog pilihan Menampilkan daftar file backup yang tersedia (nama file, tanggal, ukuran)
Proses restore 1. Hentikan akses ke database. 2. Ekstrak backup ZIP. 3. Timpa database yang rusak. 4. Catat di log.
Setelah restore Tampilkan notifikasi: "✅ Database berhasil dipulihkan. Sistem akan restart."
Fallback Jika tidak ada backup ditemukan, tampilkan: "❌ Tidak ada backup tersedia."

---

Penyempurnaan Pilar F: Cloud Sync

F1. Notifikasi Status Sinkronisasi Google Drive

Tujuan: Memberi tahu pengguna apakah backup cloud berhasil atau gagal, setiap saat.

Komponen Teknis:

Komponen Detail
Lokasi di UI Dashboard Awal, di bawah panel Status Sistem
Teks indikator "☁️ Sinkron terakhir: X menit yang lalu" (hijau) atau "⚠️ Sinkron gagal: token expired" (merah)
Waktu refresh Setiap kali Dashboard dibuka, dan setiap 30 menit saat Dashboard terbuka
Log sync Setiap hasil sync dicatat di file user_data/sync.log

---

F2. Legacy Wizard (Pemandu untuk Penerima Warisan)

Tujuan: Memandu penerima warisan menghubungkan Google Drive mereka sendiri ke MAMET OS, tanpa harus masuk ke Google Cloud Console atau membuat credentials.json secara manual.

Lokasi di UI: Dashboard Awal, tombol besar bertuliskan "🛡️ Aktifkan Warisan Digital".

Alur Langkah demi Langkah:

Langkah Tampilan Tindakan
1 "🛡️ Aktifkan Warisan Digital" Penerima klik tombol
2 "Mempersiapkan koneksi..." MAMET OS membuka browser, menampilkan halaman login Google
3 "Pilih akun Google Anda" Penerima login dengan akun Google mereka sendiri
4 "Izinkan MAMET OS mengakses folder backup?" Penerima klik "Izinkan"
5 "✅ Warisan digital aktif!" MAMET OS menyimpan token. Koneksi selesai. Mulai backup otomatis.

Yang Tidak Perlu Dilakukan Penerima:

· ❌ Masuk ke Google Cloud Console
· ❌ Membuat proyek baru
· ❌ Mengunduh credentials.json
· ❌ Mengerti apa itu OAuth atau API

Yang Terjadi di Belakang Layar (Ditangani MAMET OS):

· Menggunakan OAuth2 flow dengan client ID yang sudah tertanam di MAMET OS
· Menyimpan token di user_data/{email}/token.json
· Memulai backup otomatis ke Google Drive penerima

---

Urutan Implementasi (Final)

Prioritas Fitur Pilar
1 Tombol Backup Flashdisk (1-Klik) G
2 Integrity Check saat Booting G
3 Auto-Backup Harian G
4 Tombol "Pulihkan dari Backup" G
5 Notifikasi Status Sync Google Drive F
6 Legacy Wizard F

---

Dokumen ini melengkapi Spesifikasi v3.1 yang sudah ada. Simpan sebagai Spesifikasi v3.1 - Pilar G & F.md.
