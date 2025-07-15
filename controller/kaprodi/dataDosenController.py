from flask import render_template, Blueprint, request, jsonify, session, abort
from dao.kaprodi.dataDosenDao import dataDosenDao
from flask_login import login_required

dosen = Blueprint('dosen', __name__)
dao = dataDosenDao()

@dosen.route("/data_dosen")
@login_required
def dosen_dosen_index():
    print(f"{'[ RENDER ]':<25} Data Dosen (Role: {session['user']['role']})")
    print('========== ========== ========== ========== RENDER DATA DOSEN  ========== ========== ========== ==========')
    if session['user']['role'] not in ["KEPALA PROGRAM STUDI", "ADMIN"]:
        return abort(403)
    else:
        return render_template(
                '/kaprodi/data_dosen/index.html', 
                menu = 'Data Dosen', 
                title = 'Data Dosen', 
                prodi = session['user']['prodi'] 
                    if session['user']['role'] == "KEPALA PROGRAM STUDI"
                    else "",
                list_prodi = session['user']['list_prodi']
            )
    
@dosen.route("/data_dosen/get_display_dosen", methods=['GET'])
@login_required
def dosen_get_display_dosen():
    print(f"{'[ CONTROLLER ]':<25} Get Display Dosen")
    data = dao.get_display_dosen()
    return jsonify({ 'data': data })
    
@dosen.route("/data_dosen/get_dosen", methods=['GET'])
@login_required
def dosen_get_dosen():
    print(f"{'[ CONTROLLER ]':<25} Get Dosen")
    data = dao.get_dosen()
    return jsonify({ 'data': data })

@dosen.route("/data_dosen/get_dosen_prodi", methods=['GET'])
@login_required
def dosen_get_dosen_prodi():
    print(f"{'[ CONTROLLER ]':<25} Get Dosen Prodi")
    param = request.args.to_dict()
    data = dao.get_dosen_prodi(param.get('prodi'))
    return jsonify({ 'data': data })

@dosen.route("/data_dosen/post_dosen", methods=['POST'])
@login_required
def dosen_post_dosen():
    print(f"{'[ CONTROLLER ]':<25} Post Dosen")
    req = request.get_json('data')
    data = dao.post_dosen(req)
    return jsonify( data )

@dosen.route("/data_dosen/put_dosen", methods=['POST'])
@login_required
def dosen_put_dosen():
    print(f"{'[ CONTROLLER ]':<25} Put Dosen")
    req = request.get_json('data')
    data = dao.put_dosen(req)
    return jsonify( data )

@dosen.route("/data_dosen/delete_dosen", methods=['POST'])
@login_required
def dosen_delete_dosen():
    print(f"{'[ CONTROLLER ]':<25} Delete Dosen")
    abort(401)
    req = request.get_json('data')
    data = dao.delete_dosen(req)
    return jsonify( data )