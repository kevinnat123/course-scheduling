from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from dao.dashboardDao import dashboardDao
from dao.loginDao import loginDao
from dao.admin.dataProgramStudiDao import dataProgramStudiDao
from flask_login import login_user, logout_user, login_required

dashboard = Blueprint('dashboard', __name__)
dashboardDao = dashboardDao()

@dashboard.route("/dashboard")
@login_required
def dashboard_index():
    print(f"{'[ RENDER ]':<25} Dashboard (Role: {session['user']['role']})")
    if session['user']['role'] == 'KEPALA PROGRAM STUDI':
        prodiInfo = dataProgramStudiDao().get_prodi_by_kaprodi(session['user']['u_id'])
        if prodiInfo:
            return render_template(
                    '/kaprodi/dashboard.html', 
                    menu = 'Dashboard', 
                    title = 'Dashboard', 
                    prodi = session['user']['prodi'],
                    maks_sks = prodiInfo.get('maks_sks', 0),
                    kelompok_matkul = prodiInfo.get('kelompok_matkul', []),
                    pakar = prodiInfo.get('pakar', [])
                )
        else:
            print(f"{'💥💥💥💥💥':<25} 💣 Program Studi User tidak ditemukan")
            abort(401)
    elif session['user']['role'] == 'LABORAN':
        return render_template(
                '/laboran/dashboard.html', 
                menu = 'Dashboard', 
                title = 'Dashboard', 
            )
    elif session['user']['role'] == 'ADMIN':
        return render_template(
                '/admin/dashboard.html', 
                menu = 'Dashboard', 
                title = 'Dashboard', 
                list_prodi = session['user']['list_prodi']
            )
    else:
        return abort(403)
    
@dashboard.route("/get_pakar_prodi", methods=['GET'])
@login_required
def dashboard_getPakarProdi():
    print(f"{'[ CONTROLLER ]':<25} Get Data Pakar Prodi")
    req = request.args.to_dict()
    data = dashboardDao.get_pakar_prodi(req.get('prodi'), req.get('status_dosen'))
    return jsonify({ "data": data })

@dashboard.route("/update_general", methods=['POST'])
@login_required
def dashboardKaprodi_updateGeneral():
    print(f"{'[ CONTROLLER ]':<25} Update General")
    req = request.get_json('data')
    data = dashboardDao.update_general(req)
    return jsonify( data )

@dashboard.route("/update_kelompok_matkul", methods=['POST'])
@login_required
def dashboardKaprodi_updateKelompokMatkul():
    print(f"{'[ CONTROLLER ]':<25} Update Kelompok Matkul")
    req = request.get_json('data')
    data = dashboardDao.update_kelompokMatkul(req)
    return jsonify( data )

@dashboard.route("/update_pakar", methods=['POST'])
@login_required
def dashboardKaprodi_updatePakar():
    print(f"{'[ CONTROLLER ]':<25} Update Pakar")
    req = request.get_json('data')
    data = dashboardDao.update_pakar(req)
    return jsonify( data )    

@dashboard.route("/update_os", methods=['POST'])
@login_required
def dashboardLaboran_updateOs():
    print(f"{'[ CONTROLLER ]':<25} Update OS")
    
    req = request.get_json('data')

    result = dashboardDao.update_os(req)

    return jsonify( result )

@dashboard.route("/update_processor", methods=['POST'])
@login_required
def dashboardLaboran_updateProcessor():
    print(f"{'[ CONTROLLER ]':<25} Update Processor")
    
    req = request.get_json('data')

    result = dashboardDao.update_processor(req)

    return jsonify( result )

@dashboard.route("/update_prodi", methods=['POST'])
@login_required
def dashboardLaboran_updateProdi():
    print(f"{'[ CONTROLLER ]':<25} Update Prodi")
    
    req = request.get_json('data')

    result = dashboardDao.update_prodi(req)

    return jsonify( result )