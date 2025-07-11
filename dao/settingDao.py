from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users
from flask import session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from global_func import CustomError

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

    def manage_account(self, username, newPassword, confirmPassword):
        print(f"{'[ DAO ]':<25} Manage Account")
        result = { 'status': False }

        try:
            user = self.get_user(session['user']['u_id'])
            if user['status']:
                user_data = user['data']
                stored_password = user_data.get('password', '')
                del user_data['password']
                if newPassword == session['user']['u_id']:
                    raise CustomError({ 'message': 'Harap gunakan password lain!' })
                elif check_password_hash(stored_password, newPassword):
                    raise CustomError({ 'message': 'Silahkan masukkan password yang berbeda!' })
                elif newPassword != confirmPassword:
                    raise CustomError({ 'message': 'Password tidak sesuai!' })
                
                if username:
                    usernameExist = self.connection.find_one(
                        collection_name = db_users,
                        filter          = {
                            'username': username,
                            'u_id': {'$ne': session['user']['u_id']}
                        }
                    )
                    if usernameExist['status']: raise CustomError({ 'message': 'Harap gunakan username lain!' })
                
                if (newPassword == confirmPassword):
                    register_user_password = self.connection.update_one(
                        collection_name = db_users, 
                        filter          = { 'u_id': session['user']['u_id'] }, 
                        update_data     = { 
                            'username': username,
                            'password': generate_password_hash(newPassword, method='pbkdf2:sha256'),
                            'last_update': datetime.now().strftime("%d-%b-%Y")
                        }
                    )
                    if register_user_password and register_user_password['status']:
                        session['user']['last_update'] = datetime.now().strftime("%d-%b-%Y")
                        session.modified = True
                        result['message'] = 'Password berhasil disimpan!'
                else:
                    raise CustomError({ 'message': 'Input password baru tidak cocok!' })
            else:
                raise CustomError({ 'message': 'NIP atau password salah' })

            result.update({
                'status': True,
                'redirect_url': url_for('dashboard.dashboard_index')
            })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(e)
            result['message'] = 'Terjadi kesalahan sistem. Harap hubungi Admin.'
        return result

    def register_new_password(self, oldPassword, newPassword, verifyNewPassword):
        print(f"{'[ DAO ]':<25} Register New Password")
        result = { 'status': False }
        try:
            user = self.get_user(session['user']['u_id'])
            if user['status']:
                user_data = user['data']
                stored_password = user_data.get('password', '')
                del user_data['password']
                if check_password_hash(stored_password, oldPassword):
                    if newPassword == session['user']['u_id']:
                        raise CustomError({ 'message': 'Harap gunakan password lain!' })
                    elif check_password_hash(stored_password, newPassword):
                        raise CustomError({ 'message': 'Silahkan masukkan password yang berbeda!' })
                    elif newPassword != verifyNewPassword:
                        raise CustomError({ 'message': 'Password tidak sesuai!' })
                    
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
                            raise CustomError({ 'message': 'Password berhasil disimpan!' })
                    else:
                        raise CustomError({ 'message': 'Input password baru tidak cocok!' })
                else:
                    raise CustomError({ 'message': 'Password lama tidak sesuai!' })
            else:
                raise CustomError({ 'message': 'NIP atau password salah' })
            result.update({
                'status': True,
                'redirect_url': url_for('dashboard.dashboard_index')
            })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(e)
            result['message'] = 'Terjadi kesalahan sistem. Harap hubungi Admin.'
        return result