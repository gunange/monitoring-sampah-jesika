# Monitoring Sampah

Aplikasi berbasis web untuk memantau kondisi tempat sampah secara real-time menggunakan teknologi Computer Vision.

## 📜 Daftar Isi

- [Tentang Proyek](#-tentang-proyek)
- [Arsitektur](#-arsitektur)
- [Dibangun Dengan](#-dibangun-dengan)
- [Fitur Utama](#-fitur-utama)
- [Memulai](#-memulai)
  - [Prasyarat](#prasyarat)
  - [Instalasi](#instalasi)
- [Lisensi](#-lisensi)

## 🌟 Tentang Proyek

**Monitoring Sampah** adalah sebuah sistem cerdas yang dirancang untuk memberikan solusi efisien dalam manajemen limbah. Aplikasi ini memungkinkan petugas atau admin untuk memantau tingkat kepenuhan tempat sampah dari jarak jauh melalui dasbor interaktif. Ketika tempat sampah terdeteksi penuh oleh sistem Computer Vision, notifikasi akan dikirim secara real-time, memungkinkan pengambilan tindakan yang cepat dan efisien.

## 🏗️ Arsitektur

Proyek ini mengadopsi arsitektur berbasis layanan yang terpisah, terdiri dari tiga komponen utama:

1.  **`vue/` (Frontend)**: Antarmuka pengguna yang dibangun dengan Vue.js. Bertanggung jawab untuk menampilkan dasbor monitoring, data, dan notifikasi kepada pengguna.
2.  **`api/` (Backend)**: Server utama yang dibangun dengan Node.js dan TypeScript. Mengelola logika bisnis, otentikasi pengguna, data, dan komunikasi real-time melalui WebSockets.
3.  **`ml/` (Machine Learning)**: Layanan yang dibangun dengan Python. Bertugas untuk menganalisis feed video dari kamera menggunakan model Machine Learning (KNN) untuk mendeteksi kondisi tempat sampah.

## 🛠️ Dibangun Dengan

Berikut adalah teknologi utama yang digunakan dalam proyek ini:

| Komponen          | Teknologi                                                              |
| ----------------- | ---------------------------------------------------------------------- |
| **Frontend (vue)**| [Vue.js](https://vuejs.org/), [Vite](https://vitejs.dev/), [Pinia](https://pinia.vuejs.org/), [PrimeVue](https://www.primefaces.org/primevue/) |
| **Backend (api)** | [Node.js](https://nodejs.org/), [Express.js](https://expressjs.com/), [TypeScript](https://www.typescriptlang.org/), [Prisma](https://www.prisma.io/), [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) |
| **ML (ml)**       | [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/) (atau Flask), OpenCV, Scikit-learn |

## ✨ Fitur Utama

-   Dasbor monitoring real-time.
-   Sistem otentikasi dengan peran pengguna (Admin, Petugas).
-   Deteksi objek (kondisi sampah) menggunakan Computer Vision.
-   Notifikasi instan melalui WebSockets dan suara alarm.
-   Manajemen data pengguna dan perangkat.

## 🚀 Memulai

Untuk menjalankan proyek ini secara lokal, ikuti langkah-langkah berikut.

### Prasyarat

Pastikan Anda telah menginstal perangkat lunak berikut:

-   [Node.js](https://nodejs.org/en/download/) (v18.x atau lebih baru)
-   [Python](https://www.python.org/downloads/) (v3.9 atau lebih baru)
-   `npm` atau `yarn`

### Instalasi

1.  **Clone repository ini:**
    ```sh
    git clone <URL_REPOSITORY_ANDA>
    cd monitoring-sampah
    ```

2.  **Setup Backend (`api/`):**
    ```sh
    cd api
    npm install
    cp .env.example .env 
    # Sesuaikan variabel lingkungan di dalam file .env (misalnya, koneksi database)
    npx prisma generate
    npx prisma migrate dev
    npm run dev
    ```
    Server backend akan berjalan di port yang ditentukan di file `.env`.

3.  **Setup Machine Learning (`ml/`):**
    ```sh
    cd ../ml
    python -m venv .venv
    source .venv/bin/activate  # Pada Windows, gunakan: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env
    # Sesuaikan variabel lingkungan di dalam file .env
    # Jalankan aplikasi (contoh menggunakan uvicorn untuk FastAPI)
    uvicorn index:app --reload 
    ```
    Server ML akan berjalan di port yang ditentukan.

4.  **Setup Frontend (`vue/`):**
    ```sh
    cd ../vue
    npm install
    cp .env.example .env
    # Sesuaikan variabel lingkungan di dalam file .env (terutama URL API)
    npm run dev
    ```
    Aplikasi Vue akan berjalan dan dapat diakses melalui browser.

> **Catatan:** Pastikan ketiga layanan (api, ml, vue) berjalan secara bersamaan agar aplikasi berfungsi sepenuhnya.

## 📄 Lisensi

Didistribusikan di bawah Lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.
