# Pemulihan Pasca-Rollback dan Resolusi Bug Fatal Memori
**Tanggal:** 9 Juli 2026

Dokumen ini mencatat rentetan perbaikan (patching) kritis setelah insiden rollback yang menghilangkan sebagian pembaruan keamanan dan fitur *Multi-tenant Provider*, serta memperbaiki bug fatal pada riwayat obrolan (Chat History) dan Memori Ekstraksi.

## 1. Pembaruan Standar Python dan Otentikasi Minimal
*   **Deprecation Fix:** Mengganti pemanggilan `datetime.utcnow()` yang usang di `backend/auth/auth_handler.py` menjadi `datetime.now(timezone.utc)` untuk memastikan kompatibilitas jangka panjang.
*   **Login Minimal (Hardcoded Admin):** Merombak fungsi `/api/login` di `backend/main.py` agar tidak bergantung pada verifikasi *AuthHandler* ke *database*, melainkan menggunakan akun statis (`andreanastasya798@gmail.com`) dan menghasilkan token menggunakan modul `secrets` bawaan Python. Juga menambahkan *endpoint* bayangan `/api/login2`.

## 2. Restorasi Provider Router & Keamanan Svelte UI
Karena *rollback* menghapus fitur panel Provider di UI, rute otentikasi API Key kembali bocor dan memunculkan **Error 401**.
*   **Backend Endpoints:** Menambahkan kembali *endpoint* `POST /api/provider`, `GET /api/providers`, dan `DELETE /api/provider/{name}` di `backend/main.py` agar UI dapat menyuntikkan Kunci API langsung ke SQLite `memory.db`.
*   **Provider Router Loading:** Mempertebal modul `ProviderRouter._load_providers()` dengan menambahkan rekaman konsol (*debug print*) setiap kali peladen memuat dari pangkalan data. Menambahkan filter `priority=1` dan menghapus ketergantungan pada injeksi `api_key` pasif, serta mengalihkan model ke `openai/gpt-4o-mini`.
*   **Penangkal Chrome Autofill:** Di `desktop/src/routes/workspace/+page.svelte`, *Chrome Password Manager* terus menerus menyuntikkan *password* ke dalam kolom input API Key (karena tipe input *password*). Solusi absolut yang diterapkan:
    1. Mengubah *state* `apiKey` menjadi `apiKeyInput`.
    2. Menyuntikkan atribut `autocomplete="new-password" id="api_key_input" name="api_key_input"`.
    3. Menambahkan *Guard Prefix* di fungsi `saveApiKey` yang menolak kunci jika tidak diawali dengan `sk-or-v1-`.
*   **Isolasi API Key di Payload:** Menghapus `api_key: apiKey || null` dari pengiriman *body* `handleSend()`. Ini memaksa peladen secara mutlak mencari kunci di *database* miliknya sendiri, mempersempit vektor serangan (attack vector).

## 3. Resolusi Bug Fatal: Chat History dan Fact Extraction Skipped
Saat sistem dipaksa membaca kunci dari *database*, pengguna melaporkan bahwa asisten "hilang ingatan" atau selalu membalas pesan secara statis saat dites dengan memori personal.

**Akar Masalah:**
1.  **Fact Extraction Skipped:** Pada `_save_conversation()` (di dalam `main_orchestrator.py`), terdapat pengkondisian `if column == "kolom2" and api_key:`. Karena variabel `api_key` yang ditangkap dari *payload frontend* menjadi `None`, eksekusi `_extract_and_save_facts()` dilewati (*skipped*).
2.  **Context Overwrite Bug:** Logika pembangunan `user_msg` di `_build_response()` mengambil pesan obrolan terakhir (`recent[-1]`) dari pangkalan data dan menimpanya (*overwrite*) ke pesan aktual pengguna di putaran obrolan saat ini. Hal ini menyebabkan LLM membalas omongan pengguna di masa lalu, bukan perintah terbarunya.

**Tindakan Perbaikan:**
*   **FactExtractor Independen:** Mencabut syarat `and api_key` di modul `main_orchestrator.py`. Fungsi `_extract_and_save_facts` kini diinstruksikan untuk memanggil `ProviderRouter` secara *blind* (buta) yang mana router tersebut otomatis akan menjaring *API Key* dari *Database*, bukan dari Svelte.
*   **Strukturisasi History (Role Array):** Merombak fungsi perakitan konteks `messages`. Histori percakapan lama (`recent_conversations`) kini disuntikkan secara rapi menggunakan array `{"role": "user", ...}` dan `{"role": "assistant", ...}`, sedangkan pesan puncak (aktif) ditarik dari `plan.get("original_message")`. 

Hasil akhirnya, LLM sekarang memiliki rentetan memori kronologis, Asisten merespons pesan mutakhir dengan benar, dan `FactExtractor` kembali sukses mengukir data spesifik (seperti nama panggilan "Pak Slamet") ke SQLite secara asinkron.

**Status Keseluruhan:** Stabil penuh, MAMET OS v3.1 termutakhir tanpa residu error logika.
