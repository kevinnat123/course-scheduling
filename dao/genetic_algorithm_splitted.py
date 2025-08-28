import random, copy, traceback
from collections import defaultdict

class JadwalKuliah:
    def __init__(
            self, 
            kode_matkul:str, kode_dosen:str, sks_akademik:int, kode_ruangan:str, kapasitas:int, 
            hari:str, jam_mulai:int, jam_selesai:int, 
            tipe_kelas:str, program_studi:str, team_teaching:bool=False,
            changeable:bool=True):
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
        self.changeable = changeable

MAX_ATTEMPT = 10
MIN_ATTEMPT = 3
MAX_BEBAN_SKS_DOSEN = 12
BOBOT_PENALTI = {
    "ruangan_bentrok": 20,          # Jadwal Ruangan Bertabrakan
    "dosen_bentrok": 20,            # Jadwal Dosen Bertabrakan
    "asdos_nabrak_dosen": 20,       # Jadwal Dosen dan Asisten Berjalan Bersamaan
    "dosen_nganggur": 15,           # Dosen Tetap Tidak Mengajar
    "kelas_gaib": 15,               # Kelas Dosen atau Asisten Hilang atau Tidak Lengkap
    "solo_team": 15,                # Solo Team_Teaching
    "diluar_jam_kerja": 15,         # Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19
    "dosen_overdosis": 10,          # Beban SKS Dosen melebihi 12 sks
    "kapasitas_kelas_terbatas": 10, # Cek Total Kelas Bisa Cangkup Semua Mahasiswa
    "tipe_ruang_salah": 5,          # Tipe Ruangan Tidak Sesuai
    "melanggar_preferensi": 5,      # Tidak Sesuai dengan permintaan / request dosen
}

def convertOutputToDict(jadwal_list):
    """
    Menkonversi object jadwal menjadi dictionary.

    Args:
        jadwal_list (list of object): Jadwal yang sudah berhasil di generate.

    Returns:
        dict: Jadwal dalam bentuk dictionary.
    """

    jadwal = []

    for sesi in jadwal_list:
        s = {}
        s["kode_matkul"] = sesi.kode_matkul
        s["kode_dosen"] = sesi.kode_dosen
        s["sks_akademik"] = sesi.sks_akademik
        s["kode_ruangan"] = sesi.kode_ruangan
        s["kapasitas"] = sesi.kapasitas
        s["hari"] = sesi.hari
        s["jam_mulai"] = sesi.jam_mulai
        s["jam_selesai"] = sesi.jam_selesai
        s["tipe_kelas"] = sesi.tipe_kelas  # 'TEORI' atau 'PRAKTIKUM' atau 'INTERNATIONAL'
        s["program_studi"] = sesi.program_studi
        s["team_teaching"] = sesi.team_teaching
        jadwal.append(s)

    return jadwal

def bkd_info(jadwal, dosen_by_nip, matkul_by_kode):
    """
        Menghitung informasi BKD tiap dosen

        Args:
            jadwal (list of object): Jadwal yang akan dikalkulasi.
            dosen_by_nip (dict): Data dosen yang disimpan berdasarkan nip.
            matkul_by_kode (dict): Data mata kuliah yang disimpan berdasarkan kode matkul.

        Returns:
            dict: Hasil kalkulasi BKD dengan format {nip: {sks: value, matakuliah: dict}}
    """

    bkd = defaultdict()
    jadwal_by_dosen = defaultdict(list)
    for sesi in jadwal:
        jadwal_by_dosen[sesi.kode_dosen].append(sesi)
    for nip, dosen in dosen_by_nip.items():
        matkul_count = defaultdict()
        sbs = []
        for sesi in jadwal_by_dosen.get(nip, []):
            matkul = matkul_by_kode.get(sesi.kode_matkul[:5], {})
            if matkul.get("take_all_lecture"):
                continue
            
            is_team = "-team" if sesi.team_teaching else ""
            if sesi.tipe_kelas == "INTERNATIONAL":
                count_dosen = matkul.get("jumlah_dosen_internasional", 1)
            else:
                count_dosen = matkul.get("jumlah_dosen", 1)

            if f"{sesi.kode_matkul[:5]}{is_team}" not in matkul_count: 
                matkul_count[f"{sesi.kode_matkul[:5]}{is_team}"] = {"sks": sesi.sks_akademik / count_dosen, "jml_kelas": 0}
            matkul_count[f"{sesi.kode_matkul[:5]}{is_team}"]["jml_kelas"] += 1

        if dosen["status"] == "TETAP":
            for matkul, detail in matkul_count.items():
                sbs.append(((1/3) * detail["sks"]) * ((2 * detail["jml_kelas"]) + 1))
        elif dosen["status"] == "TIDAK_TETAP":
            for matkul, detail in matkul_count.items():
                sbs.append(detail["sks"] * detail["jml_kelas"])
        
        bkd[nip] = {"sks": sum(sbs), "matakuliah": matkul_count}
    return bkd

#   FUNCTION PENDUKUNG
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======

#   RELATED FUNCTION ke MAIN FUNCTION
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======

#   FUNCTION of GA's STEPs
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======

#   MAIN GA's FUNCTION
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======
def genetic_algorithm_dosen(matakuliah_list, dosen_list, ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.1):
    """
    Melakukan mutasi pada individu (jadwal) secara acak berdasarkan peluang yang ditentukan.

    Setiap sesi dalam individu memiliki kemungkinan untuk dimodifikasi secara acak 
    pada atribut `hari`, `jam_mulai` + `jam_selesai`, atau `kode_ruangan`.

    Args:
        matakuliah_list (list): Daftar matakuliah yang dibuka pada semester berikutnya.
        dosen_list (list): Daftar dosen yang tersedia.
        ukuran_populasi (int, optional): Jumlah populasi dalam setiap generasi. Default 75.
        jumlah_generasi (int, optional): Jumlah algoritma menghasilkan penerus. Default 100.
        peluang_mutasi (float, optional): Peluang untuk setiap sesi dimutasi. Default 0.1.

    Returns:
        dict: Jadwal hasil algoritma genetika dalam bentuk dictionary.
    """
    if not matakuliah_list: print('[ KOSONG ] list mata kuliah')
    if not dosen_list: print('[ KOSONG ] list dosen')

    try:
        # Persiapan data lookup
        for dosen in dosen_list:
            if dosen.get("preferensi") and dosen["preferensi"].get("hindari_jam"):
                dosen["preferensi"]["hindari_jam"] = [int(j) for j in dosen["preferensi"]["hindari_jam"]]
        for matkul in matakuliah_list:
            kode_dosen = set(dosen["nip"] for dosen in dosen_list if dosen["nama"] in matkul.get("dosen_ajar", []))
            if kode_dosen: matkul["dosen_ajar"] = kode_dosen
        matkul_by_kode = {m["kode"]: m for m in matakuliah_list}
        dosen_by_nip = {d["nip"]: d for d in dosen_list}

        # Generate populasi awal dan perbaiki
        populasi = generate_populasi(matakuliah_list, dosen_list, ukuran_populasi)
        probabilitas_agresif_repair = random.random()
        populasi = [
            repair_jadwal(j, probabilitas_agresif_repair, matakuliah_list, dosen_list) 
            for j in populasi
        ]

        best_gen = None
        best_fitness_global = float('-inf')
        best_individual_global = None

        for gen in range(jumlah_generasi):
            probabilitas_agresif_repair = random.random()

            # Hitung fitness untuk populasi
            fitness_scores = [
                hitung_fitness(individu, matakuliah_list, dosen_list) 
                for individu in populasi
            ]
            next_gen = []

            # Proses reproduksi
            while len(next_gen) < ukuran_populasi:
                parent1 = roulette_selection(populasi, fitness_scores)
                parent2 = roulette_selection(populasi, fitness_scores)

                child1, child2 = crossover(parent1, parent2)

                # Mutasi
                child1 = mutasi(child1, matkul_by_kode, dosen_by_nip, peluang_mutasi)
                child2 = mutasi(child2, matkul_by_kode, dosen_by_nip, peluang_mutasi)

                # Repair jadwal
                child1 = repair_jadwal(child1, probabilitas_agresif_repair, matakuliah_list, dosen_list)
                child2 = repair_jadwal(child2, probabilitas_agresif_repair, matakuliah_list, dosen_list)
                
                next_gen.append(child1)
                if len(next_gen) < ukuran_populasi:
                    next_gen.append(child2)
                
            populasi = next_gen

            # Evaluasi generasi
            fitness_scores = [
                hitung_fitness(individu, matakuliah_list, dosen_list) 
                for individu in populasi
            ]
            unique_fitness = set(fitness_scores)
            gen_worst_fitness = min(fitness_scores)
            gen_best_fitness = max(fitness_scores)
            gen_best_individual = populasi[fitness_scores.index(gen_best_fitness)]
            
            if int(gen) % 20 == 0 or int(gen) == jumlah_generasi - 1:
                print(f"\n{f'[Gen {gen}]':<10} BEST ALLTIME: {best_fitness_global} (Gen {best_gen})")
                print(f"All Unique Fitness: ({len(unique_fitness)}/{len(populasi)}) {f'(min: {gen_worst_fitness})':<12}{f'(max: {gen_best_fitness})':<12}")
                hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, True)
                print("\n")
            
            if gen < 0:
                continue

            if gen_best_fitness == 1000:
                best_gen = gen
                best_fitness_global = gen_best_fitness
                best_individual_global = copy.deepcopy(gen_best_individual)
                isSomeDosenNotSet, whoNotSet = is_some_lecture_not_scheduled(gen_best_individual, matakuliah_list, dosen_list)
                # Kalo semua dosen udah di schedule: return
                if not isSomeDosenNotSet:
                    break
            elif gen_best_fitness >= best_fitness_global:
                gen_fitness_report = hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, return_detail=True)
                dosen_bentrok = gen_fitness_report.get("bentrok_dosen") > 0
                ruangan_bentrok = gen_fitness_report.get("bentrok_ruangan") > 0
                asisten_bentrok = gen_fitness_report.get("bentrok_dosen_asdos") > 0
                # solo_team = len(gen_fitness_report.get("solo_team_teaching", {}).keys()) > 0
                no_conflict = not (
                    dosen_bentrok or 
                    ruangan_bentrok or 
                    asisten_bentrok
                )

                if no_conflict:
                    best_gen = gen
                    best_fitness_global = gen_best_fitness
                    best_individual_global = copy.deepcopy(gen_best_individual)

            # Stop jika variasi fitness terlalu sedikit
            if len(unique_fitness) < 5:
                break

        print("\n===== ===== ===== ===== ===== FINAL RES ===== ===== ===== ===== =====")
        print(f"{f'[LAST GEN {gen}]':<10} Count Unique Fitness {len(unique_fitness)}/{len(populasi)}")
        print(f"{f'BEST ALLTIME (Gen: {best_gen})':<25}: {best_fitness_global}")
        
        # Final repair jika belum perfect
        if best_fitness_global != 1000:
            repaired_individual_global = repair_jadwal_hard(best_individual_global, matakuliah_list, dosen_list)
            fitness_repaired_global = hitung_fitness(repaired_individual_global, matakuliah_list, dosen_list)
            print(f"{f'REPAIRED BEST ALLTIME':<25}: {fitness_repaired_global}")
            if fitness_repaired_global > best_fitness_global:
                best_individual_global = repaired_individual_global

        # Hasil akhir
        report_fitness = hitung_fitness(best_individual_global, matakuliah_list, dosen_list, detail=True, return_detail=True)
        bkd = bkd_info(best_individual_global, dosen_by_nip, matkul_by_kode)
    except Exception as e:
        print(f"{'[ GA ]':<25} Error: {e}")
        print(traceback.print_exc())
        return { 'status': False, 'message': e }

    return { 
        'status': True, 
        'data': convertOutputToDict(best_individual_global), 
        'score': report_fitness, 
        'bkd': bkd 
    }

def genetic_algorithm_ruangan(matakuliah_list, dosen_list, ruang_list, ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.1):
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
        # Persiapan data lookup
        for dosen in dosen_list:
            if dosen.get("preferensi") and dosen["preferensi"].get("hindari_jam"):
                dosen["preferensi"]["hindari_jam"] = [int(j) for j in dosen["preferensi"]["hindari_jam"]]
        for matkul in matakuliah_list:
            kode_dosen = set(dosen["nip"] for dosen in dosen_list if dosen["nama"] in matkul.get("dosen_ajar", []))
            if kode_dosen: matkul["dosen_ajar"] = kode_dosen
        matkul_by_kode = {m["kode"]: m for m in matakuliah_list}
        dosen_by_nip = {d["nip"]: d for d in dosen_list}

        # Generate populasi awal dan perbaiki
        populasi = generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi)
        probabilitas_agresif_repair = random.random()
        populasi = [
            repair_jadwal(j, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list) 
            for j in populasi
        ]

        best_gen = None
        best_fitness_global = float('-inf')
        best_individual_global = None

        for gen in range(jumlah_generasi):
            probabilitas_agresif_repair = random.random()

            # Hitung fitness untuk populasi
            fitness_scores = [
                hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) 
                for individu in populasi
            ]
            next_gen = []

            # Proses reproduksi
            while len(next_gen) < ukuran_populasi:
                parent1 = roulette_selection(populasi, fitness_scores)
                parent2 = roulette_selection(populasi, fitness_scores)

                child1, child2 = crossover(parent1, parent2)

                # Mutasi
                child1 = mutasi(child1, matkul_by_kode, ruang_list, dosen_by_nip, peluang_mutasi)
                child2 = mutasi(child2, matkul_by_kode, ruang_list, dosen_by_nip, peluang_mutasi)

                # Repair jadwal
                child1 = repair_jadwal(child1, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list)
                child2 = repair_jadwal(child2, probabilitas_agresif_repair, matakuliah_list, dosen_list, ruang_list)
                
                next_gen.append(child1)
                if len(next_gen) < ukuran_populasi:
                    next_gen.append(child2)
                
            populasi = next_gen

            # Evaluasi generasi
            fitness_scores = [
                hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) 
                for individu in populasi
            ]
            unique_fitness = set(fitness_scores)
            gen_worst_fitness = min(fitness_scores)
            gen_best_fitness = max(fitness_scores)
            gen_best_individual = populasi[fitness_scores.index(gen_best_fitness)]
            
            if int(gen) % 20 == 0 or int(gen) == jumlah_generasi - 1:
                print(f"\n{f'[Gen {gen}]':<10} BEST ALLTIME: {best_fitness_global} (Gen {best_gen})")
                print(f"All Unique Fitness: ({len(unique_fitness)}/{len(populasi)}) {f'(min: {gen_worst_fitness})':<12}{f'(max: {gen_best_fitness})':<12}")
                hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, True)
                print("\n")
            
            if gen < 0:
                continue

            if gen_best_fitness == 1000:
                best_gen = gen
                best_fitness_global = gen_best_fitness
                best_individual_global = copy.deepcopy(gen_best_individual)
                isSomeDosenNotSet, whoNotSet = is_some_lecture_not_scheduled(gen_best_individual, matakuliah_list, dosen_list)
                # Kalo semua dosen udah di schedule: return
                if not isSomeDosenNotSet:
                    break
            elif gen_best_fitness >= best_fitness_global:
                gen_fitness_report = hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, return_detail=True)
                dosen_bentrok = gen_fitness_report.get("bentrok_dosen") > 0
                ruangan_bentrok = gen_fitness_report.get("bentrok_ruangan") > 0
                asisten_bentrok = gen_fitness_report.get("bentrok_dosen_asdos") > 0
                # solo_team = len(gen_fitness_report.get("solo_team_teaching", {}).keys()) > 0
                no_conflict = not (
                    dosen_bentrok or 
                    ruangan_bentrok or 
                    asisten_bentrok
                )

                if no_conflict:
                    best_gen = gen
                    best_fitness_global = gen_best_fitness
                    best_individual_global = copy.deepcopy(gen_best_individual)

            # Stop jika variasi fitness terlalu sedikit
            if len(unique_fitness) < 5:
                break

        print("\n===== ===== ===== ===== ===== FINAL RES ===== ===== ===== ===== =====")
        print(f"{f'[LAST GEN {gen}]':<10} Count Unique Fitness {len(unique_fitness)}/{len(populasi)}")
        print(f"{f'BEST ALLTIME (Gen: {best_gen})':<25}: {best_fitness_global}")
        
        # Final repair jika belum perfect
        if best_fitness_global != 1000:
            repaired_individual_global = repair_jadwal_hard(best_individual_global, matakuliah_list, dosen_list, ruang_list)
            fitness_repaired_global = hitung_fitness(repaired_individual_global, matakuliah_list, dosen_list, ruang_list)
            print(f"{f'REPAIRED BEST ALLTIME':<25}: {fitness_repaired_global}")
            if fitness_repaired_global > best_fitness_global:
                best_individual_global = repaired_individual_global

        # Hasil akhir
        report_fitness = hitung_fitness(best_individual_global, matakuliah_list, dosen_list, ruang_list, detail=True, return_detail=True)
        bkd = bkd_info(best_individual_global, dosen_by_nip, matkul_by_kode)
    except Exception as e:
        print(f"{'[ GA ]':<25} Error: {e}")
        print(traceback.print_exc())
        return { 'status': False, 'message': e }

    return { 
        'status': True, 
        'data': convertOutputToDict(best_individual_global), 
        'score': report_fitness, 
        'bkd': bkd 
    }
#   ======= ======= ======= ======= ======= ======= ======= ======= ======= =======