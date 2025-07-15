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

    data_dosen = dosen.get_dosen()
    data_matkul = matkul.get_matkul()

    if downloadBy == "jadwal_kuliah":
        excel = export_jadwal_to_excel(jadwal, data_matkul, data_dosen)
    elif downloadBy == "jadwal_ruangan":
        excel = export_ruangan_to_excel(jadwal, data_matkul, data_dosen)
    return send_file(excel, as_attachment=True, download_name=f"{filename}.xls")

def get_current_datetime():
    # return datetime.now().strftime('%d-%m-%Y %I-%M-%S')  # 12-hour format
    return datetime.now().strftime('%d-%m-%Y %H-%M-%S')  # 24-hour format

def export_jadwal_to_excel(jadwal_list, matakuliah_list, dosen_list):
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

    # 🔹 Group berdasarkan program_studi
    jadwal_prodi = defaultdict(list)
    for jadwal in jadwal_list:
        jadwal_prodi[jadwal['program_studi']].append(jadwal)

    # Format header
    format_title = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'bold': True
    })
    format_header = workbook.add_format({
        'align': 'center',
        'bg_color': '#99CCFF',
        'valign': 'vcenter',
        'bold': True
    })
    format_as = workbook.add_format({
        'align': 'center',
        'bg_color': '#b9ebc6',
    })
    format_warning = workbook.add_format({
        'bg_color': "#ffd438"
    })
    format_error = workbook.add_format({
        'bg_color': '#ff0000'
    })

    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    # Sheet 1 - Beban SKS Dosen
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    worksheet = workbook.add_worksheet("BEBAN SKS DOSEN")
    object_jadwal = [JadwalKuliah(**dict_jadwal) for dict_jadwal in jadwal_list]
    beban_dosen = ga.hitung_beban_sks_dosen(jadwal=object_jadwal, dosen_list=dosen_list, matakuliah_list=matakuliah_list)
    # Tulis data beban dosen
    worksheet.merge_range("A1:C1", "Dosen Tetap", format_title)
    worksheet.merge_range("E1:G1", "Dosen Tidak Tetap", format_title)

    row_idx = 1
    worksheet.set_column("A:A", 15)
    worksheet.set_column("B:B", 50)
    worksheet.set_column("C:C", 10)
    worksheet.write(row_idx, 0, "NIP", format_header)
    worksheet.write(row_idx, 1, "Nama", format_header)
    worksheet.write(row_idx, 2, "Beban SKS", format_header)

    worksheet.set_column("E:E", 15)
    worksheet.set_column("F:F", 50)
    worksheet.set_column("G:G", 10)
    worksheet.write(row_idx, 4, "NIP", format_header)
    worksheet.write(row_idx, 5, "Nama", format_header)
    worksheet.write(row_idx, 6, "Beban SKS", format_header)
    
    row_idx += 1
    row_tetap, row_tidak_tetap = row_idx, row_idx
    for nip, sks in dict(sorted(beban_dosen.items())).items():
        data_dosen = next((d for d in dosen_list if d['nip'] == nip), None)
        if data_dosen["status"] == "TETAP":
            initial_col = 0
            row_idx = row_tetap
        elif data_dosen["status"] == "TIDAK_TETAP":
            initial_col = 4
            row_idx = row_tidak_tetap

        worksheet.write(row_idx, initial_col, nip, format_warning if sks == 0 else None)
        worksheet.write(row_idx, initial_col+1, data_dosen["nama"], format_warning if sks == 0 else None)
        worksheet.write(row_idx, initial_col+2, sks, format_warning if sks == 0 else None)

        if data_dosen["status"] == "TETAP":
            row_tetap += 1
        elif data_dosen["status"] == "TIDAK_TETAP":
            row_tidak_tetap += 1

    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    # Sheet Jadwal Mata Kuliah per Program Studi
    # ===== ===== ===== ===== ===== ===== ===== ===== ===== =====
    for program_studi in sorted(jadwal_prodi.keys()):
        sheet_name = program_studi[:31]  # Sheet name max 31 chars
        worksheet = workbook.add_worksheet(sheet_name)

        row_idx = 0
        col_widths = [len(h) for h in jadwal_list]

        # Tulis header kolom
        for col_idx, header in enumerate(fixed_headers):
            worksheet.write(row_idx, col_idx, header.replace('_', ' '), format_header)
        row_idx += 1

        # Control Area
        control_solo_teaching = {}
        old_kode_dosen, old_nama_dosen = None, None

        # Sort dan tulis data
        # sorted_group = sorted(grojadwal_prodiuped[program_studi], key=lambda x: (x.kode_ruangan, x.hari, x.jam_mulai))
        sorted_group = sorted(jadwal_prodi[program_studi], key=lambda x: x['kode_matkul'])
        for jadwal in sorted_group:
            for col_idx, attr in enumerate(fixed_headers):
                value = None
                status = True
                if attr == "nama_matkul":
                    kode_matkul = jadwal['kode_matkul']
                    data_matkul = next((m for m in matakuliah_list if m['kode'] == kode_matkul[:-1] or m['kode'] == kode_matkul[:-4]), {})
                    value = data_matkul.get("nama")
                elif attr == "nama_dosen":
                    kode_dosen = jadwal['kode_dosen']
                    data_dosen = next((d for d in dosen_list if d['nip'] == kode_dosen), {})
                    value = data_dosen.get("nama") if kode_dosen != "AS" else "ASISTEN"

                    if data_matkul.get("team_teaching"):
                        if kode_matkul not in control_solo_teaching: control_solo_teaching[kode_matkul] = []
                        if kode_dosen in control_solo_teaching[kode_matkul]: status = False
                        else: control_solo_teaching[kode_matkul].append(kode_dosen)

                        if not status: worksheet.write(row_idx - 1, col_idx, old_nama_dosen, format_error)
                elif attr == "kapasitas":
                    value = jadwal['kode_matkul']
                    if value[-2:] == "AS":
                        kapasitas_dosen = next((sesi['kapasitas'] for sesi in jadwal_list if sesi['kode_matkul'] == value[:-3]), None)
                        value = kapasitas_dosen
                    else:
                        value = jadwal[attr]
                else:
                    value = jadwal[attr]

                if (
                    jadwal["kode_ruangan"] != "ONLINE" and
                    ((attr == "jam_mulai" and int(value) < 7) or 
                    (attr == "jam_selesai" and int(value) > 19) or 
                    not status)
                ):
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

        # # Data beban dosen
        # beban_dosen = {}
        # for sesi in sorted_group:
        #     if sesi['kode_dosen'] != "AS":
        #         if sesi['kode_dosen'] not in beban_dosen: beban_dosen[sesi['kode_dosen']] = 0
        #         beban_dosen[sesi['kode_dosen']] += sesi['sks_akademik']
        # # Tulis data beban dosen
        # start_col = len(fixed_headers) + 2
        # row_idx = 0
        # worksheet.write(row_idx, start_col, "NIP", format_header)
        # worksheet.write(row_idx, start_col + 1, "Nama", format_header)
        # worksheet.write(row_idx, start_col + 2, "Beban SKS", format_header)
        # row_idx += 1
        
        # for nip, sks in dict(sorted(beban_dosen.items())).items():
        #     nama_dosen = next((d['nama'] for d in dosen_list if d['nip'] == nip), None)
        #     worksheet.write(row_idx, start_col, nip)
        #     worksheet.write(row_idx, start_col + 1, nama_dosen)
        #     worksheet.write(row_idx, start_col + 2, sks)
        #     row_idx += 1

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
            worksheet.merge_range(
                col + start_row + ":" + col + end_row, 
                value, 
                format_data
            )

    # Simpan workbook
    workbook.close()
    output.seek(0)
    return output