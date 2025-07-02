from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_URLS_COLLECTION as db_urls, MONGO_MAJOR_COLLECTION as db_prodi
from global_func import CustomError
from flask import session, abort
from werkzeug.security import check_password_hash, generate_password_hash

class loginDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def signUp(self, u_id, role, password):
        print(f"{'[ DAO ]':<25} Sign Up User: {u_id}")
        # # PYTHON 3.7.9 (Method Hash: "pbkdf2:sha256")
        # result = self.connection.insert_one(db_users, {'u_id': u_id, 'role': 'ADMIN', 'password': generate_password_hash(password, method='pbkdf2:sha256')})
        # DEFAULT HASH: "scrypt"
        result = self.connection.insert_one(
            collection_name = db_users, 
            data            = {
                    'u_id': u_id, 
                    'role': role.upper(), 
                    'password': generate_password_hash(password, method='pbkdf2:sha256'), 
                    'prodi': 'ASD'
                }
        )
        return result
    
    def get_user_id(self, u_id):
        print(f"{'[ DAO ]':<25} Get User ID: {u_id}")
        result = self.connection.find_one(
            collection_name = db_users, 
            filter          = {"u_id": u_id.upper()}
        )
        return result['data']['u_id'] if result and result.get('status') else None

    def get_user(self, u_id):
        print(f"{'[ DAO ]':<25} Get User: {u_id}")
        result = self.connection.find_one(
            collection_name = db_users, 
            filter          = {"u_id": u_id.upper()}
        )
        if result and result.get('status'):
            del result["data"]["password"]
        return result if result and result.get('status') else None
    
    def get_prodi(self):
        print(f"{'[ DAO ]':<25} Get Prodi")
        if session['user']['role'] in ["ADMIN", "LABORAN"]:
            result = self.connection.find_many(
                collection_name = db_prodi, 
                filter          = {"status_aktif": True}
            )
            if result and result.get('status'):
                list_prodi = [data["program_studi"] for data in result["data"] if data["status_aktif"] == True]
                return list_prodi
        elif session['user']['role'] == "KEPALA PROGRAM STUDI":
            return [session['user']['prodi']]
        return None
    
    def get_menu(self, role):
        print(f"{'[ DAO ]':<25} get menu: {role}")
        user_menu = self.connection.find_many(
            collection_name = db_urls, 
            filter          = {"role": role}
        )
        # Sort menu berdasarkan main role
        final_menu = []
        secondary = []
        if user_menu and user_menu.get('status') and user_menu.get('data'):
            for x in user_menu['data']:
                if x['main'] == role: 
                    del x['role'], x['main']
                    final_menu.append(x)
                else: 
                    del x['role'], x['main']
                    secondary.append(x)
            secondary = sorted(secondary, key=lambda x: x['title'])
            final_menu.extend(secondary)
        return final_menu

    def verify_user(self, u_id, password):
        print(f"{'[ DAO ]':<25} Verify User: {u_id}, {password}")
        result = { 'status': False }

        try:
            user = self.connection.find_one(
                collection_name = db_users, 
                filter          = {"u_id": u_id}
            )
            if user.get('status'):
                user_data = user['data']
                if user_data.get('role') not in ["ADMIN", "KEPALA PROGRAM STUDI", "LABORAN"]:
                    abort(401)

                if user_data.get('role') == "KEPALA PROGRAM STUDI":
                    prodi_user = self.connection.find_one(
                        collection_name = db_prodi, 
                        filter          = {"program_studi": user_data.get('prodi')}
                    )
                    if not prodi_user["status"]:
                        raise CustomError({ 'message': 'Program Studi anda tidak ditemukan!' })
    
                    prodi_data = prodi_user.get('data', {})
                    if not prodi_data.get("status_aktif"):
                        raise CustomError({ 'message': 'Program Studi anda sudah di non-aktifkan!' })

                stored_password = user_data.get('password', '')
                if check_password_hash(stored_password, password):
                    del user_data['password']
                    session['user'] = user_data
                    result.update({'data': user_data, 'message': 'Login berhasil'})
                else:
                    raise CustomError({ 'message': 'NIP atau password salah' })
            else:
                raise CustomError({ 'message': 'Anda tidak punya akun!' })
            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result