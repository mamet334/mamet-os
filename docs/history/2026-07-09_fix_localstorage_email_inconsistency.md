# Riwayat Perubahan: Penyeragaman Kunci Sesi (Local Storage) Frontend
**Tanggal**: 9 Juli 2026

## Latar Belakang Masalah
Setelah fitur akun multi-pengguna diterapkan di sisi peladen (*Backend*), antarmuka (*Frontend*) MAMET OS Svelte didapati masih mengirim parameter `email=default` dan `email=default@mamet.os` pada beberapa pemanggilan antarmuka pemrograman aplikasi (API) seperti `/api/budget`, `/api/status`, dan saat interaksi *chat*.

Hasil audit menemukan adanya **inkonsistensi penamaan kunci variabel di `localStorage` peramban (browser)**:
*   Saat proses *Login/Register* di `routes/+page.svelte`, sistem menyimpan data di laci bernama `'email'`.
*   Namun saat memasuki ruang *Dashboard* dan *Workspace*, komponen di sana (seperti `routes/dashboard/+page.svelte`) menggunakan atau mengharapkan data di laci bernama `'mamet_user_email'`.
*   Akibatnya, saat *Workspace* berupaya mengambil email pengguna, nilai yang dikembalikan adalah *null/undefined*, yang lantas memaksa Svelte untuk menggunakan identitas cadangan (yaitu `"default"`).

## Resolusi & Perubahan Kode
Kami melakukan standardisasi kunci ke seluruh ekosistem Svelte dengan menetapkan variabel **`'mamet_user_email'`** sebagai acuan tunggal (*single source of truth*) yang paten:

1. **`desktop/src/routes/+page.svelte` (Login/Register)**
   Dimodifikasi agar fungsi injeksi token tidak lagi memakai `'email'`, melainkan `localStorage.setItem('mamet_user_email', email);`
2. **`desktop/src/routes/dashboard/+page.svelte` (Dashboard)**
   Logika di dalam fungsi `onMount` dan `logout()` diubah agar membaca, serta menghancurkan `localStorage.getItem('mamet_user_email')` dengan bersih.
3. **`desktop/src/routes/workspace/+page.svelte` (Tiga Kolom)**
   Nilai dasar identitas `userEmail` (yang sebelumnya menggunakan *string default@mamet.os*) dilucuti, diganti sepenuhnya dengan pendelegasian dinamis dari nilai `localStorage` di laci yang sama.

## Dampak (*Impact*)
Masalah kebocoran data terpecahkan. Kini seluruh pemanggilan *endpoint* backend secara murni mewakili kredensial (alamat email) pengguna yang sesungguhnya sedari layar awal *login* hingga masuk jauh ke inti sistem. Pemisahan memori tiap *user* dapat beroperasi dengan presisi mutlak.
