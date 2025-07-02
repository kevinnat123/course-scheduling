from flask import render_template, Blueprint, request, jsonify, session, abort
from dao.laboran.dataRuanganDao import dataRuanganDao
from flask_login import login_required

dataRuangan = Blueprint('dataRuangan', __name__)
dao = dataRuanganDao()

@dataRuangan.route("/data_ruangan")
@login_required
def dataRuangan_index():
    print(f"{'[ RENDER ]':<25} Ruang Kelas (Role: {session['user']['role']})")
    if session['user']['role'] != 'LABORAN' and session['user']['role'] != "ADMIN":
        return abort(403)
    else:
        return render_template(
            '/laboran/data_ruangan/index.html', 
            menu = 'Ruang Kelas', 
            title = 'Ruang Kelas', 
        )
    
@dataRuangan.route("/data_ruangan/get_kelas", methods=['GET'])
@login_required
def dataRuangan_get_kelas():
    print(f"{'[ CONTROLLER ]':<25} Get Kelas")
    data = dao.get_kelas()
    return jsonify({ "data": data })
    
@dataRuangan.route("/data_ruangan/post_kelas", methods=['POST'])
@login_required
def dataRuangan_post_kelas():
    print(f"{'[ CONTROLLER ]':<25} Post Kelas")
    req = request.get_json('data')
    data = dao.post_kelas(req)
    return jsonify( data )

@dataRuangan.route("/data_ruangan/put_kelas", methods=['POST'])
@login_required
def dataRuangan_put_kelas():
    print(f"{'[ CONTROLLER ]':<25} Put Kelas")
    req = request.get_json('data')
    data = dao.put_kelas(req)
    return jsonify( data )

@dataRuangan.route("/data_ruangan/delete_kelas", methods=['POST'])
@login_required
def dataRuangan_delete_kelas():
    print(f"{'[ CONTROLLER ]':<25} Delete Kelas")
    req = request.get_json('data')
    data = dao.delete_kelas(req)
    return jsonify( data )