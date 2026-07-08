# Catatan Pengembangan: Perombakan UI/UX (Level 4 Glassmorphism)
**Tanggal:** 8 Juli 2026

Dokumen ini mencatat transisi dan perombakan desain antarmuka pengguna (UI) dari Level 3 (standar TailwindCSS) menjadi **Level 4 (Premium Glassmorphism)** sesuai dengan visi *MAMET OS v3.1*.

## 🎨 Tujuan Perombakan
Mengangkat nilai estetika aplikasi *Svelte + Tauri* agar tidak terlihat kaku, melainkan terasa seperti *Personal Assistant* futuristik yang premium dan mewah.

## 🛠️ Modifikasi Teknis

### 1. Integrasi Sistem Tipografi Global
- **File:** `desktop/src/app.html`
- Menyuntikkan tag meta pemanggilan *Google Fonts* secara global (Inter untuk teks UI, dan JetBrains Mono untuk pembacaan kode/obrolan).
- **Alasan:** Font bawaan sistem terlalu generik. `Inter` memberikan kejelasan baca yang modern.

### 2. Penambahan Palet Warna Kustom
- **File:** `desktop/tailwind.config.js`
- Mengekstensi konfigurasi warna (`extend: { colors: ... }`) dengan palet eksklusif:
  - `mamet-cyan` (`#00dbe9`): Aksen utama yang memancarkan pendaran neon.
  - `mamet-purple` (`#e9b3ff`): Aksen sekunder.
  - `mamet-amber` (`#ffb950`): Aksen peringatan.
  - Serta variabel transparansi kaca seperti `glass` dan `glassBorder`.

### 3. Pembuatan Utilitas *Glassmorphism*
- **File:** `desktop/src/app.css`
- Menghapus ketergantungan pada blok *hardcode* di komponen dan menyatukannya ke dalam blok `@layer components`.
- **`.glass-panel`**: Menciptakan panel tembus pandang menggunakan kombinasi `backdrop-blur-xl`, `bg-white/5` (kaca), dan efek bayangan (*shadow*) berkedalaman tinggi.
- **Background Utama**: Memanfaatkan `radial-gradient` gelap secara langsung pada elemen `body` untuk menghasilkan tekstur kedalaman luar angkasa, menyingkirkan `bg-gray-900` solid.

### 4. Implementasi Estetika di Berbagai Rute (Routes)
- **Layar Login (`+page.svelte`)**: Mendesain ulang struktur tata letak (layout) menjadi panel tunggal di tengah dengan dekorasi lingkaran *(glow blur)* neon di belakangnya.
- **Layar Dashboard (`dashboard/+page.svelte`)**: Mengganti kotak statistik generik dengan `.glass-panel`. Efek *shimmer* bercahaya animasi juga ditambahkan ke bar anggaran (Budget Bar) untuk membuatnya terasa interaktif.
- **Layar Workspace 3 Kolom (`workspace/+page.svelte`)**: 
  - Panel Sidebar kini menggunakan kelas *glass* menempel di kiri layar (tanpa sudut membulat/rounded-none di sisi tepi).
  - Gelembung pesan (*Chat Bubbles*) milik User disorot menggunakan *outline* pendaran `cyan-glow`, sedangkan pesan Asisten menggunakan latar belakang kaca abu-abu.
  - Area penulisan (*textarea*) kini merespons pantulan cincin *cyan* ketika sedang dititikfokuskan (`focus-within:ring-mamet-cyan/50`).
- **Layar Credit (`credit/+page.svelte`)**: Menyelaraskan teks judul (yang awalnya biru pucat bawaan) agar memakai sorotan `text-mamet-cyan` yang konsisten.

## 🏁 Kesimpulan
Sistem kini secara penuh mewakili desain masa depan (Level 4), sekaligus menjaga responsivitas dan performa super-ringan dari kerangka kerja *Svelte 5*. Tidak ada penurunan FPS *(Frames per Second)* saat efek blur kaca diterapkan.
