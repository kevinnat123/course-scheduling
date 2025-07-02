from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from datetime import datetime, timezone
from userModel import User
from dao.loginDao import loginDao

signin = Blueprint('signin', __name__)
loginDao = loginDao()
            
@signin.route("/")
def home():
    print(f"{'[ THROW ]':<25} Login Page / Dashboard")
    if "user" in session and 'u_id' in session['user']:
        return redirect(url_for('dashboard.dashboard_index'))
    else:
        abort(401)
    
@signin.route("/login", methods=['GET', 'POST'])
def login():
    print(f"{'[ CONTROLLER ]':<25} Login (Method: {request.method})")
    # loginDao.signUp(u_id="asd", role="KEPALA PROGRAM STUDI", password="asd")
    if session.get('user') and 'u_id' in session['user']:
        return redirect(url_for('dashboard.dashboard_index'))
    
    if request.method == 'POST':
        req = request.get_json('data')
        nip = req.get('nip')
        password = req.get('password')

        user = loginDao.verify_user(nip, password)

        if user['status']:
            user_obj = User(nip, user['data'])
            login_user(user_obj)

            session_generator()
            menu = loginDao.get_menu(session['user']['role'])
            session['menu'] = menu if menu else []
            session['academic_details'] = get_academic_details()

            session.permanent = True  # Aktifkan waktu hidup session
            session.modified = True

            print(f"{'':<25} {'Session Academic_Details':<30}: {session['academic_details']}\n")
            print(f"{'':<25} {'Session Menu':<30}: {session['menu']}\n")
            print(f"{'':<25} {'Session LastSync':<30}: {session['last_sync']}\n")
            return jsonify({'status': True, 'redirect_url': url_for('dashboard.dashboard_index')}), 200
            # return jsonify({'status': True, 'redirect_url': url_for('dashboard.dashboard_index')}), 200

        return jsonify({'status': False, 'message': user['message']}), 401
    return render_template('signin.html')

# @signin.route("/dashboard")
# @login_required
# def dashboard():
#     print(f"{'[ RENDER ]':<25} Dashboard")

#     # Pastikan session masih valid
#     if not session.get('user') or 'u_id' not in session['user']:
#         print("⚠️ Session tidak valid, redirect ke login")
#         return redirect(url_for('signin.login'))
    
#     if session['user']['role'] == 'KEPALA PROGRAM STUDI':
#         return render_template(
#                 '/kaprodi/dashboard.html', 
#                 menu = 'Dashboard', 
#                 title = 'Dashboard', 
#                 prodi = session['user']['prodi'],
#                 kelompok_matkul = session['user']['kelompok_matkul']

#             )
#     elif session['user']['role'] == 'LABORAN':
#         return render_template(
#                 '/laboran/dashboard.html', 
#                 menu = 'Dashboard', 
#                 title = 'Dashboard', 
#                 list_os = session['user']['list_os'],
#                 list_processor = session['user']['list_processor']
#             )
#     elif session['user']['role'] == 'ADMIN':
#         return render_template(
#                 '/admin/dashboard.html', 
#                 menu = 'Dashboard', 
#                 title = 'Dashboard', 
#             )

def session_generator():
    user_id = session['user']['u_id']
    print(f"{'':<25} Session Generator (Old User Id: {user_id})")
    updated_user = loginDao.get_user(user_id)
    
    if updated_user:
        if session['user'].get('akses'):
            updated_user['data']['akses'] = session['user']['akses']
        session["user"] = updated_user["data"]
        print(f"{'':<25} {'New User Session':<30}: {session['user']}")

        list_prodi = loginDao.get_prodi()
        session['user']['list_prodi'] = list_prodi

        session['last_sync'] = datetime.now(timezone.utc)
        session.modified = True
    else:
        print(f"{'':<25} 🚫 User tidak valid di database")
        session.clear()  # Pastikan semua session terhapus
        abort(401)

def get_academic_details():
    today = datetime.today()
    current_year = today.year
    max_year = current_year if today.month > 3 else current_year - 1
    min_year = max_year - 7

    # Menentukan semester saat ini
    if today.month <= 3:
        semester_saat_ini = "Antara"
        semester_depan = "Genap"
    elif today.month <= 8:
        semester_saat_ini = "Genap"
        semester_depan = "Gasal"
    else:
        semester_saat_ini = "Gasal"
        semester_depan = "Antara"

    # Menentukan tahun ajaran
    tahun_ajaran_saat_ini = f"{current_year - 1}/{current_year}" if today.month <= 8 else f"{current_year}/{current_year + 1}"
    tahun_ajaran_berikutnya = f"{current_year}/{current_year + 1}" if today.month > 3 else f"{current_year - 1}/{current_year}"

    list_angkatan = list(range(min_year, max_year + 1))

    return {
        "min_year": min_year,
        "max_year": max_year,
        "semester_saat_ini": semester_saat_ini,
        "semester_depan": semester_depan,
        "tahun_ajaran_saat_ini": tahun_ajaran_saat_ini,
        "tahun_ajaran_berikutnya": tahun_ajaran_berikutnya,
        "list_angkatan": list_angkatan
    }

@signin.route("/logout")
def logout():
    print(f"{'[ THROW ]':<25} Logout")
    logout_user()
    session.clear()  # Pastikan semua session terhapus
    return redirect(url_for('signin.login'))