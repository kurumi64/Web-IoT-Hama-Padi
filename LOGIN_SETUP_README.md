# Setup Sistem Login

Dokumen ini menjelaskan cara mengatur dan menggunakan sistem login baru untuk dashboard Monitoring Alat Hama.

## Fitur yang Ditambahkan

1. **Halaman Login**: Interface login yang indah yang sesuai dengan desain dashboard
2. **Perlindungan Autentikasi**: Semua halaman dashboard dan endpoint API sekarang dilindungi
3. **Fungsi Logout**: Pengguna dapat logout melalui menu dropdown
4. **Manajemen Session**: Manajemen session bawaan Django untuk autentikasi yang aman

## Instruksi Setup

### 1. Buat User Admin

Jalankan perintah berikut untuk membuat user admin awal:

```bash
cd app
python manage.py setup_user
```

Ini akan membuat user dengan:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

### 2. Jalankan Server

```bash
cd app
python manage.py runserver 0.0.0.0:8000
```

### 3. Akses Aplikasi

1. Navigasi ke `http://your-server-ip:8000`
2. Anda akan diarahkan ke halaman login
3. Gunakan kredensial:
   - Username: `admin`
   - Password: `admin123`

## Fitur Keamanan

- **Login Diperlukan**: Semua halaman dashboard dan endpoint API memerlukan autentikasi
- **Perlindungan CSRF**: Semua form dilindungi dari serangan CSRF
- **Keamanan Session**: Manajemen session aman Django
- **Validasi Password**: Validasi password bawaan Django

## Manajemen User

### Membuat User Tambahan

Anda dapat membuat user tambahan melalui:

1. **Interface Admin Django**: Kunjungi `/admin/` dan gunakan kredensial admin
2. **Management Command**: Buat command khusus seperti `setup_user.py`
3. **Secara Program**: Gunakan model User Django dalam kode Anda

### Mengubah Password

1. Login ke dashboard
2. Klik dropdown user di pojok kanan atas
3. Pilih "Pengaturan" (Settings) - Anda mungkin perlu mengimplementasikan fitur ini
4. Atau gunakan interface admin Django untuk mengubah password

## File yang Dimodifikasi/Dibuat

### File Baru:
- `app/dashboard/templates/dashboard/login.html` - Template halaman login
- `app/dashboard/management/commands/setup_user.py` - Command setup user

### File yang Dimodifikasi:
- `app/dashboard/views.py` - Menambahkan view login/logout dan decorator @login_required
- `app/dashboard/urls.py` - Menambahkan pola URL login/logout
- `app/app/settings.py` - Menambahkan konfigurasi URL login
- `app/dashboard/templates/dashboard/index.html` - Memperbarui link logout

## Perlindungan API

Semua endpoint API sekarang dilindungi dengan decorator `@login_required`:

- `/api/latest-data/`
- `/api/system-data/`
- `/api/location-data/`
- `/api/table-data/`
- `/api/detection-statistics/`
- `/api/latest-detection/`

## Troubleshooting

### Jika tidak bisa login:
1. Pastikan Anda telah menjalankan command `setup_user`
2. Periksa bahwa server sedang berjalan
3. Verifikasi username dan password sudah benar
4. Periksa log Django untuk error

### Jika halaman redirect ke login:
1. Ini adalah perilaku yang diharapkan - semua halaman memerlukan autentikasi
2. Pastikan Anda sudah login
3. Periksa bahwa session Anda belum expired

### Untuk reset password admin:
```bash
cd app
python manage.py changepassword admin
```

## Rekomendasi Keamanan

1. **Ubah Password Default**: Ubah password admin setelah login pertama
2. **Gunakan HTTPS**: Di production, selalu gunakan HTTPS
3. **Password Kuat**: Terapkan kebijakan password yang kuat
4. **Update Berkala**: Jaga Django dan dependencies tetap terupdate
5. **Session Timeout**: Pertimbangkan untuk mengimplementasikan session timeout
6. **Rate Limiting**: Pertimbangkan untuk menambahkan rate limiting untuk percobaan login

## Kustomisasi

### Styling Halaman Login

Halaman login menggunakan CSS khusus dalam template. Anda dapat memodifikasi:
- Warna dan gradien di bagian `<style>`
- Layout dan spacing
- Font dan icon

### Menambahkan Registrasi User

Untuk menambahkan fungsi registrasi user:
1. Buat view dan template registrasi
2. Tambahkan pola URL untuk registrasi
3. Implementasikan verifikasi email jika diperlukan
4. Tambahkan link registrasi ke halaman login

### Menambahkan Reset Password

Untuk menambahkan fungsi reset password:
1. Konfigurasi pengaturan email di `settings.py`
2. Tambahkan URL dan view reset password
3. Buat template reset password
4. Tambahkan link "Lupa Password" ke halaman login 