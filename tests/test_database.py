import sys, os, pytest
from bson.objectid import ObjectId
from unittest.mock import patch
from pymongo import errors

# Tambahkan path ke module utama
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dao import Database
import config  # pastikan config.MONGO_DB ada

# ========================================
# Tes Connection
# ========================================
def test_connection_failure_handled(capfd):
    with patch('dao.MongoClient', side_effect=errors.ConnectionFailure("mocked failure")):
        db = Database("testdb")
        out, _ = capfd.readouterr()
        assert "Gagal Membuat Koneksi" in out

def test_generic_exception_handled(capfd):
    with patch('dao.MongoClient', side_effect=Exception("mocked other error")):
        db = Database("testdb")
        out, _ = capfd.readouterr()
        assert "Gagal membuat koneksi" in out

# Collection sementara untuk testing
TEST_COLLECTION = "test_collection"

# ========================================
# Database
# ========================================
@pytest.fixture(scope="module")
def db():
    return Database(config.MONGO_DB)

@pytest.fixture
def clean_collection(db):
    # Bersihkan data sebelum setiap test
    db.delete_many(TEST_COLLECTION, {})
    yield
    db.delete_many(TEST_COLLECTION, {})  # Bersihkan setelah test juga

# ========================================
# Tes Insert One
# ========================================
def test_insert_one_success(db):
    data = {"nama": "Ken", "role": "ADMIN"}
    inserted = db.insert_one(TEST_COLLECTION, data)
    assert inserted["status"] is True
    assert inserted["message"] == "Data berhasil ditambahkan"

# ========================================
# Tes Find One
# ========================================
def test_find_one_not_found(db):
    result = db.find_one(TEST_COLLECTION, {"nama": "Paijo"})
    assert result["status"] is False
    assert result["message"] == "Data tidak ditemukan"

def test_find_one_found(db):
    result = db.find_one(TEST_COLLECTION, {"nama": "Ken"})
    assert result["status"] is True
    assert result["message"] == "Data ditemukan"

# ========================================
# Tes Update One
# ========================================
def test_update_one_not_found(db):
    params = {"role": "SARPRAS"}
    updated = db.update_one(TEST_COLLECTION, {"nama": "Paijo"}, params)
    assert updated["status"] is False
    assert updated["message"] == "Tidak ada data yang diperbarui"

def test_update_one_found(db):
    params = {"role": "SARPRAS"}
    updated = db.update_one(TEST_COLLECTION, {"nama": "Ken"}, params)
    assert updated["status"] is True
    assert updated["message"] == "Data berhasil diperbarui"

# ========================================
# Tes Delete One
# ========================================
def test_delete_one_not_found(db):
    deleted = db.delete_one(TEST_COLLECTION, {"nama": "Paijo"})
    assert deleted["status"] is False
    assert deleted["message"] == "Data tidak ditemukan"

def test_delete_one_found(db):
    deleted = db.delete_one(TEST_COLLECTION, {"nama": "Ken"})
    assert deleted["status"] is True
    assert deleted["message"] == "Data berhasil dihapus"

# ========================================
# Tes Insert Many
# ========================================
def test_insert_many_success(db):
    items = [{"x": i} for i in range(15)]
    inserted = db.insert_many(TEST_COLLECTION, items)
    assert inserted["status"] is True
    assert inserted["message"] == "Data berhasil ditambahkan"

# ========================================
# Tes Update Many
# ========================================
def test_update_many(db):
    db.insert_many(TEST_COLLECTION, [
        {"kelas": "A"}, {"kelas": "A"}
    ])
    result = db.update_many(TEST_COLLECTION, {"kelas": "A"}, {"kelas": "B"})
    assert result["status"] is True
    assert result["modified_count"] == 2

    result = db.update_many(TEST_COLLECTION, {"kelas": "A"}, {"kelas": "B"})
    assert result["status"] is False
    assert result["modified_count"] == 0

# ========================================
# Tes Find Many
# ========================================
def test_find_many_with_sort(db, clean_collection):
    db.insert_many(TEST_COLLECTION, [
        {"nama": "A", "urut": 2},
        {"nama": "B", "urut": 1}
    ])
    result = db.find_many(TEST_COLLECTION, sort=[("urut", 1)])
    print(result)
    assert result["status"] is True
    assert result["data"][0]["nama"] == "B"  # Urut naik

def test_find_many_and_pagination(db, clean_collection):
    items = [{"x": i} for i in range(15)]
    db.insert_many(TEST_COLLECTION, items)

    result = db.find_many(TEST_COLLECTION)
    assert result["status"] is True
    assert len(result["data"]) == 15

    paged = db.find_many_page(TEST_COLLECTION, {}, page=2, per_page=10, sort=[("x", 1)])
    assert len(paged["data"]) == 5  # sisa halaman 2

# ========================================
# Tes Count Document
# ========================================
def test_count_documents(db, clean_collection):
    db.insert_many(TEST_COLLECTION, [
        {"jenis": "teori"}, {"jenis": "teori"}, {"jenis": "praktikum"}
    ])
    result = db.count_documents(TEST_COLLECTION, {"jenis": "teori"})
    assert result["status"] is True
    assert result["count"] == 2

# ========================================
# Tes PyMongo Error
# ========================================
def test_insert_with_pymongo_error(db):
    # Simulasikan error dengan collection illegal (misal: None atau illegal name)
    result = db.find_one("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]

    result = db.find_many("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]
    
    result = db.find_many_page("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]
    
    result = db.insert_one("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]

    result = db.insert_many("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]

    result = db.update_one("", {}, {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]

    result = db.update_many("", {}, {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]

    result = db.delete_one("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]
    
    result = db.delete_many("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]

    result = db.count_documents("", {"nama": "Ken"})
    assert result["status"] is False
    assert "pymongo" in result["message"]