# Karyawan Absensi Web Application

## Deskripsi

Aplikasi web ini adalah sistem absensi untuk karyawan yang memungkinkan pengguna untuk mencatat kehadiran mereka setiap hari. Fitur utama termasuk:

- **Dashboard Admin**: Untuk mengelola pengumuman dan melihat aktivitas absensi.
- **Halaman Pengguna**: Untuk melakukan absensi dan melihat pengumuman.
- **Halaman Profil**: Untuk melihat informasi profil pengguna.


## Fitur Utama

- **Absensi Karyawan**: Pengguna dapat mengisi formulir absensi dengan alasan izin opsional.
- **Pengecekan Absensi**: Sistem mencegah pengguna melakukan absensi lebih dari satu kali per hari.
- **Pengumuman**: Admin dapat membuat dan mengelola pengumuman yang dapat dilihat oleh pengguna.
- **Pengecekan otomatis**: Untuk mengelola ketidak hadiran karyawan secara otomatis.
- **Refresh Otomatis**: Untuk merefresh ulang data absensi setiap jam 00:00.
- **Export ke Excel**: Untuk mengexport agar memudahkan admin untuk mendata.

## Persyaratan

Sebelum menjalankan aplikasi ini, pastikan Anda memiliki:

- Python 3.x
- MySQL
- Pustaka Python: Flask, Flask-Login, Flask-MySQL, dan pustaka lainnya yang diperlukan

## Instalasi

1. **Clone Repositori**

   ```bash
   git clone <URL_REPOSITORI>
   cd <NAMA_FOLDER>
   ```

2. **Buat dan Aktifkan Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Windows: venv\Scripts\activate
   ```

3. **Instal Dependensi**

   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Database**

   - Buat database di MySQL/MariaDB dan impor schema yang diperlukan.
   - Edit file konfigurasi (misalnya, `config.py`) untuk memasukkan kredensial database Anda.

5. **Jalankan Aplikasi**

   ```bash
   flask run
   ```

   Aplikasi akan berjalan pada `http://127.0.0.1:5000/` secara default.

## Penggunaan

- **Dashboard Admin**: Akses dengan login sebagai admin. Admin dapat menambahkan dan mengelola pengumuman.
- **Halaman Pengguna**: Pengguna dapat melakukan absensi dan melihat pengumuman.
- **Halaman Profil**: Pengguna dapat melihat informasi profil dan absensi mereka.

## Rute Aplikasi

- `/`: Halaman utama aplikasi
- `/attendance`: Rute untuk melakukan absensi
- `/profile`: Halaman profil pengguna
- `/user_announcements`: Halaman untuk melihat pengumuman
- `/check_attendance`: Rute untuk memeriksa apakah pengguna sudah melakukan absensi hari ini

## Penanganan Kesalahan

Jika Anda menghadapi kesalahan atau masalah, periksa log kesalahan di terminal dan pastikan semua konfigurasi telah diatur dengan benar.

## Lisensi

Aplikasi ini dirilis di bawah lisensi MIT. Lihat file LICENSE untuk detail lebih lanjut.

## Kontak

Jika Anda memiliki pertanyaan atau memerlukan bantuan, hubungi [email@example.com](mailto:email@example.com).

---

Silakan sesuaikan informasi seperti URL repositori, nama folder, dan detail kontak sesuai kebutuhan Anda.