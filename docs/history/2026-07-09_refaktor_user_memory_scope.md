# Riwayat Perubahan: Refaktorisasi Ruang Lingkup (Scope) User Memory
**Tanggal**: 9 Juli 2026

## Latar Belakang Masalah
Dalam arsitektur sebelumnya (Pilar G: *Health Monitoring*), rutinitas pemeriksaan integritas basis data (*Integrity Check*) dan penghapusan memori kadaluwarsa (*Forgetting Mechanism*) ditanamkan secara kaku (*hardcoded*) ke dalam fungsi `boot()` milik `MainOrchestrator`. 

Karena proses `boot()` berjalan sebelum ada pengguna yang melakukan interaksi, kernel terpaksa menginisiasi kelas memori dengan identitas hampa: `UserMemory(email="default")`. Hal ini memicu dua masalah arsitektural:
1. **Inkonsistensi Identitas**: Log sistem selalu melaporkan bahwa "Database memori sehat", padahal yang dicek hanyalah berkas milik pengguna bernama `"default"`, bukan pengguna asli yang sedang *login*.
2. **Efisiensi Booting**: Server membuang waktu mili-detik untuk mengecek tabel *database* yang sebenarnya kosong/tidak relevan setiap kali server dinyalakan ulang.

## Resolusi & Perubahan Kode
Kami mengeksekusi perombakan ruang lingkup (*scope refactoring*) pada berkas `backend/orchestrator/main_orchestrator.py`:

1. **Penghapusan dari `boot()`**
   *Blok try-except* yang mengunci `UserMemory` diangkat seutuhnya dari fase *startup* server. Kini, `boot()` bertindak murni hanya untuk menyiapkan mesin kecerdasan (*Planning, Collector, Decision*).

2. **Injeksi Tepat Waktu (Just-in-Time) pada `process()`**
   Rutinitas pemeliharaan memori dipindahkan ke baris terdepan dari fungsi `process()`. Fungsi ini baru akan aktif ketika sistem menerima interaksi dari pengguna, sehingga ia memiliki akses absolut ke variabel `user_id`.
   ```python
   # Potongan kode baru di dalam process()
   mem = UserMemory(email=user_id)
   if not mem.check_integrity():
       print(f"[KERNEL-CRITICAL] ⚠️ Database memori rusak untuk {user_id}...")
   deleted = mem.cleanup_expired_facts()
   if deleted > 0:
       print(f"[KERNEL] Forgetting Mechanism: Dihapus {deleted} fakta kedaluwarsa untuk {user_id}.")
   ```

## Dampak (*Impact*)
*   **Multi-tenant Ready**: MAMET OS kini sepenuhnya kebal terhadap tabrakan antar-sesi pengguna. Jika Budi dan Tono menggunakan MAMET OS secara bersamaan, *Forgetting Mechanism* hanya akan membersihkan ingatan Budi saat Budi mengirim pesan, dan ingatan Tono saat Tono mengirim pesan.
*   **Log Presisi**: Administrator (*Developer*) kini bisa melacak secara akurat di terminal, atas *user_id* siapa sebuah kerusakan database terjadi (Pilar G).
