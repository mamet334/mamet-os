# Riwayat Perubahan: Perbaikan Integrasi API Provider & Pengaturan Kunci AI
**Tanggal**: 9 Juli 2026

## Latar Belakang Masalah
Pengujian pemanggilan asisten pribadi (LLM) di Kolom 2 menghasilkan *error 401 Unauthorized*, di mana asisten justru menampilkan data mentah dari basis data (RAG) ketimbang merespons dengan gaya bahasa manusiawi. Terdapat dua persoalan utama yang saling mengikat:

1. **Hilangnya Fitur UI Penyimpanan Kunci**:
   Antarmuka *Command Center* tidak memiliki fasilitas untuk memasukkan dan menyimpan rahasia *API key* (seperti kunci OpenRouter). Alhasil, *frontend* tak bisa mengirimkan permintaan yang valid, memaksa pengguna memakai jalur belakang (Swagger) yang mana tak terhubung langsung dengan sesi identitas Svelte (`localStorage`).
2. **Kecacatan Logika Indentasi LLM**:
   Dalam `main_orchestrator.py`, eksekusi perintah LLM (`router.chat()`) keliru dikurung (*indented*) ke dalam blok bersyarat `if api_key:`. Akibatnya, jika *frontend* tidak secara eksplisit mengirimkan *API Key* melalui muatan HTTP (karena sistem seharusnya bisa secara mandiri membacanya dari database SQLite), seluruh fungsi kecerdasan buatan akan dilewati (di-*skip*). Karena dilewati, sistem secara naif mengira sedang *offline* dan menggunakan *fallback* berupa ringkasan RAG kaku.

## Resolusi & Perubahan Kode

1. **Injeksi Endpoint Khusus Provider (`backend/main.py`)**:
   Diciptakan sebuah *endpoint* `POST /api/provider` (menyimpan), ditambah `GET /api/providers` (menampilkan), dan `DELETE /api/provider/{name}` (menghapus). Ketiga endpoint ini memberikan kendali CRUD mutlak atas tabel `providers` milik masing-masing profil pengguna pada pangkalan data SQLite (`memory.db`).
2. **Perombakan Ekstensif Panel Pengaturan UI (`desktop/src/routes/workspace/+page.svelte`)**:
   Menyuntikkan seksi antarmuka **Konfigurasi Provider API** di dalam *Command Center*. Antarmuka dirancang jauh lebih estetik dengan fitur:
   - **Dropdown Provider**: Menu pilihan cerdas antara `OpenRouter`, `OpenAI`, `Grok`, dan `Gemini`.
   - **Tabel Provider Dinamis**: Area render data dari `GET /api/providers` yang mengindikasikan status ("Aktif") secara *real-time*, lengkap dengan tombol pencabut ("Hapus") yang memicu *endpoint* DELETE.
3. **Penyempurnaan Eksekutor AI (`backend/orchestrator/main_orchestrator.py`)**:
   - Melepaskan ikatan *indentasi* pada logika `router.chat()`. Ini memastikan Kernel selalu berusaha memanggil memori basis datanya untuk mengambil *API Key* jika *frontend* tidak mengirimkannya di saat itu.
   - Mengikis paksa fitur *fallback* RAG yang tidak membantu. Diganti dengan mekanisme penangkapan *error* yang tegas.
4. **Perbaikan Parameter & Model OpenRouter (`backend/ai/providers/openrouter_provider.py`)**:
   Merespons isu *Error 404* pada *endpoint* `chat/completions`, injeksi `HTTP-Referer` dan `X-Title` (wajib untuk beberapa model pada sistem keamanan OpenRouter) dilakukan. Model bawaan di-paku secara mutlak ke versi stabil `mistralai/mistral-7b-instruct:free` yang menjamin akseptasi *payload* tanpa ditolak oleh sistem hulu.
5. **Dinamisasi Model Reaktif & Migrasi Kolom Skema (`backend/ai/provider_router.py`, UI Svelte)**:
   - Skema pangkalan data `providers` (SQLite) dimigrasikan menggunakan instruksi mandiri *ALTER TABLE* untuk menyertakan ruang penyimpanan `model`.
   - UI *Command Center* disuntikkan efek *dropdown* berganda. Apabila entitas Provider di-*switch* (Misalnya "OpenAI" ke "Grok"), maka daftar Model di bawahnya akan me-*render* katalog yang spesifik merujuk pada ekosistem tersebut.
   - Pangkalan kode `ProviderRouter.chat()` tak lagi statis, melainkan menarik string spesifik dari *database* untuk digandeng ke *payload* peladen hulu.
6. **Pencegahan Intervensi Chrome Autofill & Validasi Input (`desktop/src/routes/workspace/+page.svelte`)**:
   Ditemukan *bug* anomali di mana *Chrome Password Manager* secara otomatis menyuntikkan *password* login ke *field* API Key karena bertipe `password`. Solusi mutlak diterapkan:
   - Penambahan atribut blokir: `<input type="password" autocomplete="new-password" id="api_key_input" name="api_key_input">` untuk membungkam peramban.
   - Refaktor variabel *state* dari `apiKey` menjadi `apiKeyInput` untuk menghindari konflik internal.
   - Pemasangan perlindungan berlapis di fungsi `saveProvider()` yang mendepak API Key OpenRouter jika tidak memiliki prefiks yang sah (yaitu `"sk-or-v1-"`).

7. **Penyelarasan Sisa Residu Referensi Svelte (`desktop/src/routes/workspace/+page.svelte`)**:
   Pasca-pergantian nama *state* ke `apiKeyInput`, sistem *build* Vite sempat lumpuh sementara dengan kesalahan `Can only bind to state or props bind:value={apiKey}`. Akar persoalannya adalah variabel yatim `apiKey` yang masih mengikat ke elemen UI lawas di lekuk *sidebar* sebelah kiri. Pangkalan kode telah disisir untuk menormalisasi *semua* referensi ke `apiKeyInput` (termasuk pada fungsi `handleSend()` dan `saveApiKey()`).

## Dampak (*Impact*)
Arsitektur API *Provider* untuk asisten kini beroperasi secara otonom dari pangkalan data per pengguna, sangat lincah dalam beralih kunci maupun model spesifik (CTH: melompat dari GPT-4o-mini ke Gemini 1.5 Pro via panel Svelte), dan terlepas murni dari kekakuan UI bawaan. Rantai perputaran izin (*auth*) berjalan rapi—mulai dari pilihan *dropdown* bertingkat, perlindungan penuh terhadap intrusi *Password Manager* peramban, eliminasi cacat sintaks kompiler Vite, hingga pemanggilan LLM mutlak tanpa ancaman Error 404 maupun Error 401.
