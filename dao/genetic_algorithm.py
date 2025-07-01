import random, copy

class JadwalKuliah:
    def __init__(
            self, 
            kode_matkul, kode_dosen, sks_akademik, kode_ruangan, kapasitas, 
            hari, jam_mulai, jam_selesai, 
            tipe_kelas, program_studi):
        self.kode_matkul = kode_matkul
        self.kode_dosen = kode_dosen
        self.sks_akademik = sks_akademik
        self.kode_ruangan = kode_ruangan
        self.kapasitas = kapasitas
        self.hari = hari
        self.jam_mulai = jam_mulai
        self.jam_selesai = jam_selesai
        self.tipe_kelas = tipe_kelas  # 'TEORI' atau 'PRAKTIKUM'
        self.program_studi = program_studi

# TO BE CHECKED:
# (15)  Jadwal Ruangan Bertabrakan                                  >> ruangan_bentrok           (DONE)
# (15)  Jadwal Dosen Bertabrakan                                    >> dosen_bentrok             (DONE)
# (15)  Jadwal Dosen dan Asisten Berjalan Bersamaan                 >> asdos_nabrak_dosen        (DONE)
# (15)  Kelas Dosen atau Asisten Hilang atau Tidak Lengkap          >> kelas_gaib                (DONE)
# (15)  Solo Team_Teaching                                          >> solo_team
# (10)  Beban SKS Dosen melebihi 12 sks                             >> dosen_overdosis           (DONE)
# (10)  Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19    >> diluar_jam_kerja          (DONE)
# (10)  Cek Total Kelas Bisa Cangkup Semua Mahasiswa                >> kapasitas_kelas_terbatas  (DONE)
# (5)   Tidak Sesuai dengan permintaan / request dosen              >> melanggar_preferensi      (DONE)
BOBOT_PENALTI = {
    "ruangan_bentrok": 15,
    "dosen_bentrok": 15,
    "asdos_nabrak_dosen": 15,
    "kelas_gaib": 15,
    "solo_team": 15,
    "dosen_overdosis": 10,
    "diluar_jam_kerja": 10,
    "kapasitas_kelas_terbatas": 10,
    "melanggar_preferensi": 5,

    "weekend_class": 10,
    "istirahat": 5,
    "salah_tipe_ruangan": 3,
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

def find_available_schedule(jadwal:list, kode:str, hari:str):
    """
    Mencari waktu yang tersedia dari jadwal yang sudah ada berdasarkan hari yang dipilih.

    Args:
        jadwal (list): List jadwal ruangan / dosen yang sudah ada.
        kode (str): Kode yang akan diperiksa (kode ruangan / nip).
        hari (str): Hari yang akan diperiksa jadwalnya.

    Returns:
        list: List jadwal yang bisa digunakan (jam).
    """
    
    pilihan_jam = list(range(7, 19 + 1)) if hari != "SABTU" else list(range(7, 13 + 1))
    
    jadwal_sesuai_hari = [sesi for sesi in jadwal[kode] if sesi['hari'] == hari] if jadwal[kode] else []
    used_jam = []
    for sesi in jadwal_sesuai_hari:
        used_jam.extend(range(sesi['jam_mulai'], sesi['jam_selesai']))

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
    else:
        return None  # Diluar jangkauan 1-26

def find_missing_course(jadwal, matakuliah_list):
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

def sync_team_teaching(sesi_dosen, jadwal, jadwal_dosen, jadwal_ruangan):
    for sesi_lain in jadwal:
        if sesi_lain.kode_matkul == sesi_dosen.kode_matkul: # and sesi_lain.kode_dosen != sesi_dosen.kode_dosen:
            old_hari = sesi_lain.hari
            old_jam_mulai = sesi_lain.jam_mulai
            old_jam_selesai = sesi_lain.jam_selesai
            old_kode_ruangan = sesi_lain.kode_ruangan
            
            sesi_lain.hari = sesi_dosen.hari
            sesi_lain.jam_mulai = sesi_dosen.jam_mulai
            sesi_lain.jam_selesai = sesi_dosen.jam_selesai
            sesi_lain.kode_ruangan = sesi_dosen.kode_ruangan
            sesi_lain.kapasitas = sesi_dosen.kapasitas
            sesi_lain.tipe_kelas = sesi_dosen.tipe_kelas

            if sesi_lain.kode_dosen not in jadwal_dosen:
                jadwal_dosen[sesi_lain.kode_dosen] = []
                
            jadwal_dosen[sesi_lain.kode_dosen] = [
                detail for detail in jadwal_dosen[sesi_lain.kode_dosen]
                if not (detail['hari'] == old_hari and detail['jam_mulai'] == old_jam_mulai and detail['jam_selesai'] == old_jam_selesai)
            ]
            jadwal_dosen[sesi_lain.kode_dosen].append({
                'hari': sesi_lain.hari,
                'jam_mulai': sesi_lain.jam_mulai,
                'jam_selesai': sesi_lain.jam_selesai,
            })

            if sesi_dosen.kode_ruangan not in jadwal_ruangan:
                jadwal_ruangan[sesi_dosen.kode_ruangan] = []
            if old_kode_ruangan not in jadwal_ruangan:
                jadwal_ruangan[old_kode_ruangan] = []
                
            jadwal_ruangan[old_kode_ruangan] = [
                detail for detail in jadwal_ruangan[old_kode_ruangan]
                if not (detail['hari'] == old_hari and detail['jam_mulai'] == old_jam_mulai and detail['jam_selesai'] == old_jam_selesai)
            ]
            jadwal_ruangan[sesi_dosen.kode_ruangan].append({
                'hari': sesi_lain.hari,
                'jam_mulai': sesi_lain.jam_mulai,
                'jam_selesai': sesi_lain.jam_selesai,
            })
            
    return jadwal_dosen, jadwal_ruangan

def rand_dosen_pakar(list_dosen_pakar: list, dict_beban_sks_dosen: dict = {}, excluded_dosen: list = []):
    if len(list_dosen_pakar) > 1:
        list_beban_sks_dosen = [
            value for key, value in dict_beban_sks_dosen.items() 
            if key in [
                dosen['nip'] for dosen in list_dosen_pakar
                if dosen['nip'] not in excluded_dosen
            ]
        ]
        beban_sks_tertinggi_saat_ini = max(list_beban_sks_dosen)

        kandidat_dosen = [
            dosen for dosen in list_dosen_pakar
            if (
                dict_beban_sks_dosen[dosen['nip']] < beban_sks_tertinggi_saat_ini 
                if any(sks_dosen < beban_sks_tertinggi_saat_ini for sks_dosen in list_beban_sks_dosen) 
                else dict_beban_sks_dosen[dosen['nip']] <= beban_sks_tertinggi_saat_ini 
            )
        ]
        # sorted(dosen_list, key=lambda dosen: (len(dosen.get("matkul_ajar", [])), len(dosen.get('pakar', []))), reverse=True)
        
        return random.choice([ dosen for dosen in kandidat_dosen if dosen['nip'] not in excluded_dosen ] or kandidat_dosen)
    elif len(list_dosen_pakar) == 1:
        return list_dosen_pakar[0]
    
def rand_ruangan(list_ruangan: list, data_matkul: dict, excluded_room: list = [], forAsisten: bool = False, kapasitas_ruangan_dosen: int = 0):
    toChecked = [data_matkul["prodi"], "GENERAL"]
    toChecked.extend(data_matkul.get("bidang", []))
    ruangan_prodi = [
        ruangan for ruangan in list_ruangan
        if any(plot in ruangan["plot"] for plot in data_matkul.get('bidang', [])) and
            ruangan["kode"] not in excluded_room
    ]
    if not ruangan_prodi:
        ruangan_prodi = [
            ruangan for ruangan in list_ruangan
            if any(plot in ruangan["plot"] for plot in toChecked) and
                ruangan["kode"] not in excluded_room
        ]
    
    if not forAsisten:
        kandidat_ruangan = [
            ruangan for ruangan in ruangan_prodi 
            if ruangan['tipe_ruangan'] == data_matkul['tipe_kelas']
            # if ruangan["tipe_ruangan"] in ([data_matkul["tipe_kelas"]] if data_matkul.get("asistensi", None) else [data_matkul["tipe_kelas"], "RAPAT"])
        ]

        if data_matkul.get("asistensi", None):
            if data_matkul.get("tipe_kelas_asistensi", "PRAKTIKUM") == "PRAKTIKUM":
                kandidat_ruangan = [
                    ruangan for ruangan in kandidat_ruangan 
                    if ruangan["kapasitas"] < max(
                        [ 
                            ruangan["kapasitas"] for ruangan in list_ruangan 
                            if ruangan["tipe_ruangan"] == "PRAKTIKUM" 
                        ]
                    )
                ]
    elif forAsisten:
        kandidat_ruangan = [
            ruangan for ruangan in ruangan_prodi 
            if ruangan["tipe_ruangan"] == data_matkul.get("tipe_kelas_asistensi", "TEORI") and
                ruangan["kapasitas"] >= kapasitas_ruangan_dosen
        ]

    # max_room_capacity = max([ ruangan["kapasitas"] for ruangan in kandidat_ruangan ])
    
    if len(kandidat_ruangan) > 1:
        bobot_kandidat_ruangan = [
            (len(set(ruangan.get("plot", [])) & set(data_matkul.get("bidang", [])))*10 or 1) * 
                (10 if data_matkul["prodi"] in ruangan.get("plot", []) else 1) * 
                (ruangan["kapasitas"] / 10)
            for ruangan in kandidat_ruangan
        ]

        ruangan_terpilih = random.choices(
            population=kandidat_ruangan, 
            weights=bobot_kandidat_ruangan, 
            k=1)[0]
        return ruangan_terpilih
    elif len(kandidat_ruangan) == 1:
        return kandidat_ruangan[0]    
 
def repair_jadwal(jadwal, matakuliah_list, dosen_list, ruang_list):
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")

    max_attempt = 10

    jadwal_dosen = {} # Cek Jadwal Dosen {'kode': [{'hari': '', 'jam_mulai': 0, 'jam_selesai': 0}]}
    jadwal_ruangan = {} # Cek Jadwal Ruangan {'kode': [{'hari': '', 'jam_mulai': 0, 'jam_selesai': 0}]}
    beban_dosen = {} # Cek SKS Dosen {'kode': 0}

    # AMBIL INITIAL
    for ruang in ruang_list:
        if ruang['kode'] not in jadwal_ruangan: jadwal_ruangan[ruang['kode']] = []
    for dosen in dosen_list:
        if dosen['nip'] not in jadwal_dosen: jadwal_dosen[dosen['nip']] = []
        if dosen['nip'] not in beban_dosen: beban_dosen[dosen['nip']] = 0

    # HAPUS DATA MATKUL DUPLIKAT
    seen_kode_matkul = set()
    filtered_jadwal = []

    for sesi in jadwal:
        isTeamTeaching = next((matkul.get('team_teaching') for matkul in matakuliah_list if matkul['kode'] == (sesi.kode_matkul[:-1] if sesi.kode_dosen != "AS" else sesi.kode_matkul[:-4])), None)
        if sesi.kode_matkul in seen_kode_matkul:
            if isTeamTeaching and sesi.kode_dosen != "AS":
                filtered_jadwal.append(sesi)
        else:
            seen_kode_matkul.add(sesi.kode_matkul)
            filtered_jadwal.append(sesi)

    jadwal = filtered_jadwal

    # LOOP PERTAMA:
    # - REPAIR DOSEN DENGAN SKS BERLEBIH (DONE)
    # - REPAIR JADWAL DOSEN BENTROK (DONE)
    # - PENUHI KAPASITAS KELAS KALAU BERKURANG
    for sesi_dosen in jadwal:
        if sesi_dosen.kode_dosen != "AS":
            matkul = next((m for m in matakuliah_list if m['kode'] == sesi_dosen.kode_matkul[:-1]), None)
            dosen = next((d for d in dosen_list if d['nip'] == sesi_dosen.kode_dosen), None)
            preferensi_hari_dosen = [d for d in pilihan_hari_dosen if d not in dosen['preferensi']['hindari_hari']] if dosen.get('preferensi') and dosen['preferensi'].get('hindari_hari') else pilihan_hari_dosen

            if matkul:
                old_hari = sesi_dosen.hari
                old_jam_mulai = sesi_dosen.jam_mulai
                old_jam_selesai = sesi_dosen.jam_selesai
                old_kode_ruangan = sesi_dosen.kode_ruangan
                
                # Repair Dosen dg SKS Berlebih
                if beban_dosen[dosen['nip']] > (12 - sesi_dosen.sks_akademik):
                    dosen_pakar = [
                        d for d in dosen_list 
                        if (d.get("prodi") == matkul['prodi'] or d['status'] == "TIDAK_TETAP") and 
                            ((
                                (d.get('nama') or '') in (matkul.get('dosen_ajar') or []) or 
                                len(set(d.get('pakar') or []) & set(matkul.get('bidang') or [])) > 0
                            ) if matkul.get('bidang') or matkul.get('dosen_ajar') 
                            else True) and 
                            d["nip"] not in [sesi_lain.kode_dosen for sesi_lain in jadwal if sesi_lain.kode_matkul == sesi_dosen.kode_matkul] and
                            d['status'] != "TIDAK_AKTIF"
                    ]
                    if dosen_pakar:
                        sesi_dosen.kode_dosen = rand_dosen_pakar(list_dosen_pakar=dosen_pakar, dict_beban_sks_dosen=beban_dosen)["nip"]
                    
                conflict = False

                for sesi_lain in jadwal_ruangan[sesi_dosen.kode_ruangan]:
                    if sesi_dosen.hari == sesi_lain['hari']:
                        if sesi_dosen.jam_mulai < sesi_lain['jam_selesai'] and sesi_dosen.jam_selesai > sesi_lain['jam_mulai']:
                            conflict = True
                            break

                for sesi_lain in jadwal_dosen[sesi_dosen.kode_dosen]:
                    if sesi_dosen.hari == sesi_lain['hari']:
                        if sesi_dosen.jam_mulai < sesi_lain['jam_selesai'] and sesi_dosen.jam_selesai > sesi_lain['jam_mulai']:
                            conflict = True
                            break

                attempt = 1
                excluded_day = []
                excluded_room = []
                # Repair Jadwal Dosen Bentrok
                while conflict and attempt <= max_attempt:
                    # print(sesi_dosen.kode_matkul, sesi_dosen.kode_dosen, sesi_dosen.sks_akademik, sesi_dosen.hari)
                    available_room_schedule = find_available_schedule(jadwal_ruangan, sesi_dosen.kode_ruangan, sesi_dosen.hari)
                    available_lecturer_schedule = find_available_schedule(jadwal_dosen, sesi_dosen.kode_dosen, sesi_dosen.hari)

                    # Sesuaikan dengan jadwal team jika team teaching
                    if matkul.get('team_teaching'):
                        # print(f"bfr   {sesi_dosen.kode_matkul} {matkul['kode']} : {available_lecturer_schedule}")
                        for sesi_lain in jadwal:
                            if sesi_lain.kode_matkul == sesi_dosen.kode_matkul and sesi_lain.kode_dosen != sesi_dosen.kode_dosen:
                                other_lecturer_schedule = find_available_schedule(jadwal_dosen, sesi_lain.kode_dosen, sesi_dosen.hari)
                                available_lecturer_schedule = list(set(available_lecturer_schedule) & set(other_lecturer_schedule))
                        # print(f"aftr  {sesi_dosen.kode_matkul} {matkul['kode']} : {available_lecturer_schedule}")
                    
                    available_schedule = list(set(available_room_schedule) & set(available_lecturer_schedule))
                    
                    status = False
                    for jam in available_schedule:
                        rentang_waktu = list(range(jam, jam + matkul['sks_akademik'] + 1))
                        if all(r in available_schedule for r in rentang_waktu) and jam != 12:
                            status = True
                            conflict = False
                            sesi_dosen.jam_mulai = jam
                            sesi_dosen.jam_selesai = jam + matkul['sks_akademik']
                            break
                        else:
                            status = False

                    if not status:
                        excluded_day.append(sesi_dosen.hari)
                        # print('DOSEN pil ', pilihan_hari_dosen)
                        # print('DOSEN exc ', excluded_day)
                        # print('DOSEN     ', [d for d in pilihan_hari_dosen if d not in excluded_day])
                        # print('      ', available_schedule)
                        if all(d in excluded_day for d in preferensi_hari_dosen):
                            excluded_day = []
                            excluded_room.append(sesi_dosen.kode_ruangan)
                            ruang_pengganti = rand_ruangan(list_ruangan=ruang_list, data_matkul=matkul, excluded_room=excluded_room)

                            sesi_dosen.kode_ruangan = ruang_pengganti['kode']
                            sesi_dosen.kapasitas = ruang_pengganti['kapasitas']
                            sesi_dosen.tipe_kelas = ruang_pengganti['tipe_ruangan']
                        else:
                            sesi_dosen.hari = random.choice([d for d in preferensi_hari_dosen if d not in excluded_day])

                    attempt += 1
                
                beban_dosen[dosen['nip']] += sesi_dosen.sks_akademik
                if matkul.get("team_teaching"):
                    jadwal_dosen, jadwal_ruangan = sync_team_teaching(sesi_dosen=sesi_dosen, jadwal=jadwal, jadwal_dosen=jadwal_dosen, jadwal_ruangan=jadwal_ruangan)
                else:
                    jadwal_dosen[sesi_dosen.kode_dosen] = [
                        detail for detail in jadwal_dosen[sesi_dosen.kode_dosen]
                        if not (detail['hari'] == old_hari and detail['jam_mulai'] == old_jam_mulai and detail['jam_selesai'] == old_jam_selesai)
                    ]
                    jadwal_dosen[sesi_dosen.kode_dosen].append({
                        'hari': sesi_dosen.hari,
                        'jam_mulai': sesi_dosen.jam_mulai,
                        'jam_selesai': sesi_dosen.jam_selesai,
                    })
                        
                    jadwal_ruangan[old_kode_ruangan] = [
                        detail for detail in jadwal_ruangan[old_kode_ruangan]
                        if not (detail['hari'] == old_hari and detail['jam_mulai'] == old_jam_mulai and detail['jam_selesai'] == old_jam_selesai)
                    ]
                    jadwal_ruangan[sesi_dosen.kode_ruangan].append({
                        'hari': sesi_dosen.hari,
                        'jam_mulai': sesi_dosen.jam_mulai,
                        'jam_selesai': sesi_dosen.jam_selesai,
                    })

                # # NEW BACKUP (NOT DONE)
                # sukses = False
                # outer_attempt = 1
                # while not sukses and outer_attempt <= max_attempt:
                #     # CEK BENTROK DOSEN
                #     conflict = True
                #     attempt = 1
                #     excluded_dosen = []
                #     while conflict and attempt <= max_attempt:
                #         for sesi_lain in jadwal_dosen[sesi_dosen.kode_dosen]:
                #             if sesi_dosen.hari == sesi_lain['hari']:
                #                 if sesi_dosen.jam_mulai < sesi_lain['jam_selesai'] and sesi_dosen.jam_selesai > sesi_lain['jam_mulai']:
                #                     conflict = True
                #                     excluded_dosen.append(sesi.kode_dosen)

                #                     dosen_pakar = [
                #                         dosen for dosen in dosen_list
                #                         if (dosen.get("prodi") == matkul['prodi'] or dosen['status'] == "TIDAK_TETAP") and 
                #                             ((
                #                                 (dosen.get('nama') or '') in (matkul.get('dosen_ajar') or []) or 
                #                                 len(set(dosen.get('pakar') or []) & set(matkul.get('bidang') or [])) > 0
                #                             ) if matkul.get('bidang') or matkul.get('dosen_ajar') 
                #                             else True) and dosen["nip"] not in excluded_dosen and
                #                             dosen['status'] != "TIDAK_AKTIF"
                #                     ]
                                    
                #                     if dosen_pakar:
                #                         dosen_pengganti = rand_dosen_pakar(
                #                             list_dosen_pakar=dosen_pakar, 
                #                             dict_beban_sks_dosen=beban_dosen, 
                #                             excluded_dosen=excluded_dosen
                #                         )
                #                         sesi_dosen.kode_dosen = dosen_pengganti["nip"]
                #                         attempt = 0
                #                     else: attempt = max_attempt
                #                     break
                #                 else: conflict = False
                #             else: conflict = False
                        
                #         if not conflict: break
                #         attempt += 1
                        
                #     # CEK BENTROK RUANGAN
                #     conflict = True
                #     attempt = 1
                #     excluded_room = []
                #     while conflict and attempt <= max_attempt:
                #         for sesi_lain in jadwal_ruangan[sesi_dosen.kode_ruangan]:
                #             if sesi_dosen.hari == sesi_lain['hari']:
                #                 if sesi_dosen.jam_mulai < sesi_lain['jam_selesai'] and sesi_dosen.jam_selesai > sesi_lain['jam_mulai']:
                #                     conflict = True
                #                     excluded_room.append(sesi.kode_ruangan)

                #                     ruang_pengganti = rand_ruangan(
                #                         list_ruangan=ruang_list,
                #                         data_matkul=matkul,
                #                         excluded_room=excluded_room
                #                     )
                #                     if ruang_pengganti["kode"] not in excluded_room:
                #                         sesi.kode_ruangan = ruang_pengganti["kode"]
                #                         sesi_dosen.kapasitas = ruang_pengganti['kapasitas']
                #                         sesi_dosen.tipe_kelas = ruang_pengganti['tipe_ruangan']
                #                         attempt = 0
                #                     else:
                #                         # GANTI HARI - SESUAIKAN DENGAN ALL PREFERENSI DOSEN
                #                         print("GANTI HARI")
                #                     break
                #                 else: conflict = False
                #             else: conflict = False
                        
                #         if not conflict: 
                #             for team_schedule in jadwal:
                #                 if team_schedule.kode_matkul == sesi.kode_matkul:
                #                     team_schedule.kode_ruangan = sesi.kode_ruangan
                #             break
                #         attempt += 1

                #     outer_attempt += 1
                #     # if sukses:
                #     #     beban_dosen[dosen['nip']] += sesi_dosen.sks_akademik
                #     #     jadwal_ruangan[sesi_dosen.kode_ruangan].append({'hari': sesi_dosen.hari, 'jam_mulai': sesi_dosen.jam_mulai, 'jam_selesai': sesi_dosen.jam_selesai})
                #     #     jadwal_dosen[sesi_dosen.kode_dosen].append({'hari': sesi_dosen.hari, 'jam_mulai': sesi_dosen.jam_mulai, 'jam_selesai': sesi_dosen.jam_selesai})
                #     continue

    # LOOP KEDUA:
    # - TRY DISTRIBUSI SKS
    for sesi_dosen in jadwal:
        if sesi_dosen.kode_dosen != "AS":
            matkul = next((m for m in matakuliah_list if m['kode'] == sesi_dosen.kode_matkul[:-1]), None)
            info_dosen = next((d for d in dosen_list if d['nip'] == sesi_dosen.kode_dosen), None)
            if matkul and info_dosen:
                # Cek semua beban sks dosen ajar matkul bersangkutan
                beban_pengajar_matkul = {
                    dosen['nip']: beban_dosen[dosen['nip']] 
                    for dosen in dosen_list if dosen['nama'] in matkul.get('dosen_ajar', [])
                }

                if beban_pengajar_matkul:
                    dosen_beban_tertinggi, beban_tertinggi = max(beban_pengajar_matkul.items(), key=lambda x: x[1])
                    current_sks = beban_dosen.get(sesi_dosen.kode_dosen, 0)

                    if current_sks < beban_tertinggi:
                        # kalo beban sks current dosen < beban tertinggi, ambil jadwal dosen dg beban tertinggi
                        jadwal_dosen_beban_tertinggi = [
                            j for j in jadwal # jadwal_dosen[dosen_beban_tertinggi] 
                            if j.kode_matkul.startswith(matkul['kode']) and
                                j.kode_dosen == dosen_beban_tertinggi
                        ]

                        # cek apakah ada jadwal dosen beban tertinggi yang bisa digantikan current dosen
                        for jadwal_b in jadwal_dosen_beban_tertinggi:
                            # Cek Preferensi
                            preferensi = info_dosen.get('preferensi', {})
                            hindari_hari = preferensi.get('hindari_hari', [])
                            
                            if jadwal_b.hari in hindari_hari:
                                continue
                            
                            # Cek Bentrok
                            bentrok = False
                            for jadwal_a in jadwal_dosen.get(sesi_dosen.kode_dosen, []):
                                if jadwal_a['hari'] == jadwal_b.hari:
                                    if jadwal_b.jam_mulai < jadwal_a['jam_selesai'] and jadwal_b.jam_selesai > jadwal_a['jam_mulai']:
                                        bentrok = True
                                        break

                            if bentrok:
                                continue
                            
                            jadwal_b.kode_dosen = sesi_dosen.kode_dosen

                            jadwal_dosen[dosen_beban_tertinggi] = [
                                j for j in jadwal_dosen[dosen_beban_tertinggi]
                                if not (j['hari'] == jadwal_b.hari and j['jam_mulai'] == jadwal_b.jam_mulai and j['jam_selesai'] == jadwal_b.jam_selesai)
                            ]
                            jadwal_dosen[sesi_dosen.kode_dosen].append({
                                'hari': jadwal_b.hari,
                                'jam_mulai': jadwal_b.jam_mulai,
                                'jam_selesai': jadwal_b.jam_selesai
                            })

                            beban_dosen[dosen_beban_tertinggi] -= jadwal_b.sks_akademik
                            beban_dosen[sesi_dosen.kode_dosen] += jadwal_b.sks_akademik
                            break  # break setelah tukar sesi

    # LOOP KEDUA:
    # - REPAIR JADWAL ASISTEN KALAU BENTRO K DENGAN KELAS LAIN (DONE)
    for sesi_asisten in jadwal:
        if sesi_asisten.kode_dosen == "AS": # KODE ASISTEN
            matkul = next((m for m in matakuliah_list if m['kode'] == sesi_asisten.kode_matkul[:-4]), None)

            if matkul:
                conflict = False

                sesi_dosen = next((sesi_dosen for sesi_dosen in jadwal if sesi_dosen.kode_matkul == sesi_asisten.kode_matkul[:-3]), None)
                suggested_hari_asisten = pilihan_hari_asisten[pilihan_hari_dosen.index(sesi_dosen.hari):]
                for sesi_lain in jadwal_ruangan[sesi_asisten.kode_ruangan]:
                    if sesi_asisten.hari == sesi_lain['hari']:
                        if sesi_asisten.jam_mulai < sesi_lain['jam_selesai'] and sesi_asisten.jam_selesai > sesi_lain['jam_mulai']:
                            conflict = True
                            break

                attempt = 1
                excluded_day = []
                excluded_room = []
                # 2. Repair Jadwal Asisten
                while conflict and attempt <= max_attempt:
                    # print(sesi_asisten.kode_matkul, sesi_asisten.kode_dosen, sesi_asisten.sks_akademik, sesi_asisten.hari)
                    available_room_schedule = find_available_schedule(jadwal_ruangan, sesi_asisten.kode_ruangan, sesi_asisten.hari)

                    status = False
                    for jam in available_room_schedule:
                        rentang_waktu = list(range(jam, jam + matkul['sks_akademik'] + 1))
                        if all(r in available_room_schedule for r in rentang_waktu) and jam != 12 and not (sesi_asisten.hari == sesi_dosen.hari and jam < sesi_dosen.jam_selesai and (jam + matkul['sks_akademik']) > sesi_dosen.jam_mulai):
                            status = True
                            conflict = False
                            sesi_asisten.jam_mulai = jam
                            sesi_asisten.jam_selesai = jam + matkul['sks_akademik']
                            break
                        else:
                            status = False

                    if not status:
                        excluded_day.append(sesi_asisten.hari)
                        # print('ASISTEN pil ', suggested_hari_asisten)
                        # print('ASISTEN exc ', excluded_day)
                        # print('ASISTEN     ', [d for d in suggested_hari_asisten if d not in excluded_day])
                        # print('      ', available_room_schedule)
                        if all(d in excluded_day for d in suggested_hari_asisten):
                            excluded_day = []
                            excluded_room.append(sesi_asisten.kode_ruangan)
                            ruang_pengganti = rand_ruangan(list_ruangan=ruang_list, data_matkul=matkul, excluded_room=excluded_room)
                            if ruang_pengganti:
                                sesi_asisten.kode_ruangan = ruang_pengganti['kode']
                                sesi_asisten.kapasitas = ruang_pengganti['kapasitas']
                                sesi_asisten.tipe_kelas = ruang_pengganti['tipe_ruangan']
                            else:
                                suggested_hari_asisten = pilihan_hari_asisten
                        else:
                            sesi_asisten.hari = random.choice([d for d in suggested_hari_asisten if d not in excluded_day])

                    attempt += 1
                
                jadwal_ruangan[sesi_asisten.kode_ruangan].append({'hari': sesi_asisten.hari, 'jam_mulai': sesi_asisten.jam_mulai, 'jam_selesai': sesi_asisten.jam_selesai})
    
    # # SWITCH SCHEDULE DOSEN x ASISTEN
    # for sesi_asisten in jadwal:
    #     if sesi_asisten.kode_matkul.endswith("-AS"):
    #         sesi_dosen = next((sd for sd in jadwal if sd.kode_matkul == sesi_asisten.kode_matkul[:-3]), None)
            
    #         tipe_ruang_dosen = next((r['tipe_ruangan'] for r in ruang_list if r['kode'] == sesi_dosen.kode_ruangan), None)
    #         tipe_ruang_asisten = next((r['tipe_ruangan'] for r in ruang_list if r['kode'] == sesi_asisten.kode_ruangan), None)

    #         if tipe_ruang_dosen == tipe_ruang_asisten:
    #             if pilihan_hari_dosen.index(sesi_dosen.hari) >= pilihan_hari_asisten.index(sesi_asisten.hari):
    #                 if sesi_dosen.jam_mulai > sesi_asisten.jam_selesai:
    #                     sesi_dosen.kode_ruangan, sesi_asisten.kode_ruangan = sesi_asisten.kode_ruangan, sesi_dosen.kode_ruangan
    #                     sesi_dosen.hari, sesi_asisten.hari = sesi_asisten.hari, sesi_dosen.hari
    #                     sesi_dosen.jam_mulai, sesi_asisten.jam_mulai = sesi_asisten.jam_mulai, sesi_dosen.jam_mulai
    #                     sesi_dosen.jam_selesai, sesi_asisten.jam_selesai = sesi_asisten.jam_selesai, sesi_dosen.jam_selesai
    #                     # print(f"{'':<3}Switched {sesi_dosen.kode_matkul} <--> {sesi_asisten.kode_matkul}")
        
    return jadwal

def generate_jadwal(matakuliah_list, dosen_list, ruang_list):
    # print(f"{'':<8}{'[ GA ]':<7} Generate Jadwal")
    jadwal = []
    pilihan_hari_dosen = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]
    pilihan_hari_asisten: list[str] = copy.deepcopy(pilihan_hari_dosen)
    pilihan_hari_asisten.append("SABTU")

    jadwal_dosen = {}    # {nip: [ {hari, jam_mulai, jam_selesai}, ... ]}
    jadwal_ruangan = {}  # {kode_ruangan: [ {hari, jam_mulai, jam_selesai}, ... ]}
    beban_dosen = {} # {nip: beban_sks}

    for dosen in dosen_list:
        jadwal_dosen[dosen['nip']] = []
        beban_dosen[dosen['nip']] = 0
    for ruangan in ruang_list:
        jadwal_ruangan[ruangan['kode']] = []

    max_attempt = 10
    
    for matkul in matakuliah_list:
        if matkul.get('jumlah_kelas'):
            putaran_kelas = int(matkul.get('jumlah_kelas', 0))
        else:
            putaran_kelas = int(matkul['jumlah_mahasiswa'] or 0)

        index_kelas = 1

        dosen_pakar = [
            dosen for dosen in dosen_list
            if (dosen.get("prodi") == matkul['prodi'] or dosen['status'] == "TIDAK_TETAP") and 
                ((
                    (dosen.get('nama') or '') in (matkul.get('dosen_ajar') or []) or 
                    len(set(dosen.get('pakar') or []) & set(matkul.get('bidang') or [])) > 0
                ) if matkul.get('bidang') or matkul.get('dosen_ajar') 
                else True) and
                dosen['status'] != "TIDAK_AKTIF"
        ]

        while putaran_kelas > 0:
            excluded_dosen = []
            ruang_dosen = rand_ruangan(
                list_ruangan=ruang_list, 
                data_matkul=matkul, 
            )
            
            # GENERATE KELAS DOSEN SESUAI DENGAN JUMLAH_DOSEN (TEAM_TEACHING) OR 1
            jumlah_dosen = matkul.get('jumlah_dosen', 1)
            hitung_dosen = 1
            while hitung_dosen <= jumlah_dosen:
                # PEMILIHAN DOSEN
                dosen = rand_dosen_pakar(
                    list_dosen_pakar=dosen_pakar, 
                    dict_beban_sks_dosen=beban_dosen, 
                    excluded_dosen=excluded_dosen
                )

                if hitung_dosen == 1:
                    preferensi_hari = [hari for hari in pilihan_hari_dosen if hari not in dosen['preferensi']['hindari_hari']] if dosen.get('preferensi') and dosen['preferensi'].get('hindari_hari') else pilihan_hari_dosen
                    hari_dosen = random.choice(preferensi_hari)
                    jadwal_dosen_kosong = find_available_schedule(
                        jadwal=jadwal_dosen, 
                        kode=dosen['nip'], 
                        hari=hari_dosen
                    )

                    sukses = False
                    attempt = 0
                    excluded_day = []
                    excluded_room = []
                    while not sukses and max_attempt >= attempt:
                        jadwal_ruangan_kosong = find_available_schedule(
                            jadwal=jadwal_ruangan, 
                            kode=ruang_dosen['kode'], 
                            hari=hari_dosen
                        )

                        available_schedule = list(set(jadwal_ruangan_kosong) & set(jadwal_dosen_kosong))

                        status = False
                        for jam in available_schedule:
                            rentang_waktu = list(range(jam, jam + matkul['sks_akademik'] + 1))
                            if all(r in available_schedule for r in rentang_waktu) and jam != 12:
                                status = True
                                sukses = True
                                jam_mulai_dosen = jam
                                jam_selesai_dosen = jam + matkul['sks_akademik']
                                break
                            else:
                                status = False

                        if not status:
                            excluded_day.append(hari_dosen)
                            # print('DOSEN pil ', pilihan_hari_dosen)
                            # print('DOSEN exc ', excluded_day)
                            # print('DOSEN     ', [d for d in pilihan_hari_dosen if d not in excluded_day])
                            # print('      ', available_schedule)
                            if all(d in excluded_day for d in preferensi_hari):
                                excluded_day = []
                                excluded_room.append(ruang_dosen['kode'])
                                ruang_dosen = rand_ruangan(
                                    list_ruangan=ruang_list, 
                                    data_matkul=matkul, 
                                    excluded_room=excluded_room
                                )
                            else:
                                hari_dosen = random.choice([d for d in preferensi_hari if d not in excluded_day])

                        attempt += 1
                else:
                    conflict = False
                    for sesi_lain in jadwal_dosen[dosen['nip']]:
                        if hari_dosen == sesi_lain['hari']:
                            if jam_mulai_dosen < sesi_lain['jam_selesai'] and jam_selesai_dosen > sesi_lain['jam_mulai']:
                                conflict = True
                                break

                    attempt = 1
                    # Repair Jadwal Dosen Bentrok
                    while conflict and attempt <= max_attempt:
                        excluded_dosen.append(dosen['nip'])
                        if all(dosen["nip"] in excluded_dosen for dosen in dosen_pakar):
                            # print('dosen full')
                            hitung_dosen = jumlah_dosen
                            break
                        else:
                            dosen = rand_dosen_pakar(
                                list_dosen_pakar=dosen_pakar, 
                                dict_beban_sks_dosen=beban_dosen, 
                                excluded_dosen=excluded_dosen
                            )
                        
                        attempt += 1
                
                excluded_dosen.append(dosen["nip"])
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
                    program_studi   = matkul['prodi']
                )
                jadwal.append(sesi_dosen)

                beban_dosen[dosen['nip']] += matkul['sks_akademik']
                jadwal_dosen[dosen['nip']].append({'hari': hari_dosen, 'jam_mulai': jam_mulai_dosen, 'jam_selesai': jam_selesai_dosen})
                hitung_dosen += 1
            jadwal_ruangan[ruang_dosen['kode']].append({'hari': hari_dosen, 'jam_mulai': jam_mulai_dosen, 'jam_selesai': jam_selesai_dosen})

            # Penentuan kelas asistensi yang tidak terintegrasi dengan kelas dosen
            if matkul.get('asistensi') and not matkul.get('integrated_class'):
                # print(f"{matkul['nama']:<50} praktikum: {matkul.get('asistensi'):<10} integrated: {matkul.get('integrated_class')}")
                # print(f"kapasitas ruangan dosen {ruang_dosen['kapasitas']}; {min(40, max(40, ruang_dosen['kapasitas']))}")
                suggested_hari_asisten = pilihan_hari_asisten[pilihan_hari_dosen.index(hari_dosen):]
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
                        jadwal=jadwal_ruangan, 
                        kode=ruang_asisten['kode'], 
                        hari=hari_asisten
                    )

                    status = False
                    for jam in jadwal_ruangan_kosong:
                        rentang_waktu = list(range(jam, jam + matkul['sks_akademik'] + 1))
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
                        # print('ASISTEN pil ', suggested_hari_asisten)
                        # print('ASISTEN exc ', excluded_day)
                        # print('ASISTEN     ', [d for d in suggested_hari_asisten if d not in excluded_day])
                        # print('      ', available_room_schedule)
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
                jadwal_ruangan[ruang_asisten['kode']].append({'hari': hari_asisten, 'jam_mulai': jam_mulai_asisten, 'jam_selesai': jam_selesai_asisten})
            
            putaran_kelas -= (1 if matkul.get('jumlah_kelas') else ruang_dosen['kapasitas'])
            index_kelas += 1

    return jadwal

def generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi):
    return [generate_jadwal(matakuliah_list, dosen_list, ruang_list) for _ in range(ukuran_populasi)]

def hitung_fitness(jadwal, matakuliah_list, dosen_list, ruang_list, detail=False):
    penalti = 0
    jadwal_dosen = {}
    jadwal_ruangan = {}
    beban_dosen = {}

    for dosen in dosen_list:
        if dosen['nip'] not in jadwal_dosen: jadwal_dosen[dosen['nip']] = []
        if dosen['nip'] not in beban_dosen: beban_dosen[dosen['nip']] = 0

    for ruangan in ruang_list:
        if ruangan['kode'] not in jadwal_ruangan: jadwal_ruangan[ruangan['kode']] = []

    # COUNTER
    hitung_ruangan_bentrok = 0
    hitung_dosen_bentrok = 0
    hitung_asdos_nabrak_dosen = 0
    hitung_kelas_dosen_missing = 0
    hitung_kelas_asisten_missing = 0
    hitung_diluar_jam_kerja = 0
    hitung_solo_team = {}
    pelanggaran_preferensi = {}
    mata_kuliah_minus = {}

    detail_jadwal_matkul = {}
    detail_team = {}

    # TO BE CHECKED:
    # (15)  Jadwal Ruangan Bertabrakan                                  >> ruangan_bentrok           (DONE)
    # (15)  Jadwal Dosen Bertabrakan                                    >> dosen_bentrok             (DONE)
    # (15)  Jadwal Dosen dan Asisten Berjalan Bersamaan                 >> asdos_nabrak_dosen        (DONE)
    # (15)  Kelas Dosen atau Asisten Hilang atau Tidak Lengkap          >> kelas_gaib                (DONE)
    # (15)  Solo Team_Teaching                                          >> solo_team
    # (10)  Beban SKS Dosen melebihi 12 sks                             >> dosen_overdosis           (DONE)
    # (10)  Matkul berlangsung sebelum pukul 7 atau sesudah pukul 19    >> diluar_jam_kerja          (DONE)
    # (10)  Cek Total Kelas Bisa Cangkup Semua Mahasiswa                >> kapasitas_kelas_terbatas  (DONE)
    # (5)   Tidak Sesuai dengan permintaan / request dosen              >> melanggar_preferensi      (DONE)

    seen_course = set()
    for sesi in jadwal:
        kode_matkul = sesi.kode_matkul[:-1] if sesi.kode_dosen != "AS" else sesi.kode_matkul[:-4]
        info_matkul = next((m for m in matakuliah_list if m['kode'] == kode_matkul), None)
        info_dosen = next((d for d in dosen_list if d['nip'] == sesi.kode_dosen), None)
        
        if kode_matkul not in detail_jadwal_matkul: detail_jadwal_matkul[kode_matkul] = {'jumlah_kelas': 0, 'kapasitas_total': 0}
        if sesi.kode_matkul not in detail_team and sesi.kode_dosen != "AS": detail_team[sesi.kode_matkul] = []

        # CEK SUPAYA BENTROK RUANGAN CUMA DICEK 1x UNTUK KODE MATKUL YANG SAMA
        if sesi.kode_matkul not in seen_course:
            seen_course.add(sesi.kode_matkul)
            
            # CEK BENTROK JADWAL RUANGAN
            for sesi_lain in jadwal_ruangan[sesi.kode_ruangan]:
                if sesi.hari == sesi_lain['hari']:
                    if sesi.jam_mulai < sesi_lain['jam_selesai'] and sesi.jam_selesai > sesi_lain['jam_mulai']:
                        penalti += BOBOT_PENALTI['ruangan_bentrok']
                        hitung_ruangan_bentrok += 1
            jadwal_ruangan[sesi.kode_ruangan].append({'hari': sesi.hari, 'jam_mulai': sesi.jam_mulai, 'jam_selesai': sesi.jam_selesai})

            # CEK JAM MULAI DAN JAM SELESAI MASIH DI JAM KERJA ATAU TIDAK
            if sesi.jam_mulai < 7 or sesi.jam_selesai > 19:
                penalti += BOBOT_PENALTI['diluar_jam_kerja']
                hitung_diluar_jam_kerja += 1

            if sesi.kode_dosen != "AS":
                # HITUNG TOTAL KAPASITAS
                detail_jadwal_matkul[kode_matkul]['jumlah_kelas'] += 1
                detail_jadwal_matkul[kode_matkul]['kapasitas_total'] += sesi.kapasitas

                # CEK EKSISTENSI KELAS ASISTEN
                if info_matkul.get('asistensi') and not info_matkul.get('integrated_class'):
                    sesi_asisten = next((sa for sa in jadwal if sa.kode_matkul == sesi.kode_matkul+"-AS"), None)
                    if sesi_asisten:
                        # CEK BENTROK JADWAL DOSEN X ASISTEN NGGA BENER INI ANJENG. CEK ULANG SU
                        if sesi.hari == sesi_asisten.hari:
                            if sesi.jam_mulai < sesi_asisten.jam_selesai and sesi.jam_selesai > sesi_asisten.jam_mulai:
                                penalti += BOBOT_PENALTI['asdos_nabrak_dosen']
                                hitung_asdos_nabrak_dosen += 1
                    else:
                        penalti += BOBOT_PENALTI['kelas_gaib']
                        hitung_kelas_asisten_missing += 1

        if info_matkul.get('team_teaching') and sesi.kode_dosen != "AS":
            if info_dosen['nip'] in detail_team[sesi.kode_matkul]:
                if info_dosen['nip'] not in hitung_solo_team: hitung_solo_team[info_dosen['nip']] = 0
                hitung_solo_team[info_dosen['nip']] += 1
                penalti += BOBOT_PENALTI['solo_team']
            detail_team[sesi.kode_matkul].append(info_dosen['nip'])


        if sesi.kode_dosen != "AS":
            # CEK BENTROK JADWAL DOSEN
            for sesi_lain in jadwal_dosen[sesi.kode_dosen]:
                if sesi.hari == sesi_lain['hari']:
                    if sesi.jam_mulai < sesi_lain['jam_selesai'] and sesi.jam_selesai > sesi_lain['jam_mulai']:
                        penalti += BOBOT_PENALTI['dosen_bentrok']
                        hitung_dosen_bentrok += 1
            jadwal_dosen[sesi.kode_dosen].append({'hari': sesi.hari, 'jam_mulai': sesi.jam_mulai, 'jam_selesai': sesi.jam_selesai})

            # CEK PELANGGARAN BEBAN SKS DOSEN
            beban_dosen[sesi.kode_dosen] += sesi.sks_akademik
            if beban_dosen[sesi.kode_dosen] > 12:
                penalti += BOBOT_PENALTI['dosen_overdosis']

            # CEK PELANGGARAN PREFERENSI DOSEN
            preferensi_dosen = info_dosen.get("preferensi", None)
            if preferensi_dosen:
                hindari_hari = preferensi_dosen.get("hindari_hari", None)
                hindari_jam = preferensi_dosen.get("hindari_jam", None)
                if (hindari_hari and sesi.hari in hindari_hari) or (hindari_jam and any(jam in hindari_jam for jam in range(sesi.jam_mulai, sesi.jam_selesai + 1))):
                    if info_dosen['nip'] not in pelanggaran_preferensi: pelanggaran_preferensi[info_dosen['nip']] = []
                    pelanggaran_preferensi[info_dosen['nip']].append(sesi.hari)
                    penalti += BOBOT_PENALTI['melanggar_preferensi']
        else:
            sesi_dosen = next((sd for sd in jadwal if sd.kode_matkul == sesi.kode_matkul[:-3]), None)
            # CEK EKSISTENSI KELAS DOSEN
            if not sesi_dosen:
                penalti += BOBOT_PENALTI['kelas_gaib']
                hitung_kelas_dosen_missing += 1
                
    # CEK KEKURANGAN KAPASITAS TIAP MATKUL
    for kode_matkul, data in detail_jadwal_matkul.items():
        matkul_detail = next((matkul for matkul in matakuliah_list if matkul['kode'] == kode_matkul), None)
        if matkul_detail:
            if matkul_detail.get('jumlah_kelas') and data['jumlah_kelas'] < matkul_detail['jumlah_kelas']:
                penalti += BOBOT_PENALTI['kapasitas_kelas_terbatas']
            elif not matkul_detail.get('jumlah_kelas') and data['kapasitas_total'] < matkul_detail['jumlah_mahasiswa']:
                kekurangan_kapasitas = matkul_detail['jumlah_mahasiswa'] - data['kapasitas_total']
                penalti += (BOBOT_PENALTI['kapasitas_kelas_terbatas'] * (kekurangan_kapasitas/10))
                mata_kuliah_minus[kode_matkul] = kekurangan_kapasitas

    if detail:
        if hitung_dosen_bentrok: print(f"{'':<10}{'Bentrok Dosen':<40} : {hitung_dosen_bentrok}")
        if hitung_ruangan_bentrok: print(f"{'':<10}{'Bentrok Ruangan':<40} : {hitung_ruangan_bentrok}")
        if hitung_asdos_nabrak_dosen: print(f"{'':<10}{'Bentrok Dosen-Asdos':<40} : {hitung_asdos_nabrak_dosen}")
        if hitung_diluar_jam_kerja: print(f"{'':<10}{'Kelas Diluar Jam Kerja':<40} : {hitung_diluar_jam_kerja}")
        if hitung_kelas_dosen_missing: print(f"{'':<10}{'Kelas Dosen Missing':<40} : {hitung_kelas_dosen_missing}")
        if hitung_kelas_asisten_missing: print(f"{'':<10}{'Kelas Asisten Missing':<40} : {hitung_kelas_asisten_missing}")
        if mata_kuliah_minus: print(f"{'':<10}{'Kapasitas kelas kurang x':<40} : {mata_kuliah_minus}")
        hitung_solo_team = {k: v for k, v in hitung_solo_team.items() if v}
        pelanggaran_preferensi = {k: v for k, v in pelanggaran_preferensi.items() if v}
        print(f"{'':<41}solo team : {hitung_solo_team}")
        print(f"{'':<28}pelanggaran preferensi : {pelanggaran_preferensi}")

    # print(f"{'final fitness':<50} : {max(0, 1000 - penalti)}")
    # return max(0, 1000 - penalti)
    return 1000-penalti

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
    return random.choice(populasi)  # fallback, jika tidak ketemu

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

def mutasi(individu, dosen_list, matakuliah_list, ruang_list, peluang_mutasi=0.1):
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
    pilihan_waktu = list(range(7, 20))

    for sesi in individu:
        if random.random() < peluang_mutasi:
            # Randomly mutate hari, jam, atau ruangan
            attr = random.choice(['hari', 'jam', 'ruang'])

            if attr == 'hari':
                sesi.hari = random.choice(pilihan_hari_dosen) if sesi.kode_dosen != "AS" else random.choice(pilihan_hari_asisten)
            elif attr == 'jam':
                jam_mulai = random.choice(pilihan_waktu)
                sesi.jam_mulai = (
                    jam_mulai 
                    if jam_mulai + sesi.sks_akademik <= max(pilihan_waktu) 
                    else max(pilihan_waktu) - sesi.sks_akademik)
                sesi.jam_selesai = sesi.jam_mulai + sesi.sks_akademik
            elif attr == 'ruang':
                kode_matkul = sesi.kode_matkul[:-1] if sesi.kode_dosen != "AS" else sesi.kode_matkul[:-4]
                matkul = next((matkul for matkul in matakuliah_list if matkul['kode'] == kode_matkul), None)
                if sesi.kode_dosen != "AS":
                    calon_ruang_pengganti = [
                        r for r in ruang_list if 
                            (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot']) and
                            r['kapasitas'] >= 35 and
                            (
                                r['tipe_ruangan'] == sesi.tipe_kelas or 
                                (r['tipe_ruangan'] == "RAPAT" if not matkul.get('asistensi') else False)
                            )
                    ]
                else:
                    calon_ruang_pengganti = [
                        r for r in ruang_list if 
                            (matkul['prodi'] in r['plot'] or 'GENERAL' in r['plot']) and
                            r['kapasitas'] >= sesi.kapasitas and
                            r['tipe_ruangan'] == matkul['tipe_kelas_asistensi']
                    ]
                bobot_calon_ruang_pengganti = [
                    (len(set(r['plot']) & set(matkul.get('bidang') or []))*10 or 1)
                    for r in calon_ruang_pengganti
                ]
                ruang_pengganti = random.choices(
                    population=calon_ruang_pengganti, 
                    weights=bobot_calon_ruang_pengganti, 
                    k=1)[0]
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
    print(f"{'':<8}{'[ GA ]':<7} Genetic Algorithm")
    if not matakuliah_list: print('[ KOSONG ] list mata kuliah')
    if not dosen_list: print('[ KOSONG ] list dosen')
    if not ruang_list: print('[ KOSONG ] list ruang')

    try:
        populasi = generate_populasi(matakuliah_list, dosen_list, ruang_list, ukuran_populasi)
        populasi = [repair_jadwal(j, matakuliah_list, dosen_list, ruang_list) for j in populasi]

        best_fitness_global = float('-inf')
        best_individual_global = None

        for gen in range(jumlah_generasi):
            fitness_scores = [hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) for individu in populasi]
            next_gen = []

            # Generate anak baru
            while len(next_gen) < ukuran_populasi:
                parent1 = roulette_selection(populasi, fitness_scores)
                parent2 = roulette_selection(populasi, fitness_scores)

                child1, child2 = crossover(parent1, parent2)

                child1 = mutasi(child1, dosen_list, matakuliah_list, ruang_list, peluang_mutasi)
                child2 = mutasi(child2, dosen_list, matakuliah_list, ruang_list, peluang_mutasi)

                child1 = repair_jadwal(child1, matakuliah_list, dosen_list, ruang_list)
                child2 = repair_jadwal(child2, matakuliah_list, dosen_list, ruang_list)

                next_gen.append(child1)
                if len(next_gen) < ukuran_populasi:
                    next_gen.append(child2)
                
            populasi = next_gen

            fitness_scores = [hitung_fitness(individu, matakuliah_list, dosen_list, ruang_list) for individu in populasi]
            gen_best_fitness = max(fitness_scores)
            gen_best_individual = populasi[fitness_scores.index(gen_best_fitness)]
            
            if gen > 15 and gen_best_fitness == 1000:
                print(f"{'[ Highest Best ]':<15} {gen} 1000")
                best_fitness_global = gen_best_fitness
                best_individual_global = copy.deepcopy(gen_best_individual)
            elif gen > 15 and gen_best_fitness > best_fitness_global:
                print(f"{'[ Update  Best ]':<15} {gen} {gen_best_fitness}")
                best_fitness_global = gen_best_fitness
                best_individual_global = copy.deepcopy(gen_best_individual)

            if int(gen) % 20 == 0 or int(gen) == (jumlah_generasi - 1):
                print(f"[Gen {gen}] [({len(populasi)} population)]")
                print(f"{f'[Gen {gen}]':<10}Worst: {min(fitness_scores):<5}Best: {max(fitness_scores):<5}BEST ALLTIME: {best_fitness_global}")
                if best_individual_global:
                    print('entry3')
                    hitung_fitness(gen_best_individual, matakuliah_list, dosen_list, ruang_list, True)
                    print(f"{'':<5}Missing: {find_missing_course(best_individual_global, matakuliah_list)}\n") if find_missing_course(best_individual_global, matakuliah_list) else print("\n")

            if best_fitness_global == 1000:
                break
    except Exception as e:
        print(f"{'[ GA ]':<25} Error: {e}")
        return { 'status': False, 'message': e }
    
    return { 'status': True, 'data': convertOutputToDict(best_individual_global) }