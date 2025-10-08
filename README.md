# Proyek Penjadwalan Mata Kuliah Otomatis menggunakan **Algoritma Genetika**
Aplikasi sederhana berbasis website yang ditujukan untuk membantu proses penjadwalan mata kuliah dengan menerapkan **Algoritma Genetika** sebagai dasar otomatisasi penjadwalan. Dibangun dengan menggunakan HTML, Bootstrap, JavaScript, dan Python serta MongoDB sebagai basis data.

## Fitur
- Login
- Form data dosen, mata kuliah, dan ruangan
- Automatisasi Penjadwalan dengan Algoritma Genetika

## Tech Stack
- Frontend   : HTML, Bootstrap, JavaScript (jQuery)
- Backend    : Python (Flask)

## Version
- V4.0 - Deployed

  Secara keseluruhan, program berjalan dengan baik seperti yang diharapkan dan proses penjadwalan sudah bisa dilakukan dan telah melewati pengujian dengan menggunakan dataset mata kuliah S1 TI.

- V5.0 - Dalam pengembangan... 

### Cara Menjalankan Menggunakan Local
1. Buat virtual environment
   `python -m venv myenv`
2. Install package
   `pip install -r requirements.txt`
3. Aktifkan virtual environment
   `bash source venv/bin/activate`
4. Jalankan aplikasi Flask
   `python app.py`

### Test
1. Install package
   `pip install pytest coverage`
2. Run Test Program + Coverage Program
   `coverage run -m pytest tests/`
3. Coverage Report
   `coverage report` ( Tampilkan laporan di terminal )
   `coverage html` ( Buat laporan HTML lengkap )
