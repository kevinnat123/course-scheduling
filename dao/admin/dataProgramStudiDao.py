from dao import Database
from config import MONGO_DB, MONGO_MAJOR_COLLECTION as db_prodi, MONGO_USERS_COLLECTION as db_user
from config import MONGO_LECTURERS_COLLECTION as db_dosen
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from global_func import CustomError

class dataProgramStudiDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_prodi(self):
        print(f"{'[ DAO ]':<25} Get Program Studi")
        if session['user']['role'] == "ADMIN":
            result = self.connection.find_many(
                collection_name = db_prodi, 
                sort            = [("status_aktif", -1), ("program_studi", 1)]
            )
            if result and result.get('data'):
                for data in result['data']:
                    data['status_aktif'] = "AKTIF" if data["status_aktif"] else "NONAKTIF"
                    data.setdefault('kepala_program_studi', None)
        return result['data'] if result and result.get('status') else []
    
    def get_prodi_by_kaprodi(self, nip):
        print(f"{'[ DAO ]':<25} Get Program Studi By Kaprodi")
        if session['user']['role'] in ["ADMIN", "KEPALA PROGRAM STUDI"]:
            result = self.connection.find_one(
                collection_name = db_prodi, 
                filter          = { 'kepala_program_studi': nip }
            )
            if result and result.get('data'):
                result['data']['status_aktif'] = "AKTIF" if result['data']["status_aktif"] else "NONAKTIF"
                result['data'].setdefault('kepala_program_studi', None)
        return result['data'] if result and result.get('status') else []
    
    def post_prodi(self, params: dict):
        print(f"{'[ DAO ]':<25} Post Prodi (session['user']: {params})")
        result = { 'status': False }

        try:
            print('session akses', session['user'].get('akses'))
            if not session['user'].get('akses', False):
                raise CustomError({ 'reVerify': True })
                
            if session['user']['role'] != "ADMIN":
                raise CustomError({ 'message': 'Anda tidak berhak!' })

            if not params.get('program_studi'):
                raise CustomError({ 'message': 'Nama Program Studi belum diisi!', 'target': 'input_prodi' })
            elif not params.get('status_aktif'):
                raise CustomError({ 'message': 'Status Program Studi belum diisi!' })
            
            # Check is Program Studi exist
            res = self.connection.find_one(
                collection_name = db_prodi, 
                filter          = {'program_studi': params['program_studi']}
            )
            if (res['status'] == True):
                raise CustomError({ 'message': 'Data Program Studi sudah ada!' })
                
            # Hapus key yang memiliki value kosong
            params["status_aktif"] = True if params.pop("status_aktif", None) == "AKTIF" else False
            params = {k: v for k, v in params.items() if v or k in ["program_studi", "status_aktif"]}

            if params['status_aktif'] == True and params.get('kepala_program_studi'):
                # cek data dosen
                data_kaprodi_baru = self.connection.find_one(
                    collection_name = db_dosen,
                    filter          = { 'nama': params['kepala_program_studi'] }
                )
                if data_kaprodi_baru['status']:
                    nip_kaprodi = data_kaprodi_baru['data']['nip']
                    params['kepala_program_studi'] = nip_kaprodi
                    print('nip kaprodi', nip_kaprodi)
                    # tambahkan user baru
                    self.connection.insert_one(
                        collection_name = db_user,
                        data            = {
                            'u_id': nip_kaprodi,
                            'nama': data_kaprodi_baru['data']['nama'],
                            'password': generate_password_hash(nip_kaprodi, method='pbkdf2:sha256'),
                            'role': 'KEPALA PROGRAM STUDI',
                            'prodi': params['program_studi']
                        }
                    )
                else:
                    raise CustomError({ 'message': 'Data calon kaprodi tidak ditemukan' })
            else:
                params.pop('kepala_program_studi', None)
                
            params['fakultas'] = "FAKULTAS TEKNOLOGI INFORMASI"
            res = self.connection.insert_one(
                collection_name = db_prodi, 
                data            = params
            )

            if res['status'] == True:
                result.update({ 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })

            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def put_prodi(self, params: dict):
        print(f"{'[ DAO ]':<25} Put Prodi (Parameter: {params})")
        result = { 'status': False }

        try:
            print('session akses', session['user'].get('akses'))
            if not session['user'].get('akses', False):
                raise CustomError({ 'reVerify': True })
                
            if session['user']['role'] not in ["ADMIN"]:
                raise CustomError({ 'message': 'Anda tidak berhak!' })

            if not params.get('program_studi'):
                raise CustomError({ 'message': 'Nama Program Studi belum diisi!', 'target': 'input_prodi' })
            elif not params.get('status_aktif'):
                raise CustomError({ 'message': 'Status Program Studi belum diisi!' })
            
            # Check is Program Studi exist
            old_program_studi = params.pop('old_program_studi', None)
            isExist = self.connection.find_one(
                collection_name = db_prodi, 
                filter          = {'program_studi': old_program_studi}
            )
            if isExist['status'] == False:
                raise CustomError({ 'message': 'Data prodi ' + params['program_studi'] + ' tidak ditemukan!' })
            else:
                old_prodi = isExist['data']

            params["status_aktif"] = True if params.pop("status_aktif", None) == "AKTIF" else False
            unset = {k: "" for k, v in params.items() if not v and k not in ["fakultas", "program_studi", "status_aktif"]}

            params = {k: v for k, v in params.items() if v or k in ["fakultas", "program_studi", "status_aktif"]}

            if params['status_aktif'] == True:
                if params.get('kepala_program_studi'):
                    # cek data dosen
                    data_kaprodi_baru = self.connection.find_one(
                        collection_name = db_dosen,
                        filter          = { 'nama': params['kepala_program_studi'] }
                    )
                    if data_kaprodi_baru['status']:
                        data_kaprodi_baru = data_kaprodi_baru['data']
                        nip_kaprodi_baru = data_kaprodi_baru['nip']
                        params['kepala_program_studi'] = nip_kaprodi_baru
                        if old_prodi.get('kepala_program_studi') != nip_kaprodi_baru:
                            # hapus user kaprodi lama
                            self.connection.delete_one(
                                collection_name = db_user,
                                filter          = { 'u_id': old_prodi.get('kepala_program_studi') },
                            )
                            # tambahkan user baru
                            self.connection.insert_one(
                                collection_name = db_user,
                                data            = {
                                    'u_id': nip_kaprodi_baru,
                                    'nama': data_kaprodi_baru['nama'],
                                    'password': generate_password_hash(nip_kaprodi_baru, method='pbkdf2:sha256'),
                                    'role': 'KEPALA PROGRAM STUDI',
                                    'prodi': params['program_studi']
                                }
                            )
                        else:
                            params.pop('kepala_program_studi', None)
                    else:
                        raise CustomError({ 'message': 'Data calon kaprodi tidak ditemukan' })
            else:
                params.pop('kepala_program_studi', None)
                
            res = self.connection.update_one(
                collection_name = db_prodi, 
                filter          = {'program_studi': old_program_studi}, 
                update_data     = params, 
                unset_data      = unset
            )
            
            if res['status'] == True:
                result.update({ 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })

            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def user_validation(self, params: dict):
        print(f"{'[ DAO ]':<25} User Validation")
        result = { 'status': False }

        try:
            session['user']["akses"] = False

            if not params.get("nip"):
                raise CustomError({ 'message': 'NIP belum diisi!' })
            elif not params.get("password"):
                raise CustomError({ 'message': 'Password belum diisi!' })
            
            user = self.connection.find_one(
                collection_name = db_user, 
                filter          = {'u_id': params['nip']}
            )
            if user.get('status') and user["data"].get("role") in ["ADMIN"]:
                stored_password = user["data"].get('password', '')
                if check_password_hash(stored_password, params.get('password', '')):
                    session['user']['akses'] = True
                else:
                    raise CustomError({ 'message': "NIP atau password salah!" })
            elif not user.get('status'):
                raise CustomError({ 'message': "NIP tidak ditemukan!" })
            else:
                raise CustomError({ 'message': 'Anda tidak berhak!' })

            session.modified = True
            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result