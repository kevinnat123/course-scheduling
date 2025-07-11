from flask import render_template, Blueprint, request, jsonify, session, abort
from dao.kaprodi.dataMataKuliahDao import dataMataKuliahDao
from flask_login import login_required

mataKuliah = Blueprint('mataKuliah', __name__)
dao = dataMataKuliahDao()

@mataKuliah.route("/data_mata_kuliah")
@login_required
def mataKuliah_index():
    print(f"{'[ RENDER ]':<25} Data Mata Kuliah (Role: {session['user']['role']})")
    if session['user']['role'] not in ["KEPALA PROGRAM STUDI", "ADMIN"]:
        return abort(403)
    else:
        return render_template(
                '/kaprodi/data_mataKuliah/index.html', 
                menu = 'Data Mata Kuliah', 
                title = 'Data Mata Kuliah', 
                prodi = session['user']['prodi'] 
                    if session['user']['role'] == "KEPALA PROGRAM STUDI"
                    else "",
                list_prodi = session['user']['list_prodi'],
            )
    
@mataKuliah.route("/data_mata_kuliah/get_kelompok", methods=['GET'])
@login_required
def mataKuliah_get_kelompok():
    print(f"{'[ CONTROLLER ]':<25} Get Kelompok")
    req = request.args.to_dict()
    data = dao.get_kelompok(req['prodi'])
    return jsonify({ 'data': data })
    
@mataKuliah.route("/data_mata_kuliah/get_matkul", methods=['GET'])
@login_required
def mataKuliah_get_matkul():
    print(f"{'[ CONTROLLER ]':<25} Get Matkul")
    data = dao.get_matkul()
    for matkul in data:
        matkul["asistensi"] = "Ada" if matkul["asistensi"] == True else None
    return jsonify({ 'data': data })

@mataKuliah.route("/data_mata_kuliah/get_matkul_by_prodi", methods=['GET'])
@login_required
def mataKuliah_get_matkul_by_prodi():
    print(f"{'[ CONTROLLER ]':<25} Get Matkul Prodi")
    param = request.args.to_dict()
    data = dao.get_matkul_by_prodi(param.get('prodi'))
    return jsonify({ 'data': data })

@mataKuliah.route("/data_mata_kuliah/post_matkul", methods=['POST'])
@login_required
def mataKuliah_post_matkul():
    print(f"{'[ CONTROLLER ]':<25} Post Matkul")
    req = request.get_json('data')
    data = dao.post_matkul(req)
    return jsonify( data )

@mataKuliah.route("/data_mata_kuliah/put_matkul", methods=['POST'])
@login_required
def mataKuliah_put_matkul():
    print(f"{'[ CONTROLLER ]':<25} Put Matkul")
    req = request.get_json('data')
    data = dao.put_matkul(req)
    return jsonify( data )

@mataKuliah.route("/data_mata_kuliah/delete_matkul", methods=['POST'])
@login_required
def mataKuliah_delete_matkul():
    print(f"{'[ CONTROLLER ]':<25} Delete Matkul")
    req = request.get_json('data')
    data = dao.delete_matkul(req)
    return jsonify( data )