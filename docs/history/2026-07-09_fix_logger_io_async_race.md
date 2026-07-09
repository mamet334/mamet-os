# Riwayat Perubahan: Perbaikan I/O Buffer & Race Condition Logger
**Tanggal**: 9 Juli 2026

## Latar Belakang Masalah
Sistem pelacakan *error* 24 jam (Pilar D3) dilaporkan berhenti memperbarui *file* `mamet.log` meskipun *backend* (FastAPI) terus berjalan dan menerima berbagai permintaan (*request*) API. Investigasi mendalam mengungkapkan dua cacat arsitektur yang sangat krusial:

1. **Jebakan I/O Buffer (Python)**:
   Meskipun pesan sudah dicegat dan dikirim ke fungsi penulisan *file*, sistem operasi (Windows) dan Python menggunakan mekanisme *block-buffering*. Teks log tidak langsung ditulis secara harfiah ke piringan *harddisk*, melainkan "ditampung" terlebih dahulu di memori sementara (RAM) hingga mencapai ukuran tertentu. Hal ini menyebabkan antarmuka Svelte gagal menampilkan log terbaru.

2. **Race Condition Asinkron yang Fatal (`io.StringIO`)**:
   Sebelumnya, demi meredam *spam* log saat inisialisasi status *cache*, *endpoint* `/api/status` secara radikal mengalihkan aliran `sys.stdout` global ke `io.StringIO()`. Dalam ekosistem asinkron (`asyncio`/Uvicorn), jika modul lain atau *thread* lain melakukan `print()` secara simultan tepat di milidetik saat *stdout* dialihkan, log tersebut akan ditelan ke lubang hitam (*blackhole*) `io.StringIO()` dan lenyap selamanya tanpa pernah mencapai terminal ataupun *file* log.

## Resolusi & Perubahan Kode

1. **Memaksa Flush Level-OS (`backend/orchestrator/logger.py`)**:
   Fungsi `_write_to_file` dirombak agar seketika memaksa perangkat keras untuk menulis log ke cakram (*disk*) tanpa kompromi:
   ```python
   f.writelines(formatted_lines)
   f.flush()               # Kosongkan buffer Python
   os.fsync(f.fileno())    # Paksa sinkronisasi I/O pada OS
   ```
2. **Penghapusan Peredam Berbahaya (`backend/main.py`)**:
   Blok `sys.stdout = io.StringIO()` pada *endpoint* `/api/status` dihapus sepenuhnya. Sistem kini murni mengandalkan mekanisme pemblokiran inisialisasi ganda via variabel *cache* global, membiarkan inisialisasi pertama tercetak wajar, tanpa membahayakan aliran log dari proses *background* lainnya.
3. **Pesan Identifikasi Aktif**:
   Menyuntikkan tanda `[LOGGER] MametLogger aktif...` di dalam fase inisiasi (*setup*), sehingga administrator dapat langsung memverifikasi bahwa pengait log telah mengambil kendali.

## Dampak (*Impact*)
Pemonitoran sistem kini bersifat absolut dan *real-time* (waktu nyata). Setiap bit informasi peringatan maupun kerusakan akan langsung terukir di penyimpanan tetap sepersekian milidetik sejak insiden terjadi, memastikan integritas pemonitoran Pilar D3 berjalan 100% tanpa henti.
