# Changelog

Semua perubahan penting pada proyek ini akan dicatat di file ini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/id/1.0.0/),
dan proyek ini menggunakan [Semantic Versioning](https://semver.org/lang/id/).

## [0.1.0] - 2026-07-06

### Ditambahkan
- Kernel Main Orchestrator dengan siklus PLAN → COLLECT → DECIDE → RESPOND
- Planning Engine berbasis aturan simbolik (tanpa LLM)
- Evidence Collector modular dengan sumber cache, user memory, RAG, engineer
- Decision Engine dengan decision tree dan confidence threshold
- Tiga kolom chat: Pencarian Cepat, Asisten Pribadi, Engineer
- Engineer Basic dengan kemampuan analisis proyek, baca file, list direktori
- Safety Guard untuk Engineer (persetujuan wajib untuk tindakan berbahaya)
- Code Analyzer untuk mendeteksi framework, routes, komponen
- File Reader untuk menjelajahi struktur proyek
- Frontend Next.js + TailwindCSS dengan UI responsif (desktop 3 kolom, mobile 1 kolom)
- Backend FastAPI + Uvicorn dengan auto-reload
- Deployment ke Vercel melalui GitHub auto-deploy
- Dokumentasi SPESIFIKASI.md (dilindungi .gitignore)

### Status Pengembangan
- Kernel: ✅ Berfungsi penuh
- Kolom 1 (Pencarian Cepat): ⚠️ Fallback (menunggu RAG)
- Kolom 2 (Asisten Pribadi): ⚠️ Fallback (menunggu User Memory)
- Kolom 3 (Engineer Basic): ✅ Analisis, baca file, list direktori
- UI 3 Kolom: ✅ Berfungsi, responsif
- Engineer Write/Execute: ⬜ Perlu persetujuan user (fitur berikutnya)