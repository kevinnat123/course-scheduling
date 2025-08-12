import sys
import os
import pytest

# Tambahkan path agar bisa impor dao
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dao import genetic_algorithm as ga

def test_ga():
    matakuliah_list = []
    dosen_list = []
    ruang_list = []
    
    result = ga.genetic_algorithm(
        matakuliah_list=matakuliah_list,
        dosen_list=dosen_list,
        ruang_list=ruang_list,
        peluang_mutasi=0.05
    )

    assert result["status"] is True
    assert type(result["data"]) is list
    assert type(result["score"]) is dict