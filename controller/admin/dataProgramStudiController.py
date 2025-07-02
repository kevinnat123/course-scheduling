from flask import render_template, Blueprint, request, jsonify, session, abort
from flask.wrappers import Response
from dao.admin.dataProgramStudiDao import dataProgramStudiDao
from dao.kaprodi.dataDosenDao import dataDosenDao
from dao.loginDao import loginDao
from flask_login import login_required

program_studi = Blueprint('program_studi', __name__)
dao = dataProgramStudiDao()
dao_dosen = dataDosenDao()
dao_login = loginDao()

@program_studi.route("/data_program_studi")
@login_required
def program_studi_index():
    print(f"{'[ RENDER ]':<25} Data Program Studi (Role: {session['user']['role']})")
    print('========== ========== ========== ========== RENDER DATA PROGRAM STUDI  ========== ========== ========== ==========')
    if session['user']['role'] not in ["ADMIN"]:
        return abort(403)
    else:
        return render_template(
                '/admin/data_program_studi/index.html', 
                menu = 'Data Program Studi', 
                title = 'Data Program Studi', 
            )
    
@program_studi.route("/data_program_studi/get_program_studi", methods=['GET'])
@login_required
def program_studi_get_program_studi() -> Response:
    print(f"{'[ CONTROLLER ]':<25} Get Program Studi")
    data = dao.get_prodi()
    for prodi in data:
        if prodi.get("kepala_program_studi"):
            prodi["kepala_program_studi"] = dao_dosen.get_dosen_by_nip(prodi["kepala_program_studi"]).get("nama", prodi.get('kepala_program_studi', None))
    return jsonify({ 'data': data })

@program_studi.route("/data_program_studi/post_program_studi", methods=['POST'])
@login_required
def program_studi_post_program_studi() -> Response:
    print(f"{'[ CONTROLLER ]':<25} Post Program Studi")
    req = request.get_json('data')
    data = dao.post_prodi(req)
    return jsonify( data )

@program_studi.route("/data_program_studi/put_program_studi", methods=['POST'])
@login_required
def program_studi_put_program_studi() -> Response:
    print(f"{'[ CONTROLLER ]':<25} put Program Studi")
    req = request.get_json('data')
    data = dao.put_prodi(req)
    return jsonify( data )

@program_studi.route("/data_program_studi/verifikasi_user", methods=['GET'])
@login_required
def program_studi_verifikasi_user() -> Response:
    print(f"{'[ CONTROLLER ]':<25} Verifikasi User")
    user = dao_login.get_user(request.args.to_dict().get("nip"))
    if user and user.get("data") and user["data"].get("role") == "ADMIN":
        user["data"] = { "nama": user["data"]["nama"] }
    else:
        user = { "status": False, "message": "Anda tidak berhak!" }
    return jsonify( user )

@program_studi.route("/data_program_studi/user_validation", methods=['GET'])
@login_required
def program_studi_user_validation() -> Response:
    print(f"{'[ CONTROLLER ]':<25} User Validation")
    params = request.args.to_dict()
    params.pop('_')
    res = dao.user_validation(params)
    return jsonify( res )