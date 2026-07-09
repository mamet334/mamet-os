# Pembaruan Fitur Project Context: Smart Keyword Matching & Browser Fallback
**Tanggal:** 9 Juli 2026

Dokumen ini mencatat penyelesaian dan perapian fitur **Project Context** (Kolom 2) sesuai dengan spesifikasi v3.1, memastikan Asisten Pribadi mampu membaca dan menganalisis berkas dalam direktori proyek pengguna secara natural dan akurat.

## 1. Masalah pada Implementasi Sebelumnya
Sebelum pembaruan ini, fitur pencarian file mengandalkan Regular Expression (*Regex*) yang sangat kaku di `evidence_collector.py`:
- Pengguna **wajib** mengetik nama file beserta ekstensinya (misalnya: `auth_handler.py`). Jika ekstensi tidak ditulis, sistem tidak akan menyadari bahwa pengguna meminta sebuah file.
- Sistem berasumsi bahwa berkas yang diminta selalu berada di pangkal (*root*) direktori proyek. Akibatnya, jika pengguna meminta berkas yang berada jauh di dalam sub-direktori (misalnya `backend/auth/auth_handler.py`), mekanisme `FileReader.read_file()` akan mengalami *Path Not Found*.

## 2. Solusi: Smart Keyword Matching (Pencocokan Cerdas)
Logika di dalam `backend/orchestrator/evidence_collector.py` (pada fungsi `_check_project_context`) dirombak secara total:
1. **Pemindaian Rekursif (Deep Scan):** Sistem kini memanggil `reader.list_directory(recursive=True, depth=10)` untuk menginventarisasi seluruh nama berkas di seluruh sub-folder proyek pengguna.
2. **Ekstraksi Kosakata:** Pesan/Prompt pengguna dipecah menjadi kumpulan kata (*words set*), sehingga menoleransi tanda baca, spasi, atau huruf besar/kecil.
3. **Pencocokan Nama Dasar (Basename):** Sistem mencocokkan setiap nama berkas yang ditemukan (baik nama utuh `main.py` maupun nama dasarnya saja `main`) dengan kata-kata yang diucapkan pengguna.
4. **Keberhasilan:** Asisten kini dapat membaca isi berkas meskipun pengguna menyebutnya dengan bahasa yang sangat santai, contoh: *"coba jelaskan auth_handler dan planning_engine"*, dan Asisten berhasil menemukannya meskipun berkas tersebut bersarang di dalam sub-folder.

## 3. Penambahan Mekanisme Fallback Peramban Web (UI)
Pada `desktop/src/routes/workspace/+page.svelte`, terdapat fungsi `pickProjectFolder()` yang sebelumnya hanya mengandalkan API `@tauri-apps/plugin-dialog`.
- **Kendala Keamanan:** API dialog Tauri diblokir saat antarmuka Svelte dijalankan melalui peramban web standar (`npm run dev` pada `localhost:5173`) atau ketika kapabilitas `"dialog:default"` tidak diaktifkan. Hal ini menyebabkan tombol "Pilih Folder" mati rasa.
- **Solusi:** Kami menyuntikkan *browser fallback* berbasis `window.prompt`. Jika pemanggilan *dialog* Tauri gagal, antarmuka akan memunculkan *pop-up* peringatan yang mengizinkan pengguna untuk menempelkan (copy-paste) jalur direktori (contoh: `D:\SLAMET\other\mamet-os`) secara manual, sehingga fitur Project Context tetap menyala penuh tanpa memaksakan kompilasi biner Rust (*cargo build*). Izin `"dialog:default"` juga telah ditambahkan ke `default.json` Tauri.

**Status Akhir:**
Fitur Project Context (Prioritas 1) telah selesai dan beroperasi secara optimal, memampukan Asisten Pribadi (Kolom 2) untuk memiliki kesadaran visual menyeluruh terhadap *local filesystem* proyek yang ditunjuk.
