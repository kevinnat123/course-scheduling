from flask import Flask, redirect, url_for, render_template, abort
from flask import request, session, jsonify
from flask_login import LoginManager, current_user, logout_user
from userModel import User
from dao.loginDao import loginDao
from datetime import timedelta

from controller.loginController import signin
from controller.dashboardController import dashboard
from controller.settingController import setting
from controller.excelController import export

# ADMIN
from controller.admin.dataProgramStudiController import program_studi
from controller.admin.generateJadwalController import generateJadwal

# LABORAN
from controller.laboran.dataRuanganController import dataRuangan

# KAPRODI
from controller.kaprodi.dataDosenController import dosen
from controller.kaprodi.dataMataKuliahController import mataKuliah
from controller.kaprodi.mataKuliahPilihanController import mataKuliahPilihan

login_manager = LoginManager()

# Factory function untuk membuat aplikasi Flask
def create_app():
    app = Flask(__name__)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)  # SESSION LIFETIME per 1 jam

    login_manager.init_app(app)
    login_manager.login_view = 'signin.login'

    @login_manager.user_loader
    def load_user(username):
        print(f"[ Load User ]")
        user_data = loginDao().get_user(username)
        if user_data:
            return User(username, user_data['data'])
        return None
    
    # Daftarkan Blueprint
    app.register_blueprint(signin)
    app.register_blueprint(dashboard)
    app.register_blueprint(setting)
    app.register_blueprint(export)

    # ADMIN
    app.register_blueprint(program_studi)
    app.register_blueprint(generateJadwal)

    # LABORAN
    app.register_blueprint(dataRuangan)

    # KAPRODI
    app.register_blueprint(dosen)
    app.register_blueprint(mataKuliah)
    app.register_blueprint(mataKuliahPilihan)
    
    # # Tambahkan konfigurasi tambahan jika diperlukan
    # app.config['SAMPLE_CONFIG'] = 'Sample Value'

    @app.errorhandler(401)
    def unathorized(e):
        print(f"[ Error 401 ]")
        # Jika user sudah login tapi datanya tidak valid
        if current_user.is_authenticated:
            logout_user()
        session.clear()
        return redirect(url_for('signin.login'))
    
    @app.errorhandler(403)
    def forbidden(e):
        print(f"[ Error 403 ]")
        return render_template('403.html', menu = "403 Forbidden", redirect_url = url_for('dashboard.dashboard_index'))

    @app.errorhandler(404)
    def page_not_found(e):
        print(f"[ Error 404 ]")
        return render_template('404.html', menu = "404 Not Found", redirect_url = url_for('dashboard.dashboard_index'))
    
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route("/ping")
    def ping():
        print(f"{'# HEARTBEAT #':<25} Session: {True if session.get('user') else False}")
        is_alive = session.get('user') and 'u_id' in session['user']
        if not is_alive:
            return jsonify({'status': False, 'expired': True}), 401
        return jsonify({'status': True, 'expired': False}), 200

    @app.before_request
    def check_session():
        safe_endpoints = ['signin.login', 'signin.logout', 'static', 'signin.ping', 'favicon']
        current_endpoint = request.endpoint

        # IF SAFE ENDPOINT
        if current_endpoint is None or current_endpoint in safe_endpoints or "index" in current_endpoint:
            return
        
        print(f"{'[ @ Before request ]':<25} Current Endpoint: {current_endpoint}")

        # Cek apakah session masih ada
        if not current_user.is_authenticated:
            print(f"{'':<25} ! Autentikasi user gagal")
            abort(401)
        elif current_user.is_authenticated:
            if current_user.last_update != session['user']['last_update']:
                logout_user()
                session.clear()
                return redirect(url_for('signin.login'))
        
        if "user" not in session or 'u_id' not in session['user']:
            print(f"{'':<25} ! Session tidak valid")
            abort(401)

        # Jangan reset lifetime kalau hanya /ping
        if not request.path.startswith('/ping'):
            print(f"{'':<25} ~ Perpanjang lifetime session")
            session.permanent = True
            session.modified = True

    # Cache control
    @app.after_request
    def add_cache_control(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    return app
