from flask import render_template, Blueprint, request, jsonify, session, abort
from dao.generateJadwalDao import generateJadwalDao
from dao import genetic_algorithm as ga
from dao.genetic_algorithm import JadwalKuliah
from flask_login import login_required
from global_func import CustomError

generateJadwal = Blueprint('generateJadwal', __name__)
dao = generateJadwalDao()

@generateJadwal.route("/generate_jadwal")
@login_required
def generateJadwal_index():
    print(f"{'[ RENDER ]':<25} Generate Jadwal (Role: {session['user']['role']})")
    if session['user']['role'] == 'ADMIN':
        jadwal = dao.get_jadwal()
        jadwal = True if jadwal and jadwal.get('jadwal') else False
        
        return render_template(
            '/admin/generate_jadwal/index.html', 
            menu = 'Generate Jadwal', 
            title = 'Generate Jadwal', 
            semester_ajaran_depan = session['academic_details']['semester_depan'] + "_" + session['academic_details']['tahun_ajaran_berikutnya'].replace("/", "-"),
            jadwal = jadwal
        )
    elif session["user"]["role"] == "KEPALA PROGRAM STUDI":
        jadwal = dao.get_jadwal()
        jadwal = True if jadwal and jadwal.get('jadwal') else False
        
        return render_template(
            '/kaprodi/generate_jadwal/index.html', 
            menu = 'Generate Jadwal - Dosen', 
            title = 'Generate Jadwal - Dosen', 
            semester_ajaran_depan = session['academic_details']['semester_depan'] + "_" + session['academic_details']['tahun_ajaran_berikutnya'].replace("/", "-"),
            isExist = dao.prodi_isGenerated()
        )
    else:
        return abort(403)
    
@generateJadwal.route("/generate_jadwal/is_prodi_generated", methods=['GET'])
@login_required
def is_prodi_generated():
    print(f"{'[ CONTROLLER ]':<25} is Prodi Generated")
    isCreated = dao.prodi_isGenerated()
    return jsonify({"status": isCreated})
        
@generateJadwal.route("/generate_jadwal/generate", methods=['GET'])
@login_required
def generate_jadwal():
    print(f"{'[ CONTROLLER ]':<25} Generate Jadwal")

    try:
        if session['user']['role'] not in ["ADMIN", "KEPALA PROGRAM STUDI"]:
            raise CustomError({ 'message': 'Anda tidak berhak generate jadwal!\nSilahkan hubungi Admin! '})
        
        user_role = session["user"]["role"]
        param = request.args.to_dict()
        regenerate = param['regenerate'] == 'true'
        
        if user_role == "ADMIN":
            jadwal = dao.get_jadwal()
            if jadwal and jadwal.get('jadwal') and not regenerate:
                return jsonify({ 'status': False, 'reason': 'exist'})
        elif user_role == "KEPALA PROGRAM STUDI":
            jadwal = dao.prodi_isGenerated()
            if jadwal and not regenerate:
                return jsonify({ 'status': False, 'reason': 'exist'})

        data_dosen = dao.get_dosen()
        data_matkul = dao.get_open_matkul()
        if user_role == "ADMIN":
            data_ruang = dao.get_kelas()
        elif user_role == "KEPALA PROGRAM STUDI":
            prodi = session["user"]["prodi"]
            data_dosen = [d for d in data_dosen if d.get("prodi") == prodi or d["status"] == "TIDAK_TETAP"]
            data_matkul = [m for m in data_matkul if m["prodi"] == prodi]

        attempt = 1
        while attempt <= 3:
            # best_schedule = ga.genetic_algorithm(
            #     data_matkul, data_dosen, data_ruang, 
            #     ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.05
            # )
            if user_role == "ADMIN":
                best_schedule = ga.genetic_algorithm(
                    data_matkul, data_dosen, data_ruang, 
                    ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.05
                )
            elif user_role == "KEPALA PROGRAM STUDI":
                best_schedule = ga.genetic_algorithm(
                    data_matkul, data_dosen, 
                    ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.05
                )
            if best_schedule and best_schedule.get('status') == True:
                break
            attempt += 1

        if best_schedule and best_schedule.get('status') == False:
            raise CustomError({ 'message': best_schedule.get('message') })
        
        dao.upload_jadwal(best_schedule['data'], best_schedule["score"], best_schedule["bkd"])
    except CustomError as e:
        return jsonify({ 'status': False, 'message': f"{e.error_dict.get('message')}" })
    except Exception as e:
        print(f"{'[ CONTRO ERROR ]':<25} Error: {e}")
        return jsonify({ 'status': False, 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

    return jsonify({ 'status': True, 'score': best_schedule['score'] })

# @generateJadwal.route("/generate_jadwal/upload_jadwal", methods=['POST'])
# @login_required
# def upload_jadwal():
#     print(f"{'[ CONTROLLER ]':<25} Upload Jadwal")
#     if session['user']['role'] == "ADMIN":
#         req = request.get_json('data')
#         data = dao.upload_jadwal(req['jadwal'])

#     return jsonify( data )

@generateJadwal.route("/generate_jadwal/evaluate_jadwal", methods=["GET"])
@login_required
def evaluate_jadwal():
    print(f"{'[ CONTROLLER ]':<25} Evaluate Jadwal (Fitness) (User Role: {session['user']['role']})")

    if not session['user']['role'] == "ADMIN":
        return jsonify({ 'status': False, 'message': 'No Access!'})
    
    isCreated = dao.get_jadwal()
    if not isCreated and not isCreated.get('jadwal'):
        return jsonify({ 'status': False, 'message': 'Jadwal belum dibuat!'})
    elif isCreated and isCreated.get('jadwal'):
        return jsonify({ 'data': isCreated["report"] })

@generateJadwal.route("/generate_jadwal/get_simpanan_prodi", methods=["GET"])
@login_required
def get_simpanan_prodi():
    print(f"{'[ CONTROLLER ]':<25} Get Simpanan Prodi")

    if session['user']['role'] == "ADMIN":
        data = dao.get_simpanan_prodi(session['user']['list_prodi'])

    return jsonify({ 'data': data })