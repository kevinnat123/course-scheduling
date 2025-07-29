import random, copy, traceback
from collections import defaultdict

class JadwalKuliah:
    def __init__(
            self, 
            kode_matkul:str, kode_dosen:str, sks_akademik:int, kode_ruangan:str, kapasitas:int, 
            hari:str, jam_mulai:int, jam_selesai:int, 
            tipe_kelas:str, program_studi:str, team_teaching:bool=False):
        self.kode_matkul = kode_matkul
        self.kode_dosen = kode_dosen
        self.sks_akademik = sks_akademik
        self.kode_ruangan = kode_ruangan
        self.kapasitas = kapasitas
        self.hari = hari
        self.jam_mulai = jam_mulai
        self.jam_selesai = jam_selesai
        self.tipe_kelas = tipe_kelas  # 'TEORI' atau 'PRAKTIKUM' atau 'INTERNATIONAL'
        self.program_studi = program_studi
        self.team_teaching = team_teaching

# TO BE CHECKED:
# (20)  Jadwal Ruangan Bertabrakan                                  >> ruangan_bentrok          (DONE)
# (20)  Jadwal Dosen Bertabrakan                                    >> dosen_bentrok            (DONE)
# (20)  Jadwal Dosen dan Asisten Berjalan Bersamaan                 >> asdos_nabrak_dosen       (DONE)
# (15)  Dosen Tetap Tidak Mengajar                                  >> dosen_nganggur           (DONE)
# (15)  Kelas Dosen atau Asisten Hilang atau Tidak Lengkap          >> kelas_gaib               (DONE)
# (15)  Solo Team_Teaching                                          >> solo_team
# (15)  Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19    >> diluar_jam_kerja         (DONE)
# (10)  Beban SKS Dosen melebihi 12 sks                             >> dosen_overdosis          (DONE)
# (10)  Cek Total Kelas Bisa Cangkup Semua Mahasiswa                >> kapasitas_kelas_terbatas (DONE)
# (5)   Tipe Ruangan Tidak Sesuai                                   >> tipe_ruang_salah         (DONE)
# (5)   Tidak Sesuai dengan permintaan / request dosen              >> melanggar_preferensi     (DONE)
BOBOT_PENALTI = {
    "ruangan_bentrok": 20,
    "dosen_bentrok": 20,
    "asdos_nabrak_dosen": 20,
    "dosen_nganggur": 15,
    "kelas_gaib": 15,
    "solo_team": 15,
    "diluar_jam_kerja": 15,
    "dosen_overdosis": 10,
    "kapasitas_kelas_terbatas": 10,
    "tipe_ruang_salah": 5,
    "melanggar_preferensi": 5,

    "weekend_class": 10,
    "istirahat": 5,
}

def convertOutputToDict(jadwal_list):
    """
    Menkonversi object jadwal menjadi dictionary.

    Returns:
        dict: Jadwal dalam bentuk dictionary.
    """

    jadwal = []

    for sesi in jadwal_list:
        s = {}
        s['kode_matkul'] = sesi.kode_matkul
        s['kode_dosen'] = sesi.kode_dosen
        s['sks_akademik'] = sesi.sks_akademik
        s['kode_ruangan'] = sesi.kode_ruangan
        s['kapasitas'] = sesi.kapasitas
        s['hari'] = sesi.hari
        s['jam_mulai'] = sesi.jam_mulai
        s['jam_selesai'] = sesi.jam_selesai
        s['tipe_kelas'] = sesi.tipe_kelas  # 'TEORI' atau 'PRAKTIKUM'
        s['program_studi'] = sesi.program_studi
        jadwal.append(s)

    return jadwal

def safe_append_LO(mapping, key, item):
    if item not in mapping.setdefault(key, []):
        mapping[key].append(item)

def safe_remove_LO(mapping, key, item):
    if item in mapping.get(key, []):
        mapping[key].remove(item)

def move_item_LO(mapping, old_key, new_key, item):
    safe_remove_LO(mapping, old_key, item)
    safe_append_LO(mapping, new_key, item)

def is_schedule_fit(jam_mulai, sks, preferensi_jam, available_schedule):
    range_time = range(jam_mulai, jam_mulai + sks + 1)
    return all(j in preferensi_jam and j in available_schedule for j in range_time) and jam_mulai != 12

def is_some_lecture_not_scheduled(jadwal_list=None, matakuliah_list=[], dosen_list=[]):
    matkul_take_all_lecture = [matkul["kode"] for matkul in matakuliah_list if matkul.get("take_all_lecture")]
    scheduled_dosen = set(sesi.kode_dosen for sesi in jadwal_list if sesi.kode_matkul[:5] not in matkul_take_all_lecture)
    set_dosen_tetap = set(dosen["nip"] for dosen in dosen_list if dosen["status"] == "TETAP")
    all_dosen_tetap_scheduled = all(dosen in scheduled_dosen for dosen in set_dosen_tetap)
    if not all_dosen_tetap_scheduled:
        return True, [dosen for dosen in set_dosen_tetap if dosen not in scheduled_dosen]
    else:
        return False, []

def find_available_schedule(jadwal_by:dict, kode:str, hari:str, preferensi_jam:list=[]):
    """
    Mencari waktu yang tersedia dari jadwal yang sudah ada berdasarkan hari yang dipilih.

    Args:
        jadwal (list): List jadwal ruangan / dosen yang sudah ada.
        kode (str): Kode yang akan diperiksa (kode ruangan / nip).
        hari (str): Hari yang akan diperiksa jadwalnya.

    Returns:
        list: List jadwal yang bisa digunakan (jam).
    """
    
    pilihan_jam = range(7, 19 + 1) if hari != "SABTU" else range(7, 13 + 1)
    
    jadwal_sesuai_hari = [sesi for sesi in jadwal_by[kode] if sesi.hari == hari] if jadwal_by.get(kode, []) else []
    used_jam = set()
    for sesi in jadwal_sesuai_hari:
        used_jam.update(range(sesi.jam_mulai, sesi.jam_selesai))

    if preferensi_jam:
        preferensi_jam = set(preferensi_jam)
        return [h for h in pilihan_jam if h not in used_jam and h in preferensi_jam]
    else:
        return [h for h in pilihan_jam if h not in used_jam]

def angka_ke_huruf(n: int):
    """
    Generate alphabet (A-Z) dari angka (n) yang diberikan.

    Args:
        n (int): Angka yang ingin diparsing ke alphabet.

    Returns:
        chr|None: Alphabet yang sesuai dengan angka yang diberikan.
    """

    if 1 <= int(n) <= 26:
        return chr(64 + n)  # Karena ord('A') = 65
    elif 27 <= int(n) <= 52:
        return "A" + chr(64 + n - 26)
    else:
        return None  # Diluar jangkauan 1-26

def switch_koor_matkul(jadwal:list, dosen_dict:dict, matakuliah_dict:dict):
    seen_kode_matkul = set()
    for sesi in jadwal:
        if sesi.kode_dosen == "AS":
            continue
        if sesi.kode_matkul[:5] in seen_kode_matkul:
            continue
        if sesi.kode_matkul[5:6] != "A":
            continue
        seen_kode_matkul.add(sesi.kode_matkul[:5])

        matkul = matakuliah_dict.get(sesi.kode_matkul[:5])
        dosen = dosen_dict.get(sesi.kode_dosen)
        if dosen["status"] == "TETAP" and dosen.get("prodi") != matkul.get("prodi"):
            continue

        # Cari sesi-sesi yang berkaitan
        semua_sesi = [s for s in jadwal if s.kode_matkul.startswith(sesi.kode_matkul[:5])]
        sesi_tetap = next(
            (s for s in semua_sesi if s.kode_dosen != "AS" and 
             dosen_dict.get(s.kode_dosen, {}).get("status") == "TETAP" and 
             dosen_dict.get(s.kode_dosen, {}).get("prodi") == matkul.get("prodi")), 
            None
        )
        if not sesi_tetap:
            continue
        
        kode1 = sesi.kode_matkul[:6]
        kode2 = sesi_tetap.kode_matkul[:6]

        # Ganti semua sesi kode_matkul yang match
        for s in semua_sesi:
            if s.kode_matkul.startswith(kode1):
                s.kode_matkul = s.kode_matkul.replace(kode1, "TEMP")
            elif s.kode_matkul.startswith(kode2):
                s.kode_matkul = s.kode_matkul.replace(kode2, kode1)
        for s in semua_sesi:
            if s.kode_matkul.startswith("TEMP"):
                s.kode_matkul = s.kode_matkul.replace("TEMP", kode2)

    return jadwal

def find_missing_course(jadwal:list, matakuliah_list:list):
    kode_matkul = []
    for matkul in matakuliah_list:
        kode_matkul.append(matkul['kode'])

    sesi_matkul = []
    for sesi in jadwal:
        if sesi.kode_dosen != "AS" and sesi.kode_matkul[:-1] not in sesi_matkul:
            sesi_matkul.append(sesi.kode_matkul[:-1])

    missing = []
    for kode in kode_matkul:
        if kode not in sesi_matkul:
            missing.append(kode)

    return missing

def hitung_beban_sks_dosen_all(jadwal:list, dosen_list:list, matkul_by_kode:dict):
    beban_dosen = {}
    for dosen in dosen_list:
        nip = dosen["nip"]
        mataKuliah = {}
        sbs = []
        seen_mataKuliah = set()
        for sesi in jadwal:
            if sesi.kode_dosen != nip:
                continue

            matkul = matkul_by_kode.get(sesi.kode_matkul[:5])
            if matkul.get("take_all_lecture"):
                continue

            count_dosen = len([
                team for team in jadwal 
                if team.kode_matkul == sesi.kode_matkul and team.kode_dosen != sesi.kode_dosen
            ]) + 1
            if f"{sesi.kode_matkul[:5]}{count_dosen}" not in mataKuliah: 
                mataKuliah[f"{sesi.kode_matkul[:5]}{count_dosen}"] = {"sks": 0, "jml_kelas": 0}

            if f"{sesi.kode_matkul[:5]}{count_dosen}" not in seen_mataKuliah:
                sks = sesi.sks_akademik / count_dosen
                mataKuliah[f"{sesi.kode_matkul[:5]}{count_dosen}"]["sks"] += sks
            seen_mataKuliah.add(f"{sesi.kode_matkul[:5]}{count_dosen}")

            mataKuliah[f"{sesi.kode_matkul[:5]}{count_dosen}"]["jml_kelas"] += 1
            
        for matkul, detail in mataKuliah.items():
            sbs.append(((1/3) * detail["sks"]) * ((2 * detail["jml_kelas"]) + 1))
        
        beban_dosen[nip] = sum(sbs)

    return beban_dosen

def hitung_beban_sks_dosen_specific(jadwal:list, kode_dosen:str, matkul_by_kode:dict):
    nip = kode_dosen
    mataKuliah = {}
    sbs = []
    seen_mataKuliah = set()
    for sesi in jadwal:
        if sesi.kode_dosen != nip:
            continue

        matkul = matkul_by_kode.get(sesi.kode_matkul[:5])
        if matkul.get("take_all_lecture"):
            continue

        count_dosen = len([
            team for team in jadwal 
            if team.kode_matkul == sesi.kode_matkul and team.kode_dosen != sesi.kode_dosen
        ]) + 1
        if f"{sesi.kode_matkul[:5]}{count_dosen}" not in mataKuliah: 
            mataKuliah[f"{sesi.kode_matkul[:5]}{count_dosen}"] = {"sks": 0, "jml_kelas": 0}

        if f"{sesi.kode_matkul[:5]}{count_dosen}" not in seen_mataKuliah:
            sks = sesi.sks_akademik / count_dosen
            mataKuliah[f"{sesi.kode_matkul[:5]}{count_dosen}"]["sks"] += sks
        seen_mataKuliah.add(f"{sesi.kode_matkul[:5]}{count_dosen}")

        mataKuliah[f"{sesi.kode_matkul[:5]}{count_dosen}"]["jml_kelas"] += 1
            
    for kode_matkul, detail in mataKuliah.items():
        sbs.append(((1/3) * detail["sks"]) * ((2 * detail["jml_kelas"]) + 1))

    return sum(sbs)

def sync_team_teaching(sesi_dosen:object, jadwal:list, jadwal_dosen:dict, jadwal_ruangan:dict):
    for sesi_lain in jadwal:
        if sesi_lain.kode_matkul == sesi_dosen.kode_matkul and sesi_lain.kode_dosen != sesi_dosen.kode_dosen:
            safe_remove_LO(jadwal_dosen, sesi_lain.kode_dosen, sesi_lain)
            safe_remove_LO(jadwal_ruangan, sesi_lain.kode_ruangan, sesi_lain)
            sesi_lain.hari = sesi_dosen.hari
            sesi_lain.jam_mulai = sesi_dosen.jam_mulai
            sesi_lain.jam_selesai = sesi_dosen.jam_selesai
            sesi_lain.kode_ruangan = sesi_dosen.kode_ruangan
            sesi_lain.kapasitas = sesi_dosen.kapasitas
            sesi_lain.tipe_kelas = sesi_dosen.tipe_kelas
            sesi_lain.team_teaching = sesi_dosen.team_teaching
            safe_append_LO(jadwal_dosen, sesi_lain.kode_dosen, sesi_lain)
            safe_append_LO(jadwal_ruangan, sesi_lain.kode_ruangan, sesi_lain)

def define_dosen_pakar_koor(dosen_list:list, data_matkul: dict):
    dosen_pakar = [
        dosen for dosen in dosen_list
        if dosen["nip"] in data_matkul.get("dosen_ajar", [])
            and dosen["status"] != "TIDAK_AKTIF"
    ]
    if not dosen_pakar:
        dosen_pakar = [
            dosen for dosen in dosen_list
            if len(set(dosen.get("pakar") or []) & set(data_matkul.get("bidang") or [])) > 0
                and dosen["status"] != "TIDAK_AKTIF"
        ]
    if not dosen_pakar:
        dosen_pakar = [
            dosen for dosen in dosen_list
            if dosen.get("prodi") == data_matkul.get("prodi")
                and dosen["status"] not in ["TIDAK_AKTIF", "TIDAK_TETAP"]
        ]

    dosen_koordinator = [
        dosen for dosen in dosen_pakar 
        if dosen["status"] == "TETAP" and
            dosen.get("prodi") == data_matkul.get("prodi")
    ]
    if not dosen_koordinator:
        dosen_koordinator = [
            dosen for dosen in dosen_pakar 
            if dosen["status"] == "TETAP"
        ]
    if not dosen_koordinator:
        dosen_koordinator = dosen_pakar

    return dosen_pakar, dosen_koordinator

def define_dosen_preference(data_dosen):
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]

    preferensi = data_dosen.get("preferensi", {})
    hindari_hari = preferensi.get("hindari_hari", [])
    hindari_jam = preferensi.get("hindari_jam", [])

    preferensi_hari = [d for d in pilihan_hari_dosen if d not in hindari_hari]
    preferensi_jam = [h for h in range(7, 19 + 1) if h not in hindari_jam]

    return preferensi_hari, preferensi_jam

def check_dosen_availability(data_dosen:dict, matkul_by_kode:dict, jadwal_by_dosen:dict):
    avg_sks = 3
    nip = data_dosen.get("nip")

    preferensi_hari, preferensi_jam = define_dosen_preference(data_dosen)

    estimated_number_of_class = 0
    for hari in preferensi_hari:
        jam_list = preferensi_jam[:]
        i = 0
        while i < len(jam_list):
            jam = jam_list[i]
            blok = list(range(jam, jam + avg_sks))
            if all(j in jam_list for j in blok):
                jam_list = [j for j in jam_list if j not in blok]
                estimated_number_of_class += 1
                continue
            else:
                i += 1
    
    if estimated_number_of_class == 0:
        return False, estimated_number_of_class
    
    jadwal_dosen = jadwal_by_dosen.get(nip, [])
    jadwal_dosen = [sesi for sesi in jadwal_dosen if not matkul_by_kode.get(sesi.kode_matkul[:5], {}).get("take_all_lecture")]

    if len(jadwal_dosen) < estimated_number_of_class:
        return True, estimated_number_of_class
    else:
        return False, estimated_number_of_class

def define_prioritize_dosen(dosen_pakar:list, matkul_by_kode:dict, dosen_by_nip:dict, beban_dosen:dict, jadwal_by_dosen:dict, pilihan_hari:list):    
    nip_with_both_preference = [
        d["nip"] for d in dosen_pakar 
        if d.get("preferensi") and d["preferensi"].get("hindari_jam") and d["preferensi"].get("hindari_hari")
    ]
    nip_with_either_preference = [
        d["nip"] for d in dosen_pakar 
        if d.get("preferensi") and d["nip"] not in nip_with_both_preference
    ]
    
    def filter_nip_prioritas(data_list):
        return [
            d for d in dosen_pakar
            if d["nip"] in data_list and
                check_dosen_availability(dosen_by_nip.get(d["nip"], {}), matkul_by_kode, jadwal_by_dosen)
        ]
    
    prioritas = filter_nip_prioritas(nip_with_both_preference)
    if prioritas:
        return prioritas
    
    prioritas = filter_nip_prioritas(nip_with_either_preference)
    if prioritas:
        return prioritas
    
    return dosen_pakar

def rand_dosen_pakar(list_dosen_pakar: list, data_matkul:dict,  dict_beban_sks_dosen: dict = {}, excluded_dosen: list = []):
    """
    Random dosen by Status, Prodi, beban sks

    Args:
        list_dosen_pakar (list): list dosen yang sudah di sort berdasarkan pakar + prodi
        dict_beban_sks_dosen (dict): Optional, dictionary beban sks dosen, untuk tujuan distribusi sks
        excluded_dosen (list): Opsional, nip dosen dosen yang diabaikan

    Returns:
        object: Dosen yang terpilih dari populasi.
    """
    if len(list_dosen_pakar) > 1:
        # 1. Dosen Tetap dan Sesuai Prodi dengan beban sks 0
        kandidat_dosen = [
            dosen for dosen in list_dosen_pakar
            if dict_beban_sks_dosen[dosen['nip']] == 0
                and dosen["status"] == "TETAP"
                and dosen.get("prodi") == data_matkul.get("prodi")
        ]

        # 2. Dosen Tidak Tetap dengan beban sks 0
        if not kandidat_dosen:
            kandidat_dosen = [
                dosen for dosen in list_dosen_pakar
                if dict_beban_sks_dosen[dosen['nip']] == 0
                    and dosen["status"] == "TIDAK_TETAP"
            ]

        # 3. Dosen dengan beban < beban maksimum yang ada
        if not kandidat_dosen:
            list_beban_sks_dosen = [
                dict_beban_sks_dosen[d["nip"]] for d in list_dosen_pakar
            ]
            max_beban = max(list_beban_sks_dosen or [0])

            if any(sks_dosen < max_beban for sks_dosen in list_beban_sks_dosen):
                kandidat_dosen = [
                    dosen for dosen in list_dosen_pakar
                    if dict_beban_sks_dosen[dosen['nip']] < max_beban 
                ]
            else:
                kandidat_dosen = [
                    dosen for dosen in list_dosen_pakar
                    if dict_beban_sks_dosen[dosen['nip']] <= max_beban 
                ]

            # 3a. Prioritaskan dosen prodi / tidak tetap dengan total beban sks <= 12
            sks_matkul = (1/3 * data_matkul["sks_akademik"]) * 2
            prioritize = [
                d for d in kandidat_dosen
                if (d.get("prodi") == data_matkul.get("prodi") or d["status"] == "TIDAK_TETAP")
                and dict_beban_sks_dosen[d["nip"]] + sks_matkul <= 12
            ]
            if prioritize:
                kandidat_dosen = prioritize

        if kandidat_dosen:
            available = [dosen for dosen in kandidat_dosen if dosen["nip"] not in excluded_dosen]
            return random.choice(available or kandidat_dosen)

        # If kandidat_dosen masih kosong, return random dari list_dosen_pakar yang ada
        available = [d for d in list_dosen_pakar if d["nip"] not in excluded_dosen]
        return random.choice(available or list_dosen_pakar)
    elif len(list_dosen_pakar) == 1:
        return list_dosen_pakar[0]

def rand_ruangan(list_ruangan: list, data_matkul: dict, bidang: list = [], excluded_room: list = [], forAsisten: bool = False, kapasitas_ruangan_dosen: int = 0):
    if not bidang or (forAsisten and data_matkul.get("tipe_kelas_asistensi") == "PRAKTIKUM"):
        bidang = data_matkul.get("bidang", [])

    # 1. Define ruangan utama
    ruangan_utama = []
    if bidang:
        ruangan_utama = [
            r for r in list_ruangan
            if any(plot in r["plot"] for plot in bidang)
        ]
    if not ruangan_utama:
        ruangan_utama = [
            r for r in list_ruangan
            if any(plot in r["plot"] for plot in ["GENERAL", data_matkul["prodi"]])
        ]

    # 2. Sesuaikan tipe ruangan
    if not forAsisten:
        kandidat_ruangan = [
            r for r in ruangan_utama 
            if r['tipe_ruangan'] == data_matkul['tipe_kelas']
        ]
        if not kandidat_ruangan:
            kandidat_ruangan = ruangan_utama

        if data_matkul.get("asistensi", False):
            if data_matkul.get("tipe_kelas_asistensi", None) == "PRAKTIKUM":
                list_kapasitas_lab = [ 
                    r["kapasitas"] for r in list_ruangan 
                    if r["tipe_ruangan"] == "PRAKTIKUM" 
                ]
                if list_kapasitas_lab:
                    max_kapasitas_lab = max(list_kapasitas_lab)
                    kandidat_ruangan = [
                        r for r in kandidat_ruangan 
                        if r["kapasitas"] <= max_kapasitas_lab
                    ]
    elif forAsisten:
        kandidat_ruangan = [
            r for r in ruangan_utama 
            if r["tipe_ruangan"] == data_matkul["tipe_kelas_asistensi"] and
                r["kapasitas"] >= kapasitas_ruangan_dosen
        ]
        if not kandidat_ruangan:
            kandidat_ruangan = [
                r for r in ruangan_utama 
                if r["kapasitas"] >= kapasitas_ruangan_dosen
            ]
    
    if not kandidat_ruangan:
        if ruangan_utama:
            return random.choice(ruangan_utama)
        else:
            return random.choice(list_ruangan)
    
    if len(kandidat_ruangan) > 1:
        not_excluded_room = [r for r in kandidat_ruangan if r["kode"] not in excluded_room]
        if not_excluded_room:
            kandidat_ruangan = not_excluded_room

        kapasitas_ruangan = [r["kapasitas"] for r in kandidat_ruangan if r["tipe_ruangan"] not in ["RAPAT"]]
        max_kapasitas = max(kapasitas_ruangan)

        bobot_kandidat_ruangan = [
            ((len(set(r.get("plot", [])) & set(bidang))*10 or 1) * 
                (10 if any(plot in r.get("plot", []) for plot in [data_matkul["prodi"], "GENERAL"]) else 1) * 
                (r["kapasitas"] if r["kapasitas"] > max_kapasitas*0.75 else 0))
            if r["tipe_ruangan"] not in ["RAPAT"] else 1
            for r in kandidat_ruangan
        ]

        ruangan_terpilih = random.choices(
            population=kandidat_ruangan, 
            weights=bobot_kandidat_ruangan, 
            k=1)[0]
        return ruangan_terpilih
    elif len(kandidat_ruangan) == 1:
        return kandidat_ruangan[0]

def switch_dosen_by_matkul(
        jadwal:list, 
        data_dosen:dict, 
        jadwal_by_dosen:dict, 
        beban_dosen:dict, 
        target_matkul:str, 
        matkul_by_kode:dict, 
        dosen_by_nip:dict,
        jadwal_by_matkul:dict, 
        preferensi_hari:list, 
        preferensi_jam:list, 
        forced:bool=False):
    detail_matkul = matkul_by_kode.get(target_matkul, {})
    for sesi in jadwal_by_matkul.get(target_matkul, []):
        if sesi.kode_matkul[5:] == "A":
            if data_dosen.get("prodi") != detail_matkul.get("prodi"):
                continue
        if (sesi.hari not in preferensi_hari or any(jam not in preferensi_jam for jam in range(sesi.jam_mulai, sesi.jam_selesai))) and not forced:
            continue

        old_dosen = sesi.kode_dosen
        new_dosen = data_dosen["nip"]
        sesi.kode_dosen = new_dosen

        beban_dosen[old_dosen] = hitung_beban_sks_dosen_specific(
            jadwal=jadwal, kode_dosen=old_dosen, matkul_by_kode=matkul_by_kode
        )
        beban_dosen[new_dosen] = hitung_beban_sks_dosen_specific(
            jadwal=jadwal, kode_dosen=new_dosen, matkul_by_kode=matkul_by_kode
        )

        move_item_LO(jadwal_by_dosen, old_dosen, new_dosen, sesi)
        break

def assign_schedule_for_idle_lecturers(
        jadwal, 
        dosen_list, 
        matakuliah_list, 
        beban_dosen, 
        pilihan_hari_dosen, 
        jadwal_by_dosen, 
        jadwal_by_matkul, 
        jadwal_by_ruangan, 
        matkul_by_kode,
        dosen_by_nip):
    for dosen in dosen_list:
        if dosen["status"] == "TETAP" and beban_dosen[dosen['nip']] == 0:
            preferensi_hari, preferensi_jam = define_dosen_preference(dosen)

            matkul_ajar_dosen = list(dosen.get("matkul_ajar", []))
            if not matkul_ajar_dosen:
                matkul_ajar_dosen = [
                    matkul["kode"] for matkul in matakuliah_list 
                    if len(set(dosen.get('pakar') or []) & set(matkul.get('bidang') or [])) > 0
                ]
            if not matkul_ajar_dosen:
                matkul_ajar_dosen = [
                    matkul["kode"] for matkul in matakuliah_list 
                    if matkul["prodi"] == dosen["prodi"]
                ]

            list_matkul_ajar = [kode for kode in matkul_ajar_dosen]
            if not list_matkul_ajar: 
                continue

            for kode_matkul in list_matkul_ajar:
                detail_matkul = matkul_by_kode.get(kode_matkul, {})
                if dosen.get("prodi") != detail_matkul.get("prodi") and dosen["status"] == "TETAP":
                    continue

                switch_dosen_by_matkul(
                    jadwal          = jadwal, 
                    data_dosen      = dosen, 
                    jadwal_by_dosen = jadwal_by_dosen, 
                    beban_dosen     = beban_dosen, 
                    target_matkul   = kode_matkul, 
                    matkul_by_kode  = matkul_by_kode,
                    dosen_by_nip    = dosen_by_nip, 
                    jadwal_by_matkul= jadwal_by_matkul, 
                    preferensi_hari = preferensi_hari, 
                    preferensi_jam  = preferensi_jam
                    )
                available, _ = check_dosen_availability(dosen, matkul_by_kode, jadwal_by_dosen)
                if not available:
                    break
                
def assign_teaching_partners(jadwal, jadwal_by_dosen, matakuliah_list, matkul_by_kode, dosen_by_matkul, beban_dosen):
    for sesi in jadwal:
        if not sesi.team_teaching or sesi.tipe_kelas == "ONLINE":
            continue
        if sesi.kode_dosen != "AS":
            matkul = matkul_by_kode.get(sesi.kode_matkul[:5])
            if not matkul: continue

            count_dosen = len([
                team for team in jadwal 
                if team.kode_matkul == sesi.kode_matkul and team.kode_dosen != sesi.kode_dosen
            ]) + 1

            if count_dosen > 1:
                continue

            sesi_team = next((team for team in jadwal if team.kode_matkul == sesi.kode_matkul), None)
            if not sesi_team:
                continue

            dosen_pakar = dosen_by_matkul.get(sesi.kode_matkul[:5], {}).get("pakar")

            sukses = False
            excluded_dosen = []

            while not sukses:
                if len(excluded_dosen) >= len(dosen_pakar):
                    break

                team_pengganti = rand_dosen_pakar(
                    list_dosen_pakar=dosen_pakar,
                    data_matkul=matkul,
                    dict_beban_sks_dosen=beban_dosen,
                    excluded_dosen=excluded_dosen
                )
                if not team_pengganti:
                    break

                excluded_dosen.append(team_pengganti["nip"])
                jadwal_kosong_team_pengganti = find_available_schedule(
                    jadwal_by=jadwal_by_dosen,
                    kode=team_pengganti["nip"],
                    hari=sesi.hari
                )

                range_time = range(sesi.jam_mulai, sesi.jam_selesai)
                if all(jam in jadwal_kosong_team_pengganti for jam in range_time):
                    old_nip = sesi_team.kode_dosen
                    sesi_team.kode_dosen = team_pengganti["nip"]

                    # Update jadwal_dosen
                    move_item_LO(jadwal_by_dosen, old_nip, sesi_team.kode_dosen, sesi_team)

                    # Update beban_dosen
                    beban_dosen[old_nip] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=old_nip, matkul_by_kode=matkul_by_kode)
                    beban_dosen[sesi_team.kode_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=sesi_team.kode_dosen, matkul_by_kode=matkul_by_kode)

                    sukses = True

def distribute_sks(jadwal, matkul_by_kode, dosen_by_nip, beban_dosen, jadwal_by_dosen, matakuliah_list):
    for sesi in jadwal:
        if sesi.kode_dosen == "AS":
            continue

        matkul = matkul_by_kode.get(sesi.kode_matkul[:5])
        if dosen_by_nip.get(sesi.kode_dosen, {}).get("prodi") != matkul.get("prodi") or dosen_by_nip.get(sesi.kode_dosen, {}).get("status") not in ["TETAP", "TIDAK_TETAP"]:
            continue
        if sesi.kode_matkul[5:] == "A": 
            continue
        dosen = dosen_by_nip.get(sesi.kode_dosen)
        if matkul.get("take_all_lecture") or matkul.get("tipe_kelas") == "ONLINE": continue

        if matkul and dosen:
            beban_pengajar_matkul = {
                nip: beban_dosen[nip] 
                for nip in matkul.get("dosen_ajar", []) 
                if dosen_by_nip.get(nip, {}).get("prodi") == matkul.get("prodi") 
                    or dosen_by_nip.get(nip, {}).get("status") == "TIDAK_TETAP"
            }

            if not beban_pengajar_matkul:
                continue

            dosen_beban_tertinggi, beban_tertinggi = max(beban_pengajar_matkul.items(), key=lambda x: x[1])
            current_sks = beban_dosen.get(sesi.kode_dosen, 0)

            preferensi_hari, preferensi_jam = define_dosen_preference(dosen)

            if current_sks < beban_tertinggi:
                jadwal_beban_tertinggi = [
                    j for j in jadwal # jadwal_dosen[dosen_beban_tertinggi] 
                    if j.kode_matkul.startswith(matkul['kode']) and
                        j.kode_dosen == dosen_beban_tertinggi
                ]

                for sesi_over in jadwal_beban_tertinggi:
                    if sesi_over.hari not in preferensi_hari or any(jam not in preferensi_jam for jam in range(sesi_over.jam_mulai, sesi_over.jam_selesai)):
                        continue

                    if sesi_over.kode_matkul[5:] == "A":
                        if dosen_by_nip.get(sesi.kode_dosen, {}).get("prodi") != matkul_by_kode.get(sesi_over.kode_matkul[:5], {}).get("prodi"):
                            continue
                    
                    conflict = False
                    for jadwal_dosen_current in jadwal_by_dosen.get(sesi.kode_dosen, []):
                        if jadwal_dosen_current.hari == sesi_over.hari:
                            if sesi_over.jam_mulai < jadwal_dosen_current.jam_selesai and sesi_over.jam_selesai > jadwal_dosen_current.jam_mulai:
                                conflict = True
                                break

                    if conflict:
                        continue

                    old_dosen = sesi_over.kode_dosen
                    sesi_over.kode_dosen = sesi.kode_dosen
                    move_item_LO(jadwal_by_dosen, dosen_beban_tertinggi, sesi_over.kode_dosen, sesi_over)

                    beban_dosen[old_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=old_dosen, matkul_by_kode=matkul_by_kode)
                    beban_dosen[sesi_over.kode_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=sesi_over.kode_dosen, matkul_by_kode=matkul_by_kode)
                    break

def fix_room_mismatch(jadwal, jadwal_by_dosen, jadwal_by_ruangan, ruang_list, matkul_by_kode, ruang_by_kode, dosen_by_nip):
    max_attempt = 10    
    for sesi in jadwal:
        if sesi.tipe_kelas == "ONLINE": continue
        
        matkul = matkul_by_kode.get(sesi.kode_matkul[:5])
        ruangan = ruang_by_kode.get(sesi.kode_ruangan)

        isAsisten = sesi.kode_dosen == "AS"
        bidang_matkul = matkul.get("bidang", [])
        
        needed_class_type = matkul.get("tipe_kelas_asistensi") if isAsisten else matkul.get("tipe_kelas")
        if sesi.tipe_kelas == "INTERNATIONAL" and needed_class_type == "TEORI": 
            bidang_matkul = bidang_matkul + ["INTERNATIONAL"]
        plot_ruangan = ruangan.get("plot", [])

        sukses = True
        if not any(bidang in plot_ruangan for bidang in bidang_matkul):
            roomWithPlot = [ruangan for ruangan in ruang_list if any(plot in bidang_matkul for plot in ruangan["plot"])]
            isRoomWithPlotExist = len(roomWithPlot)
            if isRoomWithPlotExist > 0:
                sukses = False
            
            if sukses: continue

            old_kode_ruangan = sesi.kode_ruangan

            qty = next((sesi_dosen.kapasitas for sesi_dosen in jadwal if sesi_dosen.kode_matkul == sesi.kode_matkul[:-3]), 0) if isAsisten else 0
            preferensi_hari = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
            if not isAsisten:
                preferensi_hari.remove("SABTU")
                dosen = dosen_by_nip.get(sesi.kode_dosen)
                preferensi_hari, preferensi_jam = define_dosen_preference(dosen)

            attempt = 1
            excluded_room = []
            while not sukses and attempt <= max_attempt:
                if all(room["kode"] in excluded_room for room in roomWithPlot): break
                ruang_pengganti = rand_ruangan(
                    list_ruangan=roomWithPlot, 
                    data_matkul=matkul,
                    bidang=bidang_matkul,
                    excluded_room=excluded_room,
                    forAsisten=isAsisten,
                    kapasitas_ruangan_dosen=qty
                )

                if ruang_pengganti is None:
                    print(f"[‼️] Tidak ada ruangan pengganti ditemukan untuk matkul {matkul['kode'], matkul['nama']}")
                    break
                if not preferensi_hari:
                    print(f"[‼️] Tidak ada preferensi hari untuk dosen {sesi.kode_dosen}, skip sesi {sesi.kode_matkul}")
                    break

                excluded_day = []
                while not all(hari in excluded_day for hari in preferensi_hari):
                    hari = random.choice([hari for hari in preferensi_hari if hari not in excluded_day])

                    if not isAsisten:
                        jadwal_dosen_kosong = find_available_schedule(
                            jadwal_by=jadwal_by_dosen,
                            kode=sesi.kode_dosen,
                            hari=hari
                        )
                        jadwal_dosen_kosong = [jam for jam in jadwal_dosen_kosong if jam in preferensi_jam]
                    else:
                        jadwal_dosen_kosong = range(7, 19 + 1)
                    jadwal_ruangan_kosong = find_available_schedule(
                        jadwal_by=jadwal_by_ruangan,
                        kode=ruang_pengganti["kode"],
                        hari=hari
                    )
                    jadwal_kosong = list(set(jadwal_dosen_kosong) & set(jadwal_ruangan_kosong))

                    for jam in jadwal_kosong:
                        range_time = range(jam, jam + sesi.sks_akademik + 1)
                        if all(jam in jadwal_kosong for jam in range_time):
                            sukses = True
                            sesi.kode_ruangan = ruang_pengganti["kode"]
                            sesi.kapasitas = ruang_pengganti["kapasitas"]
                            sesi.hari = hari
                            sesi.jam_mulai = jam
                            sesi.jam_selesai = jam + sesi.sks_akademik

                            if not isAsisten:
                                move_item_LO(jadwal_by_dosen, sesi.kode_dosen, sesi.kode_dosen, sesi)

                            move_item_LO(jadwal_by_ruangan, old_kode_ruangan, sesi.kode_ruangan, sesi)
                            break
                    excluded_day.append(hari)
                    if all(hari in excluded_day for hari in preferensi_hari): 
                        excluded_room.append(ruang_pengganti["kode"])
                        attempt += 1
                        break

def fix_lecturer_preference_violations(dosen_list, jadwal_by_dosen, jadwal_by_ruangan, dosen_by_nip, matkul_by_kode, pilihan_hari_dosen):
    for dosen in dosen_list:
        if not jadwal_by_dosen.get(dosen["nip"], []): 
            continue
        
        preferensi_hari, preferensi_jam = define_dosen_preference(dosen)
        
        for sesi in jadwal_by_dosen.get(dosen["nip"], []):
            if sesi.hari in preferensi_hari and all(jam in preferensi_jam for jam in range(sesi.jam_mulai, sesi.jam_selesai)):
                continue

            dosen_ajar = matkul_by_kode.get(sesi.kode_matkul[:5], {}).get("dosen_ajar", [])
            old_dosen = sesi.kode_dosen
            sukses = False
            for nip in dosen_ajar:
                if nip == dosen["nip"]:
                    continue
                calon_dosen_pengganti = dosen_by_nip.get(nip, {})
                if not calon_dosen_pengganti: 
                    continue

                hindari_hari_pengganti, hindari_jam_pengganti = define_dosen_preference(calon_dosen_pengganti)
                if sesi.hari in hindari_hari_pengganti or any(jam in hindari_jam_pengganti for jam in range(sesi.jam_mulai, sesi.jam_selesai)): 
                    continue
                
                for sesi_lain in jadwal_by_dosen.get(nip, []):
                    if sesi.hari == sesi_lain.hari:
                        if sesi.jam_mulai < sesi_lain.jam_selesai and sesi.jam_selesai > sesi_lain.jam_mulai:
                            continue
                        sesi.kode_dosen = nip
                        sukses = True
                        break
                if sukses: 
                    break
            if sukses:
                move_item_LO(jadwal_by_dosen, old_dosen, sesi.kode_dosen, sesi)

def repair_bentrok(jadwal, matakuliah_list, ruang_list, matkul_by_kode, dosen_by_nip, dosen_by_matkul, pilihan_hari_dosen, pilihan_hari_asisten, beban_dosen, jadwal_by_dosen, jadwal_by_matkul, jadwal_by_ruangan):
    max_attempt = 10
    seen_kode_matkul = set()
    for sesi in jadwal:
        if sesi.kode_matkul in seen_kode_matkul:
            continue

        seen_kode_matkul.add(sesi.kode_matkul)
        matkul = matkul_by_kode.get(sesi.kode_matkul[:5])

        if sesi.tipe_kelas == "ONLINE" or (matkul.get("take_all_lecture") and matkul.get("tipe_kelas") == "ONLINE"):
            continue
        
        conflict = False

        if not matkul:
            continue
            
        bidang = matkul.get("bidang", []) or []
        if sesi.tipe_kelas == "INTERNATIONAL": 
            bidang = bidang + ["INTERNATIONAL"]
        
        # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
        # PREFERENSI HARI n JAM
        # IF DOSEN: 
        #   - TENTUKAN LIST DOSEN PAKAR, CEK BEBAN SKS DOSEN, CEK BENTROK JADWAL DOSEN, CEK LANGGAR PREFERENSI
        # IF ASISTEN:
        #   - CARI SESI DOSEN, CEK BENTROK JADWAL DOSEN x ASISTEN
        # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
        if sesi.kode_dosen != "AS":
            dosen = dosen_by_nip.get(sesi.kode_dosen)
            if sesi.kode_matkul[5:] == "A":
                dosen_pakar = dosen_by_matkul.get(sesi.kode_matkul[:5], {}).get("koordinator")
            else:
                dosen_pakar = dosen_by_matkul.get(sesi.kode_matkul[:5], {}).get("pakar")

            preferensi_hari, preferensi_jam = define_dosen_preference(dosen)

            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            # CHECK BEBAN SKS DOSEN MAKS ATAU TIDAK
            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            if beban_dosen[sesi.kode_dosen] > 12:
                if dosen_pakar:
                    old_dosen = sesi.kode_dosen
                    safe_remove_LO(jadwal_by_dosen, old_dosen, sesi)
                    sesi.kode_dosen = rand_dosen_pakar(list_dosen_pakar=dosen_pakar, data_matkul=matkul, dict_beban_sks_dosen=beban_dosen)["nip"]
                    beban_dosen[old_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=old_dosen, matkul_by_kode=matkul_by_kode)
                    beban_dosen[sesi.kode_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=sesi.kode_dosen, matkul_by_kode=matkul_by_kode)
                    safe_append_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)

            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            # CHECK BENTROK JADWAL DOSEN
            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            for sesi_lain in jadwal_by_dosen.get(sesi.kode_dosen, []):
                if sesi is not sesi_lain and sesi.kode_matkul != sesi_lain.kode_matkul and sesi.hari == sesi_lain.hari:
                    if sesi.jam_mulai < sesi_lain.jam_selesai and sesi.jam_selesai > sesi_lain.jam_mulai:
                        conflict = True
                        break

            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            # CHECK LANGGAR PREFERENSI
            # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
            if sesi.hari not in preferensi_hari or any(jam not in preferensi_jam for jam in range(sesi.jam_mulai, sesi.jam_selesai)): 
                conflict = True
        else:
            sesi_dosen = next((sd for sd in jadwal_by_matkul.get(sesi.kode_matkul[:5], []) if f"{sd.kode_matkul}-AS" == sesi.kode_matkul), None)
            if sesi.hari == sesi_dosen.hari:
                if sesi.jam_mulai < sesi_dosen.jam_selesai and sesi.jam_selesai > sesi_dosen.jam_mulai:
                    conflict = True
            preferensi_hari, preferensi_jam = pilihan_hari_asisten, range(7, 19 + 1)

        # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
        # CHECK BENTROK JADWAL RUANGAN
        # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
        for sesi_lain in jadwal_by_ruangan.get(sesi.kode_ruangan, []):
            if sesi is not sesi_lain and sesi.kode_matkul != sesi_lain.kode_matkul and sesi.hari == sesi_lain.hari:
                if sesi.jam_mulai < sesi_lain.jam_selesai and sesi.jam_selesai > sesi_lain.jam_mulai:
                    conflict = True
                    break

        # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
        # WHILE CONFLICT
        #   - CARI POSSIBLE SCHEDULE UNTUK DIGANTI
        #   - CEK APAKAH RANGE WAKTU MULAI - SELESAI ADA DI POSSIBLE SCHEDULE
        #   - JIKA TIDAK, GANTI HARI or GANTI RUANGAN
        # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
        attempt = 1
        excluded_day = []
        excluded_room = []
        while conflict and attempt <= max_attempt:
            if sesi.hari not in preferensi_hari:
                safe_remove_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
                safe_remove_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                sesi.hari = random.choice(preferensi_hari)
                safe_append_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
                safe_append_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                
            possible_schedule = find_available_schedule(jadwal_by_ruangan, sesi.kode_ruangan, sesi.hari)
            if sesi.kode_dosen != "AS":
                possible_lecture_schedule = find_available_schedule(jadwal_by_dosen, sesi.kode_dosen, sesi.hari)
                possible_schedule = list(set(possible_schedule) & set(possible_lecture_schedule))

                if sesi.team_teaching:
                    for sesi_team in jadwal_by_matkul.get(sesi.kode_matkul[:5], []):
                        if sesi_team.kode_matkul == sesi.kode_matkul and sesi_team.kode_dosen != sesi.kode_dosen:
                            possible_team_schedule = find_available_schedule(jadwal_by_dosen, sesi_team.kode_dosen, sesi.hari)
                            possible_schedule = list(set(possible_schedule) & set(possible_team_schedule))

            for jam in possible_schedule:
                range_waktu = range(jam, jam + sesi.sks_akademik + 1)
                if sesi.kode_dosen != "AS":
                    additional_condition = all(jam in preferensi_jam for jam in range_waktu)
                else:
                    additional_condition = not (sesi.hari == sesi_dosen.hari and jam < sesi_dosen.jam_selesai and (jam + matkul['sks_akademik']) > sesi_dosen.jam_mulai)
                
                if all(jam in possible_schedule for jam in range_waktu) and additional_condition:
                    conflict = False
                    safe_remove_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
                    safe_remove_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                    sesi.jam_mulai = jam
                    sesi.jam_selesai = jam + sesi.sks_akademik
                    safe_append_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
                    safe_append_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                    break
                
            if not conflict:
                if sesi.kode_dosen != "AS":
                    if sesi.team_teaching:
                        sync_team_teaching(sesi_dosen=sesi, jadwal=jadwal, jadwal_dosen=jadwal_by_dosen, jadwal_ruangan=jadwal_by_ruangan)
                break
            else:
                excluded_day.append(sesi.hari)
                if all(hari in excluded_day for hari in preferensi_hari):
                    excluded_day = []
                    excluded_room.append(sesi.kode_ruangan)
                    isAsisten = sesi.kode_dosen == "AS"
                    kapasitas_dosen = (sesi_dosen.kapasitas or 0) if isAsisten else 0
                    
                    ruang_pengganti = rand_ruangan(
                        list_ruangan=ruang_list, 
                        data_matkul=matkul, 
                        bidang=bidang, 
                        excluded_room=excluded_room,
                        forAsisten=isAsisten,
                        kapasitas_ruangan_dosen=kapasitas_dosen
                    )

                    safe_remove_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                    sesi.kode_ruangan = ruang_pengganti["kode"]
                    sesi.kapasitas = ruang_pengganti["kapasitas"]
                    safe_append_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                else:
                    preferensi_hari = [d for d in preferensi_hari if d not in excluded_day]
                    safe_remove_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
                    safe_remove_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
                    sesi.hari = random.choice(preferensi_hari)
                    safe_append_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
                    safe_append_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
            
            attempt += 1

def repair_jadwal(jadwal, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list):
    if random.random() < probabilitas_agresif_repair:
        return repair_jadwal_hard(jadwal, matakuliah_list, dosen_list, ruang_list)
    else:
        return repair_jadwal_soft(jadwal, matakuliah_list, dosen_list, ruang_list)

def repair_jadwal_soft(jadwal, matakuliah_list, dosen_list, ruang_list):
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten = pilihan_hari_dosen + ["SABTU"]

    dosen_by_nip = {d['nip']: d for d in dosen_list}
    matkul_by_kode = {m['kode']: m for m in matakuliah_list}
    ruang_by_kode = {r['kode']: r for r in ruang_list}
    dosen_by_matkul = {
        m["kode"]: define_dosen_pakar_koor(dosen_list, m)
        for m in matakuliah_list
    }
    dosen_by_matkul={kode: {"pakar": pakar, "koordinator": koor} for kode, (pakar, koor) in dosen_by_matkul.items()}
    beban_dosen = hitung_beban_sks_dosen_all(jadwal, dosen_list, matkul_by_kode)

    jadwal_by_dosen = {d['nip']: [] for d in dosen_list}
    jadwal_by_matkul = {m['kode']: [] for m in matakuliah_list}
    jadwal_by_ruangan = {r['kode']: [] for r in ruang_list}

    for sesi in jadwal:
        if sesi.tipe_kelas == "ONLINE":
            continue
        safe_append_LO(jadwal_by_ruangan, sesi.kode_ruangan, sesi)
        if sesi.kode_dosen != "AS":
            safe_append_LO(jadwal_by_dosen, sesi.kode_dosen, sesi)
        safe_append_LO(jadwal_by_matkul, sesi.kode_matkul[:5], sesi)

    repair_bentrok(
        jadwal=jadwal,
        matakuliah_list=matakuliah_list,
        ruang_list=ruang_list,
        matkul_by_kode=matkul_by_kode,
        dosen_by_nip=dosen_by_nip,
        dosen_by_matkul=dosen_by_matkul,
        pilihan_hari_dosen=pilihan_hari_dosen,
        pilihan_hari_asisten=pilihan_hari_asisten,
        beban_dosen=beban_dosen,
        jadwal_by_dosen=jadwal_by_dosen,
        jadwal_by_matkul=jadwal_by_matkul,
        jadwal_by_ruangan=jadwal_by_ruangan
    )

    fix_room_mismatch(
        jadwal=jadwal,
        jadwal_by_dosen=jadwal_by_dosen,
        jadwal_by_ruangan=jadwal_by_ruangan,
        ruang_list=ruang_list,
        matkul_by_kode=matkul_by_kode,
        ruang_by_kode=ruang_by_kode,
        dosen_by_nip=dosen_by_nip
    )

    fix_lecturer_preference_violations(
        dosen_list=dosen_list,
        jadwal_by_dosen=jadwal_by_dosen,
        jadwal_by_ruangan=jadwal_by_ruangan,
        dosen_by_nip=dosen_by_nip,
        matkul_by_kode=matkul_by_kode,
        pilihan_hari_dosen=pilihan_hari_dosen
    )

    return jadwal

def repair_jadwal_hard(jadwal, matakuliah_list, dosen_list, ruang_list):
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")

    dosen_by_nip = {d['nip']: d for d in dosen_list}
    matkul_by_kode = {m['kode']: m for m in matakuliah_list}
    ruang_by_kode = {r['kode']: r for r in ruang_list}
    dosen_by_matkul = {
        m["kode"]: define_dosen_pakar_koor(dosen_list, m)
        for m in matakuliah_list
    }
    dosen_by_matkul={kode: {"pakar": pakar, "koordinator": koor} for kode, (pakar, koor) in dosen_by_matkul.items()}
    beban_dosen = hitung_beban_sks_dosen_all(
        jadwal=jadwal, 
        dosen_list=dosen_list, 
        matkul_by_kode=matkul_by_kode
    )
    jadwal_by_dosen = {d['nip']: [] for d in dosen_list}
    jadwal_by_matkul = {m['kode']: [] for m in matakuliah_list}
    jadwal_by_ruangan = {r['kode']: [] for r in ruang_list}
    for sesi in jadwal:
        if sesi.tipe_kelas == "ONLINE": continue
        jadwal_by_ruangan[sesi.kode_ruangan].append(sesi)
        if sesi.kode_dosen == "AS": continue
        jadwal_by_dosen[sesi.kode_dosen].append(sesi)
        jadwal_by_matkul[sesi.kode_matkul[:5]].append(sesi)

    assign_schedule_for_idle_lecturers(
        jadwal              = jadwal, 
        dosen_list          = dosen_list,
        matakuliah_list     = matakuliah_list, 
        beban_dosen         = beban_dosen,
        pilihan_hari_dosen  = pilihan_hari_dosen, 
        jadwal_by_dosen     = jadwal_by_dosen,
        jadwal_by_matkul    = jadwal_by_matkul, 
        jadwal_by_ruangan   = jadwal_by_ruangan,
        matkul_by_kode      = matkul_by_kode,
        dosen_by_nip        = dosen_by_nip
    )

    distribute_sks(
        jadwal          = jadwal,
        matkul_by_kode  = matkul_by_kode,
        dosen_by_nip    = dosen_by_nip,
        beban_dosen     = beban_dosen,
        jadwal_by_dosen = jadwal_by_dosen,
        matakuliah_list = matakuliah_list
    )

    repair_bentrok(
        jadwal              = jadwal,
        matakuliah_list     = matakuliah_list,
        ruang_list          = ruang_list,
        matkul_by_kode      = matkul_by_kode,
        dosen_by_nip        = dosen_by_nip,
        dosen_by_matkul     = dosen_by_matkul,
        pilihan_hari_dosen  = pilihan_hari_dosen,
        pilihan_hari_asisten= pilihan_hari_asisten,
        beban_dosen         = beban_dosen,
        jadwal_by_dosen     = jadwal_by_dosen,
        jadwal_by_matkul    = jadwal_by_matkul,
        jadwal_by_ruangan   = jadwal_by_ruangan
    )
    
    assign_teaching_partners(
        jadwal          = jadwal,
        jadwal_by_dosen = jadwal_by_dosen,
        matakuliah_list = matakuliah_list,
        matkul_by_kode  = matkul_by_kode,
        dosen_by_matkul = dosen_by_matkul,
        beban_dosen     = beban_dosen
    )
    
    fix_room_mismatch(
        jadwal              = jadwal,
        jadwal_by_dosen     = jadwal_by_dosen,
        jadwal_by_ruangan   = jadwal_by_ruangan,
        ruang_list          = ruang_list,
        matkul_by_kode      = matkul_by_kode,
        ruang_by_kode       = ruang_by_kode,
        dosen_by_nip        = dosen_by_nip
    )
    
    fix_lecturer_preference_violations(
        dosen_list          = dosen_list, 
        jadwal_by_dosen     = jadwal_by_dosen, 
        jadwal_by_ruangan   = jadwal_by_ruangan,
        dosen_by_nip        = dosen_by_nip, 
        matkul_by_kode      = matkul_by_kode, 
        pilihan_hari_dosen  = pilihan_hari_dosen
    )
    
    return jadwal

def generate_jadwal(matakuliah_list, dosen_list, ruang_list):
    jadwal = []
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten: list[str] = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")

    jadwal_by_dosen = {}    # {nip: [ {hari, jam_mulai, jam_selesai}, ... ]}
    jadwal_by_ruangan = {}  # {kode_ruangan: [ {hari, jam_mulai, jam_selesai}, ... ]}
    beban_dosen = {} # {nip: beban_sks}
    dosen_by_matkul = {
        m["kode"]: {
            "pakar": dosen_pakar,
            "koordinator": dosen_koordinator
        }
        for m in matakuliah_list
        for dosen_pakar, dosen_koordinator in [define_dosen_pakar_koor(dosen_list=dosen_list, data_matkul=m)]
    }
    dosen_by_nip = {d["nip"]: d for d in dosen_list}
    matkul_by_kode = {m["kode"]: m for m in matakuliah_list}

    for dosen in dosen_list:
        jadwal_by_dosen[dosen["nip"]] = []
        beban_dosen[dosen['nip']] = 0
    for ruangan in ruang_list:
        jadwal_by_ruangan[ruangan["kode"]] = []

    max_attempt = 5 # 10
    
    for matkul in matakuliah_list:
        if matkul.get("tipe_kelas") == "ONLINE" and matkul.get("take_all_lecture"):
            index_kelas = 1
            for dosen in dosen_list:
                if dosen["status"] != "TETAP" or dosen.get("prodi") != matkul.get("prodi"):
                    continue

                sesi_dosen = JadwalKuliah(
                    kapasitas       = 0,
                    kode_matkul     = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}",
                    kode_dosen      = dosen['nip'],
                    sks_akademik    = matkul['sks_akademik'],
                    kode_ruangan    = "ONLINE",
                    hari            = None,
                    jam_mulai       = None,
                    jam_selesai     = None,
                    tipe_kelas      = "ONLINE",
                    program_studi   = matkul['prodi']
                )
                jadwal.append(sesi_dosen)
                index_kelas += 1
        elif matkul.get("tipe_kelas") == "ONLINE":
            putaran_kelas = int(matkul.get('jumlah_kelas') or 1)
            index_kelas = 1
            if index_kelas == 1:
                dosen_pakar = dosen_by_matkul.get(matkul["kode"], {}).get("koordinator")
            else:
                dosen_pakar = dosen_by_matkul.get(matkul["kode"], {}).get("pakar")

            while putaran_kelas > 0:
                dosen = rand_dosen_pakar(list_dosen_pakar=dosen_pakar, data_matkul=matkul, dict_beban_sks_dosen=beban_dosen)
                sesi_dosen = JadwalKuliah(
                    kapasitas       = 0,
                    kode_matkul     = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}",
                    kode_dosen      = dosen['nip'],
                    sks_akademik    = matkul['sks_akademik'],
                    kode_ruangan    = "ONLINE",
                    hari            = None,
                    jam_mulai       = None,
                    jam_selesai     = None,
                    tipe_kelas      = "ONLINE",
                    program_studi   = matkul['prodi']
                )
                jadwal.append(sesi_dosen)
                beban_dosen[sesi_dosen.kode_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=sesi_dosen.kode_dosen, matkul_by_kode=matkul_by_kode)
                index_kelas += 1
                putaran_kelas -= 1

        if matkul.get("tipe_kelas") == "ONLINE" or matkul.get("take_all_lecture"):
            continue
        
        index_kelas = 1

        kandidat_ruangan = [
            ruang for ruang in ruang_list
            if any(plot in ruang["plot"] for plot in matkul.get("bidang", [matkul["prodi"], "GENERAL"]))
        ]

        if matkul.get('jumlah_kelas'):
            putaran_kelas = int(matkul.get('jumlah_kelas', 0))
        else:
            putaran_kelas = int(matkul['jumlah_mahasiswa'] or 0)
        while putaran_kelas > 0:
            if index_kelas == 1:
                dosen_pakar = dosen_by_matkul.get(matkul["kode"], {}).get("koordinator")
            else:
                dosen_pakar = dosen_by_matkul.get(matkul["kode"], {}).get("pakar")
                
            jumlah_dosen = matkul.get('jumlah_dosen', 1)
            hitung_dosen = 1
            while hitung_dosen <= jumlah_dosen:
                excluded_dosen = []
                dosen = rand_dosen_pakar(
                    list_dosen_pakar=dosen_pakar,
                    data_matkul=matkul,
                    dict_beban_sks_dosen=beban_dosen,
                    excluded_dosen=excluded_dosen
                )
                preferensi_hari, preferensi_jam = define_dosen_preference(dosen)
                
                if hitung_dosen == 1:
                    sukses = False
                    attempt = 1
                    excluded_room = []
                    while not sukses and attempt <= max_attempt:
                        if all(ruang["kode"] in excluded_room for ruang in kandidat_ruangan):
                            break
                        
                        ruang_dosen = rand_ruangan(
                            list_ruangan=ruang_list, 
                            data_matkul=matkul, 
                            excluded_room=excluded_room
                        )
                        excluded_room.append(ruang_dosen["kode"])

                        excluded_day = []
                        while any(hari not in excluded_day for hari in preferensi_hari):
                            hari_dosen = random.choice([hari for hari in preferensi_hari if hari not in excluded_day])
                            excluded_day.append(hari_dosen)

                            jadwal_kosong_ruang = find_available_schedule(
                                jadwal_by=jadwal_by_ruangan,
                                kode=ruang_dosen["kode"],
                                hari=hari_dosen
                            )
                            jadwal_kosong_dosen = find_available_schedule(
                                jadwal_by=jadwal_by_dosen,
                                kode=dosen["nip"],
                                hari=hari_dosen
                            )

                            available_schedule = list(set(jadwal_kosong_ruang) & set(jadwal_kosong_dosen))
                            for jam in available_schedule:
                                rentang_waktu = range(jam, jam + matkul["sks_akademik"] + 1)
                                if all(jam in preferensi_jam for jam in rentang_waktu) and all(jam in available_schedule for jam in rentang_waktu) and jam != 12:
                                    sukses = True
                                    jam_mulai_dosen: int = jam
                                    jam_selesai_dosen = jam + matkul['sks_akademik']
                                    break
                            if sukses: break
                        attempt += 1
                else:
                    sukses = False
                    while not sukses:
                        for sesi_lain in jadwal_by_dosen.get(dosen["nip"], []):
                            if hari_dosen == sesi_lain.hari:
                                if jam_mulai_dosen < sesi_lain.jam_selesai and jam_selesai_dosen > sesi_lain.jam_mulai:
                                    sukses = False
                                    break
                                else:
                                    sukses = True

                        if hari_dosen not in preferensi_hari or any(jam not in preferensi_jam for jam in preferensi_jam):
                            sukses = False

                        if sukses: 
                            break
                        else:
                            if all(dosen["nip"] in excluded_dosen for dosen in dosen_pakar):
                                hitung_dosen = jumlah_dosen
                                break
                            else:
                                excluded_dosen.append(dosen["nip"])
                                dosen = rand_dosen_pakar(
                                    list_dosen_pakar=dosen_pakar,
                                    data_matkul=matkul,
                                    dict_beban_sks_dosen=beban_dosen,
                                    excluded_dosen=excluded_dosen
                                )
                                preferensi_hari, preferensi_jam = define_dosen_preference(dosen)
                    
                            if hitung_dosen <= jumlah_dosen:
                                break

                hitung_dosen += 1
                sesi_dosen = JadwalKuliah(
                    kapasitas       = ruang_dosen['kapasitas'],
                    kode_matkul     = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}",
                    kode_dosen      = dosen['nip'],
                    sks_akademik    = matkul['sks_akademik'],
                    kode_ruangan    = ruang_dosen['kode'],
                    hari            = hari_dosen,
                    jam_mulai       = jam_mulai_dosen,
                    jam_selesai     = jam_selesai_dosen,
                    tipe_kelas      = matkul['tipe_kelas'],
                    program_studi   = matkul['prodi'],
                    team_teaching   = True if jumlah_dosen > 1 else False
                )
                jadwal.append(sesi_dosen)

                beban_dosen[sesi_dosen.kode_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=sesi_dosen.kode_dosen, matkul_by_kode=matkul_by_kode)
                safe_append_LO(jadwal_by_dosen, sesi_dosen.kode_dosen, sesi_dosen)
            safe_append_LO(jadwal_by_ruangan, sesi_dosen.kode_ruangan, sesi_dosen)

            # Penentuan kelas asistensi yang tidak terintegrasi dengan kelas dosen
            if matkul.get('asistensi') and not matkul.get('integrated_class'):
                suggested_hari_asisten = pilihan_hari_asisten
                hari_asisten = random.choice(suggested_hari_asisten)

                ruang_asisten = rand_ruangan(
                    list_ruangan=ruang_list, 
                    data_matkul=matkul, 
                    forAsisten=True, 
                    kapasitas_ruangan_dosen=sesi_dosen.kapasitas
                )
                
                sukses = False
                attempt = 0
                excluded_day = []
                excluded_room = []
                while not sukses and max_attempt >= attempt:
                    jadwal_ruangan_kosong = find_available_schedule(
                        jadwal_by=jadwal_by_ruangan, 
                        kode=ruang_asisten['kode'], 
                        hari=hari_asisten
                    )

                    status = False
                    for jam in jadwal_ruangan_kosong:
                        rentang_waktu = range(jam, jam + matkul['sks_akademik'] + 1)
                        if all(r in jadwal_ruangan_kosong for r in rentang_waktu) and jam != 12 and not (hari_asisten == sesi_dosen.hari and jam < sesi_dosen.jam_selesai and (jam + matkul['sks_akademik']) > sesi_dosen.jam_mulai):
                            status = True
                            sukses = True
                            jam_mulai_asisten = jam
                            jam_selesai_asisten = jam + matkul['sks_akademik']
                            break
                        else:
                            status = False

                    if not status:
                        excluded_day.append(hari_asisten)
                        if all(d in excluded_day for d in suggested_hari_asisten):
                            excluded_day = []
                            excluded_room.append(ruangan['kode'])
                            ruang_asisten = rand_ruangan(
                                list_ruangan=ruang_list, 
                                data_matkul=matkul, 
                                excluded_room=excluded_room, 
                                forAsisten=True, 
                                kapasitas_ruangan_dosen=sesi_dosen.kapasitas
                            )
                        else:
                            hari_asisten = random.choice([d for d in suggested_hari_asisten if d not in excluded_day])

                    attempt += 1
                
                sesi_asisten = JadwalKuliah(
                    kapasitas    = ruang_asisten['kapasitas'],
                    kode_matkul  = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}-AS",
                    kode_dosen   = "AS",
                    sks_akademik = matkul['sks_akademik'],
                    kode_ruangan = ruang_asisten['kode'],
                    hari         = hari_asisten,
                    jam_mulai    = jam_mulai_asisten,
                    jam_selesai  = jam_selesai_asisten,
                    tipe_kelas   = matkul['tipe_kelas_asistensi'],
                    program_studi= matkul['prodi']
                )
                jadwal.append(sesi_asisten)
                safe_append_LO(jadwal_by_ruangan, sesi_asisten.kode_ruangan, sesi_asisten)
            
            putaran_kelas -= (1 if matkul.get('jumlah_kelas') else ruang_dosen['kapasitas'])
            index_kelas += 1
        
        putaran_inter = int(matkul.get('jumlah_kelas_internasional') or 0)
        bidang = matkul.get("bidang", []) + ["INTERNATIONAL"]
        kandidat_ruangan = [
            ruang for ruang in ruang_list
            if any(plot in ruang["plot"] for plot in bidang)
        ]
        if not kandidat_ruangan:
            kandidat_ruangan = [
                ruang for ruang in ruang_list
                if any(plot in ruang["plot"] for plot in [matkul["prodi"], "GENERAL"])
            ]
        while putaran_inter > 0:
            if index_kelas == 1:
                dosen_pakar = dosen_by_matkul.get(matkul["kode"], {}).get("koordinator")
            else:
                dosen_pakar = dosen_by_matkul.get(matkul["kode"], {}).get("pakar")
                
            jumlah_dosen = int(matkul.get('jumlah_dosen_internasional') or 1)
            hitung_dosen = 1
            while hitung_dosen <= jumlah_dosen:
                excluded_dosen = []
                dosen = rand_dosen_pakar(
                    list_dosen_pakar=dosen_pakar,
                    data_matkul=matkul,
                    dict_beban_sks_dosen=beban_dosen,
                    excluded_dosen=excluded_dosen
                )
                preferensi_hari, preferensi_jam = define_dosen_preference(dosen)
                
                if hitung_dosen == 1:
                    sukses = False
                    excluded_room = []
                    attempt = 1
                    while not sukses and attempt <= max_attempt:
                        if all(ruang["kode"] in excluded_room for ruang in kandidat_ruangan):
                            break
                        
                        ruang_dosen = rand_ruangan(
                            list_ruangan=ruang_list, 
                            data_matkul=matkul, 
                            bidang=bidang, 
                            excluded_room=excluded_room
                        )
                        excluded_room.append(ruang_dosen["kode"])

                        excluded_day = []
                        while any(hari not in excluded_day for hari in preferensi_hari):
                            hari_dosen = random.choice([hari for hari in preferensi_hari if hari not in excluded_day])
                            excluded_day.append(hari_dosen)

                            jadwal_kosong_ruang = find_available_schedule(
                                jadwal_by=jadwal_by_ruangan,
                                kode=ruang_dosen["kode"],
                                hari=hari_dosen
                            )
                            jadwal_kosong_dosen = find_available_schedule(
                                jadwal_by=jadwal_by_dosen,
                                kode=dosen["nip"],
                                hari=hari_dosen
                            )

                            available_schedule = list(set(jadwal_kosong_ruang) & set(jadwal_kosong_dosen))
                            for jam in available_schedule:
                                rentang_waktu = range(jam, jam + matkul["sks_akademik"] + 1)
                                if all(jam in preferensi_jam for jam in rentang_waktu) and all(jam in available_schedule for jam in rentang_waktu) and jam != 12:
                                    sukses = True
                                    jam_mulai_dosen = jam
                                    jam_selesai_dosen = jam + matkul['sks_akademik']
                                    break
                            if sukses: break
                        attempt += 1
                else:
                    sukses = False
                    while not sukses:
                        excluded_dosen.append(dosen["nip"])
                        for sesi_lain in jadwal_by_dosen.get(dosen["nip"], []):
                            if hari_dosen == sesi_lain.hari:
                                if jam_mulai_dosen < sesi_lain.jam_selesai and jam_selesai_dosen > sesi_lain.jam_mulai:
                                    sukses = False
                                    break
                                else:
                                    sukses = True

                        if hari_dosen not in preferensi_hari or any(jam not in preferensi_jam for jam in preferensi_jam):
                            sukses = False

                        if sukses: 
                            break
                        else:
                            if all(dosen["nip"] in excluded_dosen for dosen in dosen_pakar):
                                hitung_dosen = jumlah_dosen
                                break
                            else:
                                excluded_dosen.append(dosen["nip"])
                                dosen = rand_dosen_pakar(
                                    list_dosen_pakar=dosen_pakar,
                                    data_matkul=matkul,
                                    dict_beban_sks_dosen=beban_dosen,
                                    excluded_dosen=excluded_dosen
                                )
                                preferensi_hari, preferensi_jam = define_dosen_preference(dosen)
                    
                            if hitung_dosen <= jumlah_dosen:
                                break

                hitung_dosen += 1
                sesi_dosen = JadwalKuliah(
                    kapasitas       = ruang_dosen['kapasitas'],
                    kode_matkul     = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}",
                    kode_dosen      = dosen['nip'],
                    sks_akademik    = matkul['sks_akademik'],
                    kode_ruangan    = ruang_dosen['kode'],
                    hari            = hari_dosen,
                    jam_mulai       = jam_mulai_dosen,
                    jam_selesai     = jam_selesai_dosen,
                    tipe_kelas      = "INTERNATIONAL",
                    program_studi   = matkul['prodi'],
                    team_teaching   = True if jumlah_dosen > 1 else False
                )
                jadwal.append(sesi_dosen)

                beban_dosen[sesi_dosen.kode_dosen] = hitung_beban_sks_dosen_specific(jadwal=jadwal, kode_dosen=sesi_dosen.kode_dosen, matkul_by_kode=matkul_by_kode)
                safe_append_LO(jadwal_by_dosen, sesi_dosen.kode_dosen, sesi_dosen)
            safe_append_LO(jadwal_by_ruangan, sesi_dosen.kode_ruangan, sesi_dosen)

            # Penentuan kelas asistensi yang tidak terintegrasi dengan kelas dosen
            if matkul.get('asistensi') and not matkul.get('integrated_class'):
                suggested_hari_asisten = pilihan_hari_asisten
                hari_asisten = random.choice(suggested_hari_asisten)

                ruang_asisten = rand_ruangan(
                    list_ruangan=ruang_list, 
                    data_matkul=matkul, 
                    bidang=bidang,
                    forAsisten=True, 
                    kapasitas_ruangan_dosen=sesi_dosen.kapasitas
                )
                
                sukses = False
                attempt = 0
                excluded_day = []
                excluded_room = []
                while not sukses and max_attempt >= attempt:
                    jadwal_ruangan_kosong = find_available_schedule(
                        jadwal_by=jadwal_by_ruangan, 
                        kode=ruang_asisten['kode'], 
                        hari=hari_asisten
                    )

                    status = False
                    for jam in jadwal_ruangan_kosong:
                        rentang_waktu = range(jam, jam + matkul['sks_akademik'] + 1)
                        if all(r in jadwal_ruangan_kosong for r in rentang_waktu) and jam != 12 and not (hari_asisten == sesi_dosen.hari and jam < sesi_dosen.jam_selesai and (jam + matkul['sks_akademik']) > sesi_dosen.jam_mulai):
                            status = True
                            sukses = True
                            jam_mulai_asisten = jam
                            jam_selesai_asisten = jam + matkul['sks_akademik']
                            break
                        else:
                            status = False

                    if not status:
                        excluded_day.append(hari_asisten)
                        if all(d in excluded_day for d in suggested_hari_asisten):
                            excluded_day = []
                            excluded_room.append(ruangan['kode'])
                            ruang_asisten = rand_ruangan(
                                list_ruangan=ruang_list, 
                                data_matkul=matkul, 
                                bidang=bidang,
                                excluded_room=excluded_room, 
                                forAsisten=True, 
                                kapasitas_ruangan_dosen=sesi_dosen.kapasitas
                            )
                        else:
                            hari_asisten = random.choice([d for d in suggested_hari_asisten if d not in excluded_day])

                    attempt += 1
                
                sesi_asisten = JadwalKuliah(
                    kapasitas    = ruang_asisten['kapasitas'],
                    kode_matkul  = f"{matkul['kode']}{angka_ke_huruf(index_kelas)}-AS",
                    kode_dosen   = "AS",
                    sks_akademik = matkul['sks_akademik'],
                    kode_ruangan = ruang_asisten['kode'],
                    hari         = hari_asisten,
                    jam_mulai    = jam_mulai_asisten,
                    jam_selesai  = jam_selesai_asisten,
                    tipe_kelas   = "INTERNATIONAL",
                    program_studi= matkul['prodi']
                )
                jadwal.append(sesi_asisten)
                safe_append_LO(jadwal_by_ruangan, sesi_asisten.kode_ruangan, sesi_asisten)
            
            putaran_inter -= 1
            index_kelas += 1

    return jadwal

def generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi):
    return [generate_jadwal(matakuliah_list, dosen_list, ruang_list) for _ in range(ukuran_populasi)]

def hitung_fitness(jadwal, matakuliah_list, dosen_list, ruang_list, detail=False, return_detail=False):
    penalti = 0
    jadwal_dosen = {}
    jadwal_ruangan = {}
    beban_dosen = {}

    dosen_by_nip = {d["nip"]: d for d in dosen_list}
    matkul_by_kode = {m["kode"]: m for m in matakuliah_list}
    ruang_by_kode = {r["kode"]: r for r in ruang_list}

    for dosen in dosen_list:
        if dosen['nip'] not in jadwal_dosen: jadwal_dosen[dosen['nip']] = []
    for ruangan in ruang_list:
        if ruangan['kode'] not in jadwal_ruangan: jadwal_ruangan[ruangan['kode']] = []

    # COUNTER
    hitung_dosen_overdose = 0
    hitung_ruangan_bentrok = 0
    hitung_dosen_bentrok = 0
    hitung_asdos_nabrak_dosen = 0
    hitung_kelas_dosen_missing = 0
    hitung_kelas_asisten_missing = 0
    hitung_salah_tipe_kelas = 0
    hitung_diluar_jam_kerja = 0
    hitung_solo_team = {}
    pelanggaran_preferensi = []
    mata_kuliah_minus = {}

    set_ruang_bentrok = set()
    set_dosen_bentrok = set()
    detail_jadwal_matkul = {}

    # TO BE CHECKED:
    # (20)  Jadwal Ruangan Bertabrakan                                  >> ruangan_bentrok           (DONE)
    # (20)  Jadwal Dosen Bertabrakan                                    >> dosen_bentrok             (DONE)
    # (20)  Jadwal Dosen dan Asisten Berjalan Bersamaan                 >> asdos_nabrak_dosen        (DONE)
    # (15)  Dosen Tetap Tidak Mengajar                                  >> dosen_nganggur           (DONE)
    # (15)  Kelas Dosen atau Asisten Hilang atau Tidak Lengkap          >> kelas_gaib                (DONE)
    # (15)  Solo Team_Teaching                                          >> solo_team
    # (10)  Beban SKS Dosen melebihi 12 sks                             >> dosen_overdosis           (DONE)
    # (10)  Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19    >> diluar_jam_kerja          (DONE)
    # (10)  Cek Total Kelas Bisa Cangkup Semua Mahasiswa                >> kapasitas_kelas_terbatas  (DONE)
    # (5)   Tipe Ruangan Tidak Sesuai                                   >> tipe_ruang_salah         (DONE)
    # (5)   Tidak Sesuai dengan permintaan / request dosen              >> melanggar_preferensi      (DONE)

    # CEK DOSEN NGANGGUR
    isSomeDosenNotSet, whoNotSet = is_some_lecture_not_scheduled(jadwal, matakuliah_list, dosen_list)
    if isSomeDosenNotSet:
        penalti += (BOBOT_PENALTI["dosen_nganggur"] * len(whoNotSet))

    # CEK PELANGGARAN BEBAN SKS DOSEN
    beban_dosen = hitung_beban_sks_dosen_all(jadwal=jadwal, dosen_list=dosen_list, matkul_by_kode=matkul_by_kode)
    for nip, beban_sks in beban_dosen.items():
        if beban_sks > 12:
            hitung_dosen_overdose += 1
            penalti += BOBOT_PENALTI['dosen_overdosis']

    seen_course = set()
    for sesi in jadwal:
        # CEK SUPAYA BENTROK RUANGAN CUMA DICEK 1x UNTUK KODE MATKUL YANG SAMA
        if sesi.kode_matkul not in seen_course:
            seen_course.add(sesi.kode_matkul)

            kode_matkul = sesi.kode_matkul[:5]
            info_matkul = matkul_by_kode.get(sesi.kode_matkul[:5], {})
            is_asisten = sesi.kode_dosen == "AS"
            if not is_asisten:
                info_dosen = dosen_by_nip.get(sesi.kode_dosen) 
            info_ruangan = ruang_by_kode.get(sesi.kode_ruangan, {})
            
            if kode_matkul not in detail_jadwal_matkul: detail_jadwal_matkul[kode_matkul] = {'jumlah_kelas': 0, 'kapasitas_total': 0}
            
            if sesi.tipe_kelas != "ONLINE":
                # CEK BENTROK JADWAL RUANGAN
                for sesi_lain in jadwal_ruangan[sesi.kode_ruangan]:
                    if sesi.hari == sesi_lain['hari']:
                        if sesi.jam_mulai < sesi_lain['jam_selesai'] and sesi.jam_selesai > sesi_lain['jam_mulai']:
                            set_ruang_bentrok.add(sesi.kode_matkul)
                            penalti += BOBOT_PENALTI['ruangan_bentrok']
                            hitung_ruangan_bentrok += 1
                jadwal_ruangan[sesi.kode_ruangan].append({'hari': sesi.hari, 'jam_mulai': sesi.jam_mulai, 'jam_selesai': sesi.jam_selesai})

                # CEK JAM MULAI DAN JAM SELESAI MASIH DI JAM KERJA ATAU TIDAK
                if sesi.jam_mulai < 7 or sesi.jam_selesai > 19:
                    penalti += BOBOT_PENALTI['diluar_jam_kerja']
                    hitung_diluar_jam_kerja += 1


            if not is_asisten:
                if sesi.tipe_kelas != "ONLINE":
                    if sesi.tipe_kelas != "INTERNATIONAL" and info_ruangan.get("tipe_ruangan") != info_matkul.get("tipe_kelas"):
                        hitung_salah_tipe_kelas += 1
                        penalti += BOBOT_PENALTI["tipe_ruang_salah"]
                    elif sesi.tipe_kelas == "INTERNATIONAL" and info_matkul.get("tipe_kelas") == "TEORI" and sesi.tipe_kelas not in info_ruangan.get("plot", []):
                        hitung_salah_tipe_kelas += 1
                        penalti += BOBOT_PENALTI["tipe_ruang_salah"]
                    
                    # CEK BENTROK DOSEN
                    for sesi_lain in jadwal_dosen[sesi.kode_dosen]:
                        if sesi.hari == sesi_lain['hari']:
                            if sesi.jam_mulai < sesi_lain['jam_selesai'] and sesi.jam_selesai > sesi_lain['jam_mulai']:
                                set_dosen_bentrok.add(frozenset({sesi.kode_matkul: sesi.kode_dosen}.items()))
                                penalti += BOBOT_PENALTI['dosen_bentrok']
                                hitung_dosen_bentrok += 1
                    jadwal_dosen[sesi.kode_dosen].append({'hari': sesi.hari, 'jam_mulai': sesi.jam_mulai, 'jam_selesai': sesi.jam_selesai})

                    # CEK PELANGGARAN PREFERENSI DOSEN
                    preferensi_hari, preferensi_jam = define_dosen_preference(info_dosen)
                    pelanggaran_hari = sesi.hari not in preferensi_hari
                    pelanggaran_jam = any(jam not in preferensi_jam for jam in range(sesi.jam_mulai, sesi.jam_selesai + 1))
                    if pelanggaran_hari and pelanggaran_jam:
                        pelanggaran_preferensi.append({"kode_dosen": sesi.kode_dosen, "kode_matkul": sesi.kode_matkul, "hari": sesi.hari, "jam_mulai": sesi.jam_mulai, "jam_selesai": sesi.jam_selesai})
                        penalti += (BOBOT_PENALTI['melanggar_preferensi'] * 2)
                    elif pelanggaran_hari or pelanggaran_jam:
                        pelanggaran_preferensi.append({"kode_dosen": sesi.kode_dosen, "kode_matkul": sesi.kode_matkul, "hari": sesi.hari, "jam_mulai": sesi.jam_mulai, "jam_selesai": sesi.jam_selesai})
                        penalti += (BOBOT_PENALTI['melanggar_preferensi'])

                    # HITUNG TOTAL KAPASITAS
                    detail_jadwal_matkul[kode_matkul]['jumlah_kelas'] += 1
                    detail_jadwal_matkul[kode_matkul]['kapasitas_total'] += sesi.kapasitas

                # CEK SOLO TEAM
                if sesi.team_teaching:
                    if info_dosen['nip'] not in hitung_solo_team: hitung_solo_team[info_dosen['nip']] = 0
                    count_dosen = len([
                        team for team in jadwal 
                        if team.kode_matkul == sesi.kode_matkul
                            and team.kode_dosen != sesi.kode_dosen
                    ]) + 1 # +1 untuk sesi.kode_dosen itu sendiri
                    if count_dosen == 1:
                        hitung_solo_team[info_dosen['nip']] += 1
                        penalti += BOBOT_PENALTI['solo_team']
                    else:
                        for sesi_team in jadwal:
                            if sesi_team.kode_matkul == sesi.kode_matkul and sesi_team.kode_dosen != sesi.kode_dosen:
                                if sesi_team.tipe_kelas != "ONLINE":
                                    # CEK BENTROK DOSEN TEAM
                                    for sesi_lain in jadwal_dosen[sesi_team.kode_dosen]:
                                        if sesi_team.hari == sesi_lain['hari']:
                                            if sesi_team.jam_mulai < sesi_lain['jam_selesai'] and sesi_team.jam_selesai > sesi_lain['jam_mulai']:
                                                penalti += BOBOT_PENALTI['dosen_bentrok']
                                                hitung_dosen_bentrok += 1
                                    jadwal_dosen[sesi_team.kode_dosen].append({'hari': sesi_team.hari, 'jam_mulai': sesi_team.jam_mulai, 'jam_selesai': sesi_team.jam_selesai})

                                    # CEK PELANGGARAN BEBAN SKS DOSEN TEAM
                                    if beban_dosen[sesi_team.kode_dosen] > 12:
                                        penalti += BOBOT_PENALTI['dosen_overdosis']

                                    # CEK PELANGGARAN PREFERENSI DOSEN TEAM
                                    info_team = next((d for d in dosen_list if d['nip'] == sesi_team.kode_dosen), {})
                                    preferensi_hari, preferensi_jam = define_dosen_preference(info_team)

                                    pelanggaran_hari = sesi_team.hari not in preferensi_hari
                                    pelanggaran_jam = any(jam not in preferensi_jam for jam in range(sesi_team.jam_mulai, sesi_team.jam_selesai + 1))

                                    if pelanggaran_hari and pelanggaran_jam:
                                        pelanggaran_preferensi.append({"kode_dosen": sesi_team.kode_dosen, "kode_matkul": sesi_team.kode_matkul, "hari": sesi_team.hari, "jam_mulai": sesi_team.jam_mulai, "jam_selesai": sesi_team.jam_selesai})
                                        penalti += (BOBOT_PENALTI['melanggar_preferensi'] * 2)
                                    elif pelanggaran_hari or pelanggaran_jam:
                                        pelanggaran_preferensi.append({"kode_dosen": sesi_team.kode_dosen, "kode_matkul": sesi_team.kode_matkul, "hari": sesi_team.hari, "jam_mulai": sesi_team.jam_mulai, "jam_selesai": sesi_team.jam_selesai})
                                        penalti += (BOBOT_PENALTI['melanggar_preferensi'])

                # CEK EKSISTENSI KELAS ASISTEN
                if info_matkul.get('asistensi') and not info_matkul.get('integrated_class'):
                    sesi_asisten = next((sa for sa in jadwal if sa.kode_matkul == sesi.kode_matkul+"-AS"), None)
                    if sesi_asisten:
                        if sesi.tipe_kelas != "ONLINE":
                            # CEK BENTROK JADWAL DOSEN X ASISTEN NGGA BENER INI ANJENG. CEK ULANG SU
                            if sesi.hari == sesi_asisten.hari:
                                if sesi.jam_mulai < sesi_asisten.jam_selesai and sesi.jam_selesai > sesi_asisten.jam_mulai:
                                    penalti += BOBOT_PENALTI['asdos_nabrak_dosen']
                                    hitung_asdos_nabrak_dosen += 1
                    else:
                        penalti += BOBOT_PENALTI['kelas_gaib']
                        hitung_kelas_asisten_missing += 1
            else:
                if sesi.tipe_kelas != "INTERNATIONAL" and sesi.tipe_kelas != info_matkul.get("tipe_kelas_asistensi"):
                    hitung_salah_tipe_kelas += 1
                    penalti += BOBOT_PENALTI["tipe_ruang_salah"]
                elif sesi.tipe_kelas == "INTERNATIONAL" and info_matkul.get("tipe_kelas_asistensi") == "TEORI" and "INTERNATIONAL" not in info_ruangan.get("plot", []):
                    hitung_salah_tipe_kelas += 1
                    penalti += BOBOT_PENALTI["tipe_ruang_salah"]
                    
                sesi_dosen = next((sd for sd in jadwal if sd.kode_matkul == sesi.kode_matkul[:-3]), None)
                # CEK EKSISTENSI KELAS DOSEN
                if not sesi_dosen:
                    penalti += BOBOT_PENALTI['kelas_gaib']
                    hitung_kelas_dosen_missing += 1
                
    # CEK KEKURANGAN KAPASITAS TIAP MATKUL
    for kode_matkul, data in detail_jadwal_matkul.items():
        matkul_detail = next((matkul for matkul in matakuliah_list if matkul['kode'] == kode_matkul), None)
        if matkul_detail.get("take_all_lecture") or matkul_detail.get("tipe_kelas") == "ONLINE": continue
        
        if matkul_detail:
            if matkul_detail.get('jumlah_kelas') and data['jumlah_kelas'] < matkul_detail['jumlah_kelas']:
                penalti += BOBOT_PENALTI['kapasitas_kelas_terbatas']
            elif not matkul_detail.get('jumlah_kelas') and data['kapasitas_total'] < matkul_detail['jumlah_mahasiswa']:
                kekurangan_kapasitas = matkul_detail['jumlah_mahasiswa'] - data['kapasitas_total']
                penalti += (BOBOT_PENALTI['kapasitas_kelas_terbatas'] * (kekurangan_kapasitas/10))
                mata_kuliah_minus[kode_matkul] = kekurangan_kapasitas

    if detail:
        if hitung_dosen_overdose: print(f"{'':<10}{'Dosen Overdose':<40} : {hitung_dosen_overdose}")
        if hitung_dosen_bentrok: print(f"{'':<10}{'Bentrok Dosen':<40} : {hitung_dosen_bentrok}")
        if hitung_ruangan_bentrok: print(f"{'':<10}{'Bentrok Ruangan':<40} : {hitung_ruangan_bentrok}")
        if hitung_asdos_nabrak_dosen: print(f"{'':<10}{'Bentrok Dosen-Asdos':<40} : {hitung_asdos_nabrak_dosen}")
        if hitung_diluar_jam_kerja: print(f"{'':<10}{'Kelas Diluar Jam Kerja':<40} : {hitung_diluar_jam_kerja}")
        if hitung_kelas_dosen_missing: print(f"{'':<10}{'Kelas Dosen Missing':<40} : {hitung_kelas_dosen_missing}")
        if hitung_salah_tipe_kelas: print(f"{'':<10}{'Salah Tipe Ruangan':<40} : {hitung_salah_tipe_kelas}")
        if hitung_kelas_asisten_missing: print(f"{'':<10}{'Kelas Asisten Missing':<40} : {hitung_kelas_asisten_missing}")
        if mata_kuliah_minus: print(f"{'':<10}{'Kapasitas kelas kurang x':<40} : {mata_kuliah_minus}")
        hitung_solo_team = {k: v for k, v in hitung_solo_team.items() if v}
        if hitung_solo_team: print(f"{'':<10}{'solo team':<40} : {hitung_solo_team}")
        if len(pelanggaran_preferensi) > 0: print(f"{'':<10}{'pelanggaran preferensi':<40} : {len(pelanggaran_preferensi)}")
        if whoNotSet: print(f"{'':<10}{'dosen tidak mengajar':<40} : {whoNotSet}")

    if return_detail:
        list_dosen_bentrok = list()
        list_ruang_bentrok = list(set_ruang_bentrok)
        for item in set_dosen_bentrok:
            d = dict(item)
            list_dosen_bentrok.append(d)
        data_return = {
            "score": max(0, 1000 - penalti),
            "dosen_overdose": hitung_dosen_overdose,
            "bentrok_dosen": hitung_dosen_bentrok,
            "bentrok_ruangan": hitung_ruangan_bentrok,
            "bentrok_dosen_asdos": hitung_asdos_nabrak_dosen,
            "solo_team_teaching": {k: v for k, v in hitung_solo_team.items() if v},
            "pelanggaran_preferensi": pelanggaran_preferensi,
            "dosen_not_set": whoNotSet,
            "list_ruang_bentrok": list_ruang_bentrok,
            "list_dosen_bentrok": list_dosen_bentrok
        }
        return data_return

    return max(0, 1000 - penalti)

def roulette_selection(populasi, fitness_scores):
    """
    Memilih satu individu dari populasi menggunakan metode seleksi berdasarkan fitness.

    Individu dipilih secara acak menggunakan nilai acak antara 0 hingga total fitness 
    (populasi), di mana individu dengan fitness lebih tinggi memiliki peluang lebih besar terpilih.

    Args:
        populasi (list): Daftar individu (jadwal) yang tersedia.
        fitness_scores (list): Daftar nilai fitness yang sesuai dengan setiap individu dalam populasi.

    Returns:
        object: Individu yang terpilih dari populasi.
    """
    
    total_fitness = sum(fitness_scores)
    pick = random.uniform(0, total_fitness)
    current = 0
    for individu, score in zip(populasi, fitness_scores):
        current += score
        if current > pick:
            return individu
    return random.choice(populasi)

def crossover(parent1: object, parent2: object):
    """
    Melakukan crossover antara parent1 dan parent2 berdasarkan blok kode_matkul (tanpa suffix paralel).

    Titik acak diambil dari parent1, lalu blok matkul utamanya diidentifikasi
    (misal TC502 dari TC502A/TC502C/TC502-AS). Crossover dilakukan dari titik
    awal blok tersebut pada kedua parent.

    Args:
        parent1 (list): Individu pertama berupa list sesi.
        parent2 (list): Individu kedua berupa list sesi.

    Returns:
        tuple: Dua individu hasil crossover (child1, child2).
    """
    
    titik = random.randint(1, len(parent1)-1)
    sesi_target = parent1[titik]
    kode_matkul = sesi_target.kode_matkul
    is_asisten = sesi_target.kode_dosen == "AS"
    matkul_code_base = kode_matkul[:-4] if is_asisten else kode_matkul[:-1]

    titik1 = next((index for index, sesi in enumerate(parent1) if sesi.kode_matkul == matkul_code_base + 'A'), 0)
    titik2 = next((index for index, sesi in enumerate(parent2) if sesi.kode_matkul == matkul_code_base + 'A'), 0)

    child1 = parent1[:titik1] + parent2[titik2:]
    child2 = parent2[:titik2] + parent1[titik1:]
    return child1, child2

def mutasi(individu, matakuliah_list, ruang_list, peluang_mutasi=0.1):
    """
    Melakukan mutasi pada individu (jadwal) secara acak berdasarkan peluang yang ditentukan.

    Setiap sesi dalam individu memiliki kemungkinan untuk dimodifikasi secara acak 
    pada atribut `hari`, `jam_mulai` + `jam_selesai`, atau `kode_ruangan`.

    Args:
        individu (list): Daftar sesi jadwal dalam satu individu.
        dosen_list (list): Daftar dosen yang tersedia.
        ruang_list (list): Daftar ruangan yang tersedia, masing-masing berupa dict dengan key 'kode'.
        peluang_mutasi (float, optional): Peluang untuk setiap sesi dimutasi. Default 0.1.

    Returns:
        list: Individu yang telah mengalami mutasi (bisa sama atau berbeda).
    """
    
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")
    pilihan_waktu = range(7, 19 + 1)
    max_attempt = 10

    for sesi in individu:
        matkul = matakuliah_list.get(sesi.kode_matkul[:5], {})
        if matkul.get("online") or matkul.get("take_all_lecture"):
            continue
        if sesi.tipe_kelas == "ONLINE": continue
        
        if random.random() < peluang_mutasi:
            # Randomly mutate hari, jam, atau ruangan
            attr = random.choice(['hari', 'jam', 'ruang'])

            if attr == 'hari':
                sesi.hari = random.choice(pilihan_hari_dosen) if sesi.kode_dosen != "AS" else random.choice(pilihan_hari_asisten)
            elif attr == 'jam':
                success= False
                attempt = 1
                while not success and attempt <= max_attempt:
                    jam_mulai = random.choice(pilihan_waktu)
                    if jam_mulai + sesi.sks_akademik <= max(pilihan_waktu):
                        sesi.jam_mulai = jam_mulai
                        sesi.jam_selesai = jam_mulai + sesi.sks_akademik
                        success = True
                        break
                    attempt += 1
                if not success:
                    sesi.jam_mulai, sesi.jam_selesai = 7, 7 + sesi.sks_akademik
            elif attr == 'ruang':
                is_asisten = sesi.kode_dosen == "AS"
                kapasitas_ruangan_dosen = next((sesi_dosen.kapasitas for sesi_dosen in individu if sesi_dosen.kode_matkul == sesi.kode_matkul[:-3]), 0) if is_asisten else 0
                
                ruang_pengganti = rand_ruangan(
                    list_ruangan=ruang_list,
                    data_matkul=matkul,
                    bidang=sesi.tipe_kelas if sesi.tipe_kelas == "INTERNATIONAL" else None,
                    forAsisten=is_asisten,
                    kapasitas_ruangan_dosen=kapasitas_ruangan_dosen
                )
                sesi.kode_ruangan = ruang_pengganti['kode']
    return individu

def genetic_algorithm(matakuliah_list, dosen_list, ruang_list, ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.1):
    """
    Melakukan mutasi pada individu (jadwal) secara acak berdasarkan peluang yang ditentukan.

    Setiap sesi dalam individu memiliki kemungkinan untuk dimodifikasi secara acak 
    pada atribut `hari`, `jam_mulai` + `jam_selesai`, atau `kode_ruangan`.

    Args:
        matakuliah_list (list): Daftar matakuliah yang dibuka pada semester berikutnya.
        dosen_list (list): Daftar dosen yang tersedia.
        ruang_list (list): Daftar ruangan yang tersedia, masing-masing berupa dict dengan key 'kode'.
        ukuran_populasi (int, optional): Jumlah populasi dalam setiap generasi. Default 75.
        jumlah_generasi (int, optional): Jumlah algoritma menghasilkan penerus. Default 100.
        peluang_mutasi (float, optional): Peluang untuk setiap sesi dimutasi. Default 0.1.

    Returns:
        dict: Jadwal hasil algoritma genetika dalam bentuk dictionary.
    """
    if not matakuliah_list: print('[ KOSONG ] list mata kuliah')
    if not dosen_list: print('[ KOSONG ] list dosen')
    if not ruang_list: print('[ KOSONG ] list ruang')

    try:
        for dosen in dosen_list:
            if dosen.get("preferensi") and dosen["preferensi"].get("hindari_jam"):
                dosen["preferensi"]["hindari_jam"] = [int(j) for j in dosen["preferensi"]["hindari_jam"]]
        
        for matkul in matakuliah_list:
            kode_dosen = set(dosen["nip"] for dosen in dosen_list if dosen["nama"] in matkul.get("dosen_ajar", []))
            if kode_dosen: matkul["dosen_ajar"] = kode_dosen

        matkul_by_kode = {m["kode"]: m for m in matakuliah_list}
        
        populasi = generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi)
        probabilitas_agresif_repair = random.random()
        populasi = [repair_jadwal(j, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list) for j in populasi]

        best_fitness_global = float('-inf')
        best_individual_global = None

        for gen in range(jumlah_generasi):
            probabilitas_agresif_repair = random.random()

            fitness_scores = [hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) for individu in populasi]
            next_gen = []

            # Generate anak baru
            while len(next_gen) < ukuran_populasi:
                parent1 = roulette_selection(populasi, fitness_scores)
                parent2 = roulette_selection(populasi, fitness_scores)

                child1, child2 = crossover(parent1, parent2)

                child1 = mutasi(child1, matkul_by_kode, ruang_list, peluang_mutasi)
                child2 = mutasi(child2, matkul_by_kode, ruang_list, peluang_mutasi)

                child1 = repair_jadwal(child1, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list)
                child2 = repair_jadwal(child2, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list)
                
                next_gen.append(child1)
                if len(next_gen) < ukuran_populasi:
                    next_gen.append(child2)
                
            populasi = next_gen

            fitness_scores = [hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) for individu in populasi]
            unique_fitness = set(fitness_scores)
            gen_worst_fitness = min(fitness_scores)
            gen_best_fitness = max(fitness_scores)
            gen_best_individual = populasi[fitness_scores.index(gen_best_fitness)]
            
            if gen > 5 and len(unique_fitness) < 5:
                break
            elif gen > 5 and gen_best_fitness == 1000:
                print(f"{'[ Found 1000 ]':<20} {gen}")
                best_fitness_global = gen_best_fitness
                best_individual_global = copy.deepcopy(gen_best_individual)
                isSomeDosenNotSet, whoNotSet = is_some_lecture_not_scheduled(gen_best_individual, matakuliah_list, dosen_list)
                # Kalo semua dosen udah di schedule: return
                if not isSomeDosenNotSet:
                    break
            elif gen > 5 and gen_best_fitness >= best_fitness_global:
                gen_fitness_report = hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, return_detail=True)
                dosen_bentrok = gen_fitness_report.get("bentrok_dosen") > 0
                ruangan_bentrok = gen_fitness_report.get("bentrok_ruangan") > 0
                asisten_bentrok = gen_fitness_report.get("bentrok_dosen_asdos") > 0
                solo_team = len(gen_fitness_report.get("solo_team_teaching", {}).keys()) > 0
                if not (dosen_bentrok or ruangan_bentrok or asisten_bentrok or solo_team):
                    print(f"{'[ Update Best ]':<20} {gen} {gen_best_fitness} ( Unique: {len(unique_fitness)}/{len(populasi)} )")
                    best_fitness_global = gen_best_fitness
                    best_individual_global = copy.deepcopy(gen_best_individual)

            if int(gen) % 20 == 0 or int(gen) == jumlah_generasi - 1:
                print(f"\n{f'[Gen {gen}]':<10} BEST ALLTIME: {best_fitness_global}")
                print(f"All Unique Fitness: ({len(unique_fitness)}/{len(populasi)}) {f'(min: {gen_worst_fitness})':<12}{f'(max: {gen_best_fitness})':<12}")
                hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, True)
                print("\n")

        print("\n===== ===== ===== ===== ===== FINAL RES ===== ===== ===== ===== =====")
        print(f"{f'[LAST GEN {gen}]':<10} Count Unique Fitness {len(unique_fitness)}/{len(populasi)}")
        print(f"{f'BEST ALLTIME':<25}: {best_fitness_global}")
        # if best_fitness_global != 1000:
        #     best_individual_global = repair_jadwal_hard(best_individual_global, matakuliah_list, dosen_list, ruang_list)
        #     report_fitness = hitung_fitness(best_individual_global, matakuliah_list, dosen_list, ruang_list, detail=True, return_detail=True)
        #     print(f"{f'REPAIRED BEST ALLTIME':<25}: {report_fitness['score']}")
        # else:
        report_fitness = hitung_fitness(best_individual_global, matakuliah_list, dosen_list, ruang_list, detail=True, return_detail=True)
    except Exception as e:
        print(f"{'[ GA ]':<25} Error: {e}")
        print(traceback.print_exc())
        return { 'status': False, 'message': e }
    
    return { 'status': True, 'data': convertOutputToDict(best_individual_global), 'score': report_fitness }