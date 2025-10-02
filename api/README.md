To install dependencies:
```sh
bun install
```

To run:
```sh
bun run dev
```

open http://localhost:3101

To run list route in terminal:
```sh
bun run list-routes
```

# Struktur Proyek

Berikut adalah struktur direktori proyek:


## 📂 Penjelasan Direktori

- **`app/`** → Konfigurasi utama aplikasi.
- **`controllers/`** → Logika utama untuk menangani request.
- **`middleware/`** → Middleware seperti autentikasi, logging, dll.
- **`middleware/`** → Untuk type serta model yang ada didatabase.
- **`repositories/`** → Query database menggunakan Prisma.
- **`response/`** → Kumpulan respons API.
- **`routes/`** → Definisi rute API.
- **`services/`** → Logika bisnis (akses database, perhitungan, dll.).
- **`types/`** → Definisi tipe TypeScript (opsional).
- **`utils/`** → Kumpulan fungsi bantuan.
- **`validators/`** → Validasi request dengan Zod.
- **`index.ts`** → Entry point aplikasi.

