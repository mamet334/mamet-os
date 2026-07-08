
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

Dokumen ini sudah mencakup semua keputusan hingga sesi ini. Anda bisa menyimpannya sebagai `Spesifikasi v3.1.md` yang baru.