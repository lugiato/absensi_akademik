# ROADMAP PENGERJAAN PROJECT
# SISTEM ABSENSI HYBRID QR DINAMIS BERBASIS PYTHON

---

# Deskripsi Singkat

Project ini merupakan sistem absensi hybrid (online dan offline) berbasis web menggunakan QR Code dinamis untuk membantu mengurangi potensi kecurangan absensi seperti titip absen, penggunaan screenshot QR lama, dan manipulasi kehadiran.

Sistem menggunakan validasi berbasis waktu, session control oleh dosen, serta validasi lokasi pada mode offline.

---

# Tujuan Project

- Membuat sistem absensi modern berbasis Python
- Menggunakan QR Code dinamis
- Mendukung mode online dan offline
- Mengurangi potensi titip absen
- Membuat validasi absensi berbasis waktu
- Menyimpan data absensi secara otomatis

---

# Konsep Sistem

## Mode Offline
Pada mode offline:
- dosen membuka sesi absensi
- QR kelas ditampilkan
- mahasiswa melakukan absensi
- sistem melakukan validasi lokasi GPS dan waktu

---

## Mode Online
Pada mode online:
- dosen membuka sesi online
- QR kelas ditampilkan selama sesi aktif
- mahasiswa dapat mengunggah screenshot QR melalui sistem
- sistem melakukan validasi waktu dan status sesi

---

# Teknologi Yang Digunakan

## Backend
- Python
- Flask

---

## Frontend
- HTML
- CSS
- JavaScript

---

## Database
- SQLite (pengembangan awal)
- MySQL (pengembangan lanjut)

---

# Library Python

## Flask

```bash
pip install flask
```

## Flask SQLAlchemy

```bash
pip install flask_sqlalchemy
```

## Flask Login

```bash
pip install flask-login
```

## qrcode

```bash
pip install qrcode[pil]
```

## OpenCV

```bash
pip install opencv-python
```

## pyzbar

```bash
pip install pyzbar
```

## geopy

```bash
pip install geopy
```

---

# Software Yang Dibutuhkan

## Wajib
- Visual Studio Code
- Python
- Browser (Chrome / Edge)

---

# Extension VS Code Yang Disarankan

- Python
- Pylance
- HTML CSS Support
- Live Server
- Markdown Preview Enhanced
- Error Lens

---

# Struktur Folder Project

```text
project/
│
├── app.py
├── database.db
│
├── static/
│   ├── css/
│   ├── js/
│   ├── qr/
│   └── images/
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── qr.html
│   ├── admin.html
│   └── attendance.html
│
├── models/
│   ├── user.py
│   ├── session.py
│   └── attendance.py
│
├── routes/
│   ├── auth.py
│   ├── qr.py
│   ├── session.py
│   └── attendance.py
│
└── utils/
    ├── qr_generator.py
    ├── gps_validator.py
    └── token_generator.py
```

---

# Tahapan Pengerjaan

# TAHAP 1 — Persiapan Environment

## Install Python

Cek versi Python:

```bash
python --version
```

---

## Membuat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## Install Library

```bash
pip install flask
pip install flask_sqlalchemy
pip install flask-login
pip install qrcode[pil]
pip install opencv-python
pip install pyzbar
pip install geopy
```

---

# TAHAP 2 — Setup Backend Flask

## Yang Dikerjakan

- membuat app.py
- konfigurasi Flask
- routing dasar
- koneksi database

---

## Target
Aplikasi Flask berhasil berjalan.

---

# TAHAP 3 — Sistem Login

## Fitur

- login mahasiswa
- login dosen
- logout
- session login

---

## Yang Dibutuhkan

- Flask Login
- database users

---

# TAHAP 4 — Database

## Membuat Table

### users

```text
id
nama
email
password_hash
role
device_id
```

---

### sessions

```text
id
mata_kuliah
mode
tanggal
jam_mulai
jam_selesai
status
latitude
longitude
radius
```

---

### attendance

```text
id
user_id
session_id
waktu_absen
status_kehadiran
lokasi
```

---

## Contoh Status Kehadiran

```text
hadir
terlambat
izin
alpha
```

---

# TAHAP 5 — Sistem Session Dosen

## Fitur

Dosen dapat:
- membuka absensi
- menutup absensi
- memilih mode:
  - online
  - offline

---

## Target

Absensi hanya aktif saat dosen membuka sesi.

---

## Session Expired

Session absensi otomatis berakhir ketika waktu sesi selesai.

---

# TAHAP 6 — QR Dinamis

## Yang Dikerjakan

- generate QR otomatis
- token unik
- timestamp dinamis
- auto refresh QR

---

## Target

QR berubah otomatis setiap 30–60 detik.

---

# TAHAP 7 — Sistem Scan QR

## Mode Offline
- mahasiswa melakukan scan QR kelas
- sistem memvalidasi GPS dan waktu

---

## Mode Online
- mahasiswa mengunggah screenshot QR
- sistem melakukan decode QR

---

## Library Yang Digunakan

- OpenCV
- pyzbar

---

# TAHAP 8 — Validasi Sistem

## Validasi Waktu
QR expired otomatis sesuai waktu tertentu.

---

## Validasi Session
QR hanya valid jika sesi absensi aktif.

---

## Validasi GPS
Digunakan sebagai validasi pendukung pada mode offline.

---

## Validasi Device
Optional untuk keamanan tambahan.

---

# TAHAP 9 — Dashboard

## Dashboard Mahasiswa

- melihat QR
- melihat histori absensi

---

## Dashboard Dosen

- membuka sesi
- melihat data kehadiran
- melihat rekap absensi

---

# TAHAP 10 — Pengujian Sistem

## Testing Yang Dilakukan

- test login
- test QR dinamis
- test GPS
- test mode online
- test mode offline
- test upload screenshot QR
- test keamanan dasar

---

# MVP (Minimal Viable Product)

## Fitur Inti Yang Wajib Selesai

- login
- QR dinamis
- session dosen
- mode online
- mode offline
- database absensi

---

# Fitur Tambahan

## Optional

- anti fake GPS
- face recognition
- export PDF
- statistik kehadiran
- Progressive Web App
- aplikasi Android

---

# Pembagian Prioritas

## Prioritas Tinggi

- login
- QR dinamis
- session dosen
- database

---

## Prioritas Menengah

- GPS
- upload screenshot QR

---

## Prioritas Rendah

- AI
- face recognition
- anti spoofing

---

# Tantangan Project

- keamanan QR
- validasi GPS
- koneksi internet
- performa sistem
- upload QR online

---

# Limitasi Sistem

- Sistem bergantung pada koneksi internet
- GPS dapat dipengaruhi akurasi device
- Mode online masih memiliki potensi penyalahgunaan screenshot
- Fake GPS masih memungkinkan pada beberapa device

---

# Estimasi Tingkat Kesulitan

## Backend Python
Menengah.

---

## Frontend
Dasar hingga menengah.

---

## Security System
Menengah.

---

# Kesimpulan

Project ini merupakan sistem absensi hybrid modern berbasis Python yang menggabungkan QR Code dinamis, validasi berbasis waktu, session control oleh dosen, dan dukungan kelas online maupun offline.

Project ini cocok dijadikan tugas akhir karena mencakup:
- backend
- frontend
- database
- keamanan dasar
- validasi lokasi
- pengelolaan session