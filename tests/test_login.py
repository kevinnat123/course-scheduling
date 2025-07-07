import sys
import os
import pytest

# Tambahkan path agar bisa impor dao
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dao.loginDao import loginDao
loginDao = loginDao()

# ========================================
# Tes SignUp
# ========================================
def test_sign_up():
    result = loginDao.signUp("admin", "admin", "admin123")
    assert result["status"] is True
    assert result["message"] == 'Data berhasil ditambahkan'

# ========================================
# Tes jika user tidak ditemukan
# ========================================
def test_no_account():
    result = loginDao.verify_user("admin", "admin123")
    assert result["status"] is False
    assert result["message"] == 'Anda tidak punya akun!'

# ========================================
# Tes jika password salah
# ========================================
def test_wrong_password():
    result = loginDao.verify_user("kevinnat", "salah")
    assert result["status"] is False
    assert result["message"] == 'Username atau password salah'

# ========================================
# Tes jika program studi tidak ditemukan
# (khusus untuk KAPRODI)
# ========================================
def test_program_studi_not_found():
    result = loginDao.verify_user("not_found", "00")
    assert result["status"] is False
    assert result["message"] == 'Program Studi anda tidak ditemukan!'

# ========================================
# Tes login berhasil
# ========================================
def test_success():
    result = loginDao.verify_user("kevinnat", "ken")
    assert result["status"] is True
    assert result["message"] == 'Login berhasil'
    assert "data" in result  # validasi ada field data
