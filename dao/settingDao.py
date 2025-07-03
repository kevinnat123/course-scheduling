from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

class settingDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_user(self, u_id):
        print(f"{'[ DAO ]':<25} Get User")
        result = self.connection.find_one(
            collection_name = db_users, 
            filter          = {"u_id": u_id.upper()}
        )
        return result if result and result.get('status') else None

    def register_new_password(self, oldPassword, newPassword, verifyNewPassword):
        print(f"{'[ DAO ]':<25} Register New Password")
        user = self.get_user(session['user']['u_id'])
        if user:
            user_data = user['data']
            stored_password = user_data.get('password', '')
            if check_password_hash(stored_password, oldPassword):
                del user_data['password']
                if (oldPassword == newPassword):
                    return {'status': False, 'message': 'Silahkan masukkan password yang berbeda!'}
                
                if (newPassword == verifyNewPassword):
                    register_user_password = self.connection.update_one(
                        collection_name = db_users, 
                        filter          = { 'u_id': session['user']['u_id'] }, 
                        update_data     = { 
                            'password': generate_password_hash(newPassword),
                            'last_update': datetime.now().strftime("%d-%b-%Y")
                        }
                    )
                    if register_user_password and register_user_password['status']:
                        session['user']['last_update'] = datetime.now().strftime("%d-%b-%Y")
                        session.modified = True
                        return {'status': True, 'message': 'Password berhasil disimpan!'}
                else:
                    return {'status': False, 'message': 'Input password baru tidak cocok!'}
        return {'status': False, 'message': 'NIP atau password salah'}