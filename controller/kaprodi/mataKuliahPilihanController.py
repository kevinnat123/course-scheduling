from flask import render_template, Blueprint, request, jsonify, session, abort
from dao.dashboardDao import dashboardDao
from dao.kaprodi.mataKuliahPilihanDao import mataKuliahPilihanDao
from flask_login import login_required

mataKuliahPilihan = Blueprint('mataKuliahPilihan', __name__)
dash = dashboardDao()
dao = mataKuliahPilihanDao()

@mataKuliahPilihan.route("/mata_kuliah_pilihan")
@login_required
def mataKuliahPilihan_index():
    print(f"{'[ RENDER ]':<25} Mata Kuliah Pilihan (Role: {session['user']['role']})")
    if session['user']['role'] != 'KEPALA PROGRAM STUDI' and session['user']['role'] != "ADMIN":
        return abort(403)
    else:
        return render_template(
                '/kaprodi/mataKuliah_pilihan/index.html', 
                menu = 'Mata Kuliah Pilihan', 
                title = 'Mata Kuliah Pilihan', 
                prodi = session['user']['prodi'] 
                    if session['user']['role'] == "KEPALA PROGRAM STUDI"
                    else "",
                list_prodi = session['user']['list_prodi'],
                data_sebelum = dao.get_listMatkulTersimpan()
            )
    
@mataKuliahPilihan.route("/mata_kuliah_pilihan/get_bidang_minat", methods=['GET'])
@login_required
def mataKuliahPilihan_get_bidang_minat():
    print(f"{'[ CONTROLLER ]':<25} Get Bidang Minat")
    req = request.args.to_dict()
    data = dao.get_bidang_minat(req['prodi'])
    return jsonify({ 'data': data })
    
@mataKuliahPilihan.route("/mata_kuliah_pilihan/post_matkul", methods=['POST'])
@login_required
def mataKuliahPilihan_post_matkul():
    print(f"{'[ CONTROLLER ]':<25} Post Matkul Pilihan")
    req = request.get_json('data')
    data = dao.post_matkul(req)
    return jsonify( data )

@mataKuliahPilihan.route("/mata_kuliah_pilihan/put_matkul", methods=['POST'])
@login_required
def mataKuliahPilihan_put_matkul():
    print(f"{'[ CONTROLLER ]':<25} Put Matkul Pilihan")
    req = request.get_json('data')
    data = dao.put_matkul(req)
    return jsonify( data )

@mataKuliahPilihan.route("/mata_kuliah_pilihan/delete_data", methods=['POST'])
@login_required
def mataKuliahPilihan_delete_data():
    print(f"{'[ CONTROLLER ]':<25} Delete Matkul Pilihan")
    req = request.get_json('data')
    data = dao.delete_data(req)
    return jsonify( data )