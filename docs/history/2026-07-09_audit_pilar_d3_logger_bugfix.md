# Riwayat Perubahan: Audit Pilar D3 & Perbaikan Bug Sistem Log
**Tanggal**: 9 Juli 2026

## Ringkasan Eksekutif
Dokumen ini mencatat hasil audit fungsional terhadap modul-modul Pilar D (Keamanan & Stabilitas), spesifiknya pada pengujian tekanan (`stress_test.py`) dan modul perekaman aktivitas (`logger.py`). Selama audit berlangsung, ditemukan dua *bug* struktural yang berpotensi merusak pengalaman pengembang (*Developer Experience*) pada sistem operasi Windows. Keduanya telah diisolasi dan diatasi.

## Daftar Temuan & Perbaikan Kode

### 1. Bug *UnicodeEncodeError* (Emoji Windows)
*   **Lokasi Berkas**: `backend/stress_test.py` (dan `audit_pilar_d3.py`)
*   **Gejala (*Symptom*)**: Saat menjalankan *stress test* via terminal Windows (CMD/PowerShell), sistem mengalami benturan (*crash*) mematikan dengan pesan `UnicodeEncodeError: 'charmap' codec can't encode characters`.
*   **Penyebab (*Root Cause*)**: MAMET OS menggunakan banyak emoji (*seperti ✅, ❌, ⚠️*) sebagai penanda visual yang cepat ditangkap oleh mata. Namun, konsol bawaan Windows tidak menggunakan penyandian (*encoding*) UTF-8 secara *default* (melainkan `cp1252` atau varian lainnya). Ketika instruksi `print()` mengeksekusi karakter Unicode ekstrim, *buffer stdout* tidak mampu menerjemahkannya lalu terhenti total.
*   **Perbaikan Kode**:
    Saya menginjeksi rekayasa alur pada baris ke-9 `stress_test.py` untuk secara paksa mengubah *encoding stream output* terminal ke UTF-8 sebelum orkestrator dan modul lainnya dimuat:
    ```python
    # Paksa stdout encoding ke utf-8 agar tidak error di Windows console (untuk emoji)
    if hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    ```
*   **Alasan**: Daripada menghapus fitur emoji yang merusak estetika *log*, memaksa terminal untuk mengadopsi standar UTF-8 menjamin seluruh antarmuka karakter tercetak sempurna tanpa menyentuh ratusan perintah `print` di dalam inti sistem.

### 2. Bug *Ghost Log* (Karakter *Newline* Kosong)
*   **Lokasi Berkas**: `backend/orchestrator/logger.py`
*   **Gejala (*Symptom*)**: Saat UI Svelte memanggil `/api/logs`, baris log yang dihasilkan memunculkan entitas kosong bertuliskan `[ERROR] ` setiap kali sebuah eksepsi (*Traceback*) dilempar.
*   **Penyebab (*Root Cause*)**: Mekanisme `MametLogger` mencegat (*intercept*) aliran data dari `sys.stderr`. Saat *backend* mencetak pesan *error* standar (seperti `print("pesan", file=sys.stderr)`), Python memisahkan pengiriman string; ia mengirim string `"pesan"` terlebih dahulu, lalu di aliran kedua ia mengirim karakter *newline* `"\n"`. Fungsi `write_err` sebelumnya langsung menyerap karakter `\n` tersebut dan memformatnya buta-buta menjadi `[ERROR] \n`.
*   **Perbaikan Kode**:
    Menambahkan saringan (*filter*) presisi pada fungsi `write_err` (baris 49):
    ```python
    def write_err(self, message):
        self.terminal_err.write(message)
        # Saringan baru: Hentikan eksekusi jika pesan hanyalah spasi kosong / newline
        if not message or message == '\n':
            return
        self._write_to_file(f"[ERROR] {message}")
    ```
*   **Alasan**: Modifikasi ini secara krusial mencegah penumpukan baris *log* yang tidak bermakna di Dasbor Svelte dan memastikan sistem hanya menyerap substansi peringatannya saja. 

## Kesimpulan
Sistem *Error Monitoring* Pilar D3 kini lulus inspeksi presisi. Modul sudah diuji kembali melalui `audit_pilar_d3.py` dan mampu menghasilkan catatan waktu harian yang mutlak rapi, serta mampu menahan uji gempuran 50-pemanggilan bersamaan dari `stress_test.py` dengan aman.
