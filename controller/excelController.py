from flask import Blueprint, request, send_file
from flask_login import login_required
from io import BytesIO
from datetime import datetime
from collections import defaultdict
import xlsxwriter
import random

from dao.admin.generateJadwalDao import generateJadwalDao
from dao.kaprodi.dataMataKuliahDao import dataMataKuliahDao
from dao.kaprodi.dataDosenDao import dataDosenDao
from dao import genetic_algorithm as ga
from dao.genetic_algorithm import JadwalKuliah
export = Blueprint('export', __name__)
dao = generateJadwalDao()
matkul = dataMataKuliahDao()
dosen = dataDosenDao()

@export.route("/export/export_to_excel", methods=['POST'])
@login_required
def export_to_excel():
    print(f"{'[ CONTROLLER ]':<25} Download Excel")
    req = request.get_json('data')
    filename = req['filename']
    downloadBy = req['downloadBy']
    data_jadwal = dao.get_jadwal()
    jadwal = data_jadwal['jadwal']
    report_fitness = data_jadwal["report"]
    bkd = data_jadwal["bkd"]

    data_dosen = dosen.get_dosen()
    data_matkul = matkul.get_matkul()

    if downloadBy == "jadwal_kuliah":
        excel = export_jadwal_to_excel(jadwal, data_matkul, data_dosen, report_fitness, bkd)
    elif downloadBy == "jadwal_ruangan":
        excel = export_ruangan_to_excel(jadwal, data_matkul, data_dosen)
    return send_file(excel, as_attachment=True, download_name=f"{filename}.xls")

def get_current_datetime():
    # return datetime.now().strftime('%d-%m-%Y %I-%M-%S')  # 12-hour format
    return datetime.now().strftime('%d-%m-%Y %H-%M-%S')  # 24-hour format

def export_jadwal_to_excel(jadwal_list, matakuliah_list, dosen_list, report_fitness, bkd):
    print(f"{'[ CONTROLLER ]':<25} Building File Excel By Jadwal")
    output = BytesIO()

    fixed_headers = [
        'kode_matkul', 'nama_matkul',
        'kode_dosen', 'nama_dosen', 'sks_akademik', 
        'kode_ruangan', 'kapasitas', 
        'hari', 'jam_mulai', 'jam_selesai',
        'tipe_kelas'
    ]

    workbook = xlsxwriter.Workbook(output)

    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    # Format Used
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    format_bkd_prodi = workbook.add_format({
        'bg_color': '#99CCFF',
        'align': 'center',
        'valign': 'top',
        'text_wrap': True,
        'border': 1
    })
    format_bkd_sks = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True,
        'top': 1
    })
    format_header_with_top_bottom = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True,
        'top': 1,
        'bottom': 1
    })
    format_header_with_top = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True,
        'top': 1,
    })
    format_header = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True,
    })
    format_header_with_bottom = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True,
        'bottom': 1,
    })
    format_bottom_line = workbook.add_format({
        'bottom': 1,
    })
    format_as = workbook.add_format({
        'align': 'center',
        'bg_color': '#b9ebc6',
    })
    format_info = workbook.add_format({
        'bg_color': "#38fff5"
    })
    format_success = workbook.add_format({
        'bg_color': "#53ff38"
    })
    format_warning = workbook.add_format({
        'bg_color': "#ffd438"
    })
    format_warning_with_bottom = workbook.add_format({
        'bg_color': "#ffd438",
        'bottom': 1
    })
    format_beban = workbook.add_format({
        'bg_color': "#c4a01c"
    })
    format_beban_with_bottom = workbook.add_format({
        'bg_color': "#c4a01c",
        'bottom': 1
    })
    format_error = workbook.add_format({
        'bg_color': '#ff0000'
    })

    # Data Source
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    object_jadwal = [JadwalKuliah(**dict_jadwal) for dict_jadwal in jadwal_list]
    # Grouping jadwal by prodi
    jadwal_prodi = defaultdict(list)
    for jadwal in jadwal_list:
        jadwal_prodi[jadwal['program_studi']].append(jadwal)
    # Grouping dosen by prodi
    dosen_by_prodi = defaultdict(list)
    for dosen in dosen_list:
        prodi = dosen.get("prodi") or "TIDAK_TETAP"
        dosen_by_prodi[prodi].append(dosen["nip"])
    # Grouping dosen by NIP
    dosen_by_nip = {d['nip']: d for d in dosen_list}
    # Grouping matkul by kode
    matkul_by_kode = {m['kode']: m for m in matakuliah_list}
    # beban_dosen = ga.hitung_beban_sks_dosen_all(
    #     jadwal=object_jadwal, 
    #     dosen_list=dosen_list, 
    #     matkul_by_kode=matkul_by_kode
    # ) # NOTE: PERHITUNGAN SKS DARI LUAR GA SALAH
    if report_fitness["pelanggaran_preferensi"]:
        report_fitness["pelanggaran_preferensi"] = {dt["kode_matkul"]: dt for dt in report_fitness["pelanggaran_preferensi"]}
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

    # # Sheet 1 - Beban SKS Dosen # NOTE: PERHITUNGAN SKS DARI LUAR GA SALAH
    # # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    # worksheet = workbook.add_worksheet("BEBAN SKS")

    # # Set Ukuran Kolom
    # worksheet.set_column("A:A", 15)
    # worksheet.set_column("B:B", 50)
    # worksheet.set_column("C:C", 10)
    # worksheet.set_column("E:E", 15)
    # worksheet.set_column("F:F", 50)
    # worksheet.set_column("G:G", 10)
    
    # row = 1
    # for prodi, data_dosen in dosen_by_prodi.items():
    #     if prodi == "TIDAK_TETAP":
    #         row, col = 1, 4
    #         # worksheet.merge_range(f"E{row}:G{row}", "Dosen Tidak Tetap", format_header_with_top)
    #     else:
    #         col = 0
    #         # worksheet.merge_range(f"A{row}:C{row}", f"Dosen Tetap - {prodi}", format_header_with_top)
    #     worksheet.write(row, col, "NIP", format_header_with_bottom)
    #     worksheet.write(row, col + 1, "Nama", format_header_with_bottom)
    #     worksheet.write(row, col + 2, "Beban SKS", format_header_with_bottom)

    #     last_row = row + len(data_dosen)
    #     for nip in data_dosen:
    #         row += 1
    #         if beban_dosen[nip] > 20:
    #             format = format_error
    #         elif beban_dosen[nip] > 12:
    #             format = format_beban
    #         elif beban_dosen[nip] > 12 and row == last_row:
    #             format = format_beban
    #         elif beban_dosen[nip] == 0 and row == last_row:
    #             format = format_warning_with_bottom
    #         elif beban_dosen[nip] == 0:
    #             format = format_warning
    #         elif row == last_row:
    #             format = format_bottom_line
    #         else:
    #             format = None
    #         worksheet.write(row, col, nip, format)
    #         worksheet.write(row, col+1, dosen_by_nip[nip]["nama"], format)
    #         worksheet.write(row, col+2, beban_dosen[nip], format)

    #     if prodi != "TIDAK_TETAP":
    #         row += 3 # 1 buat space, 1 buat merge_range
    # # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

    # Sheet 2 - BKD
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    worksheet = workbook.add_worksheet("BKD")

    # Set Ukuran Kolom
    worksheet.set_column("A:A", 15)
    worksheet.set_column("B:B", 10)
    worksheet.set_column("C:C", 50)
    worksheet.set_column("D:D", 50)
    worksheet.set_column("E:E", 5)
    worksheet.set_column("F:F", 5)
    worksheet.set_column("G:G", 5)
    
    row, col = 0, 0
    # HEADER
    worksheet.write(row, col    , "Program Studi"   , format_header_with_bottom)
    worksheet.write(row, col + 1, "NIP"             , format_header_with_bottom)
    worksheet.write(row, col + 2, "Nama"            , format_header_with_bottom)
    worksheet.write(row, col + 3, "Matakuliah"      , format_header_with_bottom)
    worksheet.write(row, col + 4, "SKS"             , format_header_with_bottom)
    worksheet.write(row, col + 5, "Jml Kelas"       , format_header_with_bottom)
    worksheet.write(row, col + 6, "SBS"             , format_header_with_bottom)
    worksheet.write(row, col + 7, "Beban Ajar"      , format_header_with_bottom)

    row += 1
    for prodi, list_nip in dosen_by_prodi.items():
        init_row_prodi = row
        for nip in list_nip:
            init_row_sks = row
            dosen = dosen_by_nip.get(nip, {})
            worksheet.write(row, col + 1, nip)
            worksheet.write(row, col + 2, dosen.get("nama", "-"))

            calc_bkd = bkd.get(nip)
            if not calc_bkd or not calc_bkd["matakuliah"]:
                row += 1
                worksheet.set_row(row - 1, None, format_bottom_line)
                worksheet.write(init_row_sks, col + 3, "-")
                worksheet.write(init_row_sks, col + 4, "-")
                worksheet.write(init_row_sks, col + 5, "-")
                worksheet.write(init_row_sks, col + 6, "-")
                worksheet.write(init_row_sks, col + 7, 0, format_bkd_sks)
                continue
            
            calc_sks = 0
            for kode, info_bkd in calc_bkd["matakuliah"].items():
                nama_matkul = matkul_by_kode.get(kode[:5], {}).get("nama", "-")
                worksheet.write(row, col + 3, nama_matkul + " (team)" if kode[5:] else nama_matkul)
                worksheet.write(row, col + 4, info_bkd["sks"])
                worksheet.write(row, col + 5, info_bkd["jml_kelas"])
                if dosen.get("status") == "TETAP":
                    sbs = ((info_bkd["sks"] / 3) * ((2 * info_bkd["jml_kelas"]) + 1))
                elif dosen.get("status") == "TIDAK_TETAP":
                    sbs =  info_bkd["sks"] * info_bkd["jml_kelas"]

                worksheet.write(row, col + 6, sbs)
                calc_sks += sbs
                row += 1

            worksheet.set_row(row - 1, None, format_bottom_line)

            if init_row_sks == row - 1:
                worksheet.write(init_row_sks, col + 7, calc_sks, format_bkd_sks)
            else:
                worksheet.merge_range(f"H{init_row_sks + 1}:H{row}", calc_sks, format_bkd_sks)
            
        if init_row_prodi < row:
            worksheet.merge_range(f"A{init_row_prodi + 1}:A{row}", prodi, format_bkd_prodi)
        else:
            worksheet.write(init_row_prodi, col, prodi, format_bkd_prodi)

    # # Ga Fungsi
    # worksheet.conditional_format(
    #     # 2, 3, row - 1, 3,  # baris dari 2 s.d. row-1, kolom ke-3 (D)
    #     "D2:D111",
    #     {
    #         'type': 'text',
    #         'criteria': 'containing',
    #         'value': '(team)',
    #         'format': format_info
    #     }
    # )

    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

    # Sheet etc - Jadwal Mata Kuliah per Program Studi
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    for program_studi in sorted(jadwal_prodi.keys()):
        sheet_name = program_studi[:31]  # Sheet name max 31 chars
        worksheet = workbook.add_worksheet(sheet_name)

        row_idx = 0
        col_widths = [len(h) for h in jadwal_list]

        # Tulis header kolom
        for col_idx, header in enumerate(fixed_headers):
            worksheet.write(row_idx, col_idx, header.replace('_', ' '), format_header_with_top_bottom)
        row_idx += 1

        # Control Area
        control_solo_teaching = {}
        old_kode_dosen, old_nama_dosen = None, None

        # Sort dan tulis data
        # sorted_group = sorted(grojadwal_prodiuped[program_studi], key=lambda x: (x.kode_ruangan, x.hari, x.jam_mulai))
        sorted_group = sorted(jadwal_prodi[program_studi], key=lambda x: x['kode_matkul'])
        for jadwal in sorted_group:
            kode_matkul = jadwal['kode_matkul']
            data_matkul = matkul_by_kode.get(kode_matkul[:5], {})
            kode_dosen = jadwal['kode_dosen']
            data_dosen = dosen_by_nip.get(kode_dosen, {})

            for col_idx, attr in enumerate(fixed_headers):
                value = None
                status = True
                if attr == "nama_matkul":
                    value = data_matkul.get("nama")
                elif attr == "nama_dosen":
                    value = data_dosen.get("nama") if kode_dosen != "AS" else "ASISTEN"

                    if data_matkul.get("team_teaching"):
                        if kode_matkul not in control_solo_teaching: control_solo_teaching[kode_matkul] = []
                        if kode_dosen in control_solo_teaching[kode_matkul]: status = False
                        else: control_solo_teaching[kode_matkul].append(kode_dosen)

                        if not status: 
                            worksheet.write(row_idx - 1, col_idx, old_nama_dosen, format_error)
                elif attr == "kapasitas":
                    if kode_dosen == "AS":
                        kapasitas_dosen = next((sesi['kapasitas'] for sesi in jadwal_list if f"{sesi['kode_matkul']}-AS" == kode_matkul), None)
                        value = kapasitas_dosen
                    else:
                        value = jadwal[attr]
                else:
                    value = jadwal[attr] if attr in jadwal else ""

                if (
                    jadwal["kode_ruangan"] != "ONLINE" and
                    ((attr == "jam_mulai" and int(value) < 7) or 
                    (attr == "jam_selesai" and int(value) > 19) or 
                    not status)
                ):
                    # DILUAR JAM KERJA + NOT ONLINE
                    worksheet.write(row_idx, col_idx, value, format_error)
                elif jadwal["kode_matkul"] in report_fitness["pelanggaran_preferensi"] and \
                    jadwal["kode_dosen"] == report_fitness["pelanggaran_preferensi"][jadwal["kode_matkul"]]["kode_dosen"] and \
                    attr in ["hari", "jam_mulai", "jam_selesai"]:
                    # PELANGGARAN PREFERENSI
                    worksheet.write(row_idx, col_idx, value, format_error)
                elif attr == "kode_ruangan" and kode_matkul in report_fitness["list_ruang_bentrok"]:
                    # RUANG BENTROK
                    worksheet.write(row_idx, col_idx, value, format_error)
                elif (attr == "kode_dosen" or attr == "nama_dosen") and kode_matkul in report_fitness["list_dosen_bentrok"]:
                    # DOSEN BENTROK
                    worksheet.write(row_idx, col_idx, value, format_error)
                else:
                    worksheet.write(row_idx, col_idx, value, format_as if jadwal['kode_dosen'] == "AS" else None)

                # Control
                if attr == "nama_dosen":
                    old_kode_dosen = kode_dosen
                    old_nama_dosen = data_dosen.get("nama") if kode_dosen != "AS" else "ASISTEN"

                val_len = len(str(value))
                if val_len > col_widths[col_idx]:
                    col_widths[col_idx] = val_len
            row_idx += 1

        # Set lebar kolom
        for col_idx, width in enumerate(col_widths):
            worksheet.set_column(col_idx, col_idx, width + 2)
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====

    # Simpan workbook
    workbook.close()
    output.seek(0)
    return output

def export_ruangan_to_excel(jadwal_list, matakuliah_list, dosen_list):
    print(f"{'[ CONTROLLER ]':<25} Building File Excel By Ruangan")
    output = BytesIO()

    hari = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
    mapping_hari = {h: i for i, h in enumerate(hari, start=2)}
    jam = list(range(7, 19+1))
    tampilan_jam = [f"{j:02d}:00" for j in jam]
    mapping_jam = {j: i for i, j in enumerate(jam, start=2)}

    workbook = xlsxwriter.Workbook(output)

    # 🔹 Group berdasarkan program_studi
    grouped = defaultdict(list)
    for jadwal in jadwal_list:
        if jadwal["tipe_kelas"] == "ONLINE": continue
        grouped[jadwal['kode_ruangan']].append(jadwal)

    # Format header
    format_header = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True
    })

    # Loop setiap group dan tulis ke sheet terpisah
    for ruangan in sorted(grouped.keys()):
        sheet_name = ruangan[:31]  # Sheet name max 31 chars
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.set_default_row(30)
        worksheet.hide_gridlines()

        row_idx = 0

        # Tulis header kolom
        for col_idx, value in enumerate(hari):
            worksheet.write(0, col_idx + 1, value, format_header)
            worksheet.set_column(col_idx + 1, col_idx + 1, 15) # set lebar column
        for row_idx in range(len(tampilan_jam) - 1):  # hindari akses indeks terakhir + 1
            waktu_mulai = tampilan_jam[row_idx]
            waktu_selesai = tampilan_jam[row_idx + 1]
            worksheet.write(row_idx + 1, 0, f"{waktu_mulai}-{waktu_selesai}", format_header)
            worksheet.set_column(0, 0, 15) # set lebar column
        row_idx += 1

        # Sort dan tulis data
        merged_ranges = set()
        sorted_group = sorted(grouped[ruangan], key=lambda x: (x['tipe_kelas'], x['kode_ruangan'], x['hari'], x['jam_mulai']))
        for jadwal in sorted_group:
            format_data = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'bg_color': random.choice(['#fce9b3', '#b5fcb3', '#fadcb9', '#b9e3fa', '#b9e3fa', '#fab9df', '#b9fae6']),
            })

            col = chr(64 + mapping_hari[jadwal['hari']])
            start_row = str(mapping_jam[jadwal['jam_mulai']])
            end_row = str(mapping_jam[jadwal['jam_selesai'] - 1])

            kode_matkul = jadwal['kode_matkul'][:-1] if jadwal['kode_dosen'] != "AS" else jadwal['kode_matkul'][:-4]
            index = jadwal['kode_matkul'][-1:] if jadwal['kode_dosen'] != "AS" else jadwal['kode_matkul'][-4:-3]
            nama_matkul = next((m['nama'] for m in matakuliah_list if m['kode'] == kode_matkul), '')
            nama_dosen = next((d['nama'] for d in dosen_list if d['nip'] == jadwal['kode_dosen']), '') if jadwal['kode_dosen'] != "AS" else "ASISTEN"
            
            full = f"{nama_matkul} {index} - {nama_dosen}".split(' ')
            full = [value.capitalize() for value in full]
            value = ''
            for text in full:
                value += (" " + text)
            cell_range = col + start_row + ":" + col + end_row
            if cell_range not in merged_ranges:
                worksheet.merge_range(
                    cell_range, 
                    value, 
                    format_data
                )
                merged_ranges.add(cell_range)

    # Simpan workbook
    workbook.close()
    output.seek(0)
    return output