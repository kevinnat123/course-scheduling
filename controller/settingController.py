from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.settingDao import settingDao
from flask_login import login_user, logout_user, login_required

setting = Blueprint('setting', __name__)
settingDao = settingDao()

@setting.route("/setting")
@login_required
def setting_index():
    print(f"{'[ RENDER ]':<25} Setting (Role: {session['user']['role']})")
    return render_template(
            '/setting.html', 
            menu = 'Setting', 
            title = 'Setting', 
        )

@setting.route("/pengaturan_akun", methods=['POST'])
@login_required
def setting_pengaturanAkun():
    print(f"{'[ CONTROLLER ]':<25} Pengaturan Akun")
    req = request.get_json('data')
    username = req.get('username')
    newPassword = req.get('new_password')
    confirmPassword = req.get('confirm_password')

    manage_account = settingDao.manage_account(username, newPassword, confirmPassword)

    return jsonify( manage_account )
    
@setting.route("/register_new_password", methods=['GET', 'POST'])
@login_required
def setting_registerNewPassword():
    print(f"{'[ CONTROLLER ]':<25} Register New Password (Method: {request.method})")
    if request.method == 'POST':
        req = request.get_json('data')
        oldPassword = req.get('oldPassword')
        newPassword = req.get('newPassword')
        verifyNewPassword = req.get('verifyNewPassword')

        manage_new_password = settingDao.register_new_password(oldPassword, newPassword, verifyNewPassword)
            
    return jsonify( manage_new_password )