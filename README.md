# Flask Application

### Cara Menjalankan

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
