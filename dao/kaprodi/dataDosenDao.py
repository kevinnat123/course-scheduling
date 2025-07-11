from dao import Database
from config import MONGO_DB, MONGO_LECTURERS_COLLECTION as db_dosen, MONGO_COURSES_COLLECTION as db_matkul
from flask import session

from dao.dashboardDao import dashboardDao
from global_func import CustomError

class dataDosenDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_dosen(self):
        print(f"{'[ DAO ]':<25} Get Dosen")
        if session['user']['role'] == "KEPALA PROGRAM STUDI":
            result = self.connection.find_many(
                collection_name = db_dosen, 
                filter          = {
                        '$or': [
                            {'prodi': session['user']['prodi']}, 
                            {'status': 'TIDAK_TETAP'}
                        ]
                    }, 
                sort            = [ ("status", 1), ("nip", 1) ]
            )
        elif session['user']['role'] == "ADMIN":
            result = self.connection.find_many(
                collection_name = db_dosen, 
                filter          = { 'status': {'$ne': 'TIDAK_AKTIF'} }, 
                sort            = [ ("status", 1), ("nip", 1) ]
            )
        if result and result.get('status'):
            for dosen in result['data']:
                dosen.setdefault('pakar', None)
                dosen.setdefault('prodi', None)
                # dosen.setdefault('matkul_ajar', None)
        return result['data'] if result and result.get('status') else []
    
    def get_dosen_prodi(self, prodi):
        print(f"{'[ DAO ]':<25} Get Dosen Prodi (Prodi: {prodi})")
        result = self.connection.find_many(
            collection_name = db_dosen, 
            filter          = {
                    # '$and': [
                        # {
                            '$or': [
                                {'prodi': prodi}, 
                                {'status': 'TIDAK_TETAP'}
                            ]
                        # },
                        # {
                        #     'status': { '$ne': 'TIDAK_AKTIF' }
                        # }
                    # ]
                }, 
            sort            = [ ("status", 1), ("nip", 1) ]
        )
        if result and result.get('status'):
            for dosen in result['data']:
                dosen.setdefault('pakar', None)
                dosen.setdefault('prodi', None)
                # dosen.setdefault('matkul_ajar', None)
        return result['data'] if result and result.get('status') else []
    
    def get_dosen_by_nip(self, nip):
        print(f"{'[ DAO ]':<25} Get Dosen By NIP (NIP: {nip})")
        result = self.connection.find_one(
            collection_name = db_dosen,
            filter          = {"nip": nip}
        )
        return result['data'] if result and result.get('status') else []
    
    def post_dosen(self, params: dict):
        print(f"{'[ DAO ]':<25} Post Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('nip'):
                raise CustomError({ 'message': 'NIP belum diisi!', 'target': 'input_nip' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama belum diisi!', 'target': 'input_nama' })
            elif not params.get("status"):
                raise CustomError({ 'message': 'Status Dosen belum diisi!' })
            elif not params.get('prodi') and params.get('status') != "TIDAK_TETAP":
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            
            # Check exist
            res = self.connection.find_one(
                collection_name = db_dosen, 
                filter          = {'nip': params['nip']}
            )
            if (res['status'] == True):
                raise CustomError({ 'message': 'Data dengan NIP ' + params['nip'] + ' sudah ada!' })
            if session['user']['role'] == "KEPALA PROGRAM STUDI":
                if params['prodi'] != session['user']['prodi'] and params.get('status') != "TIDAK_TETAP":
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })
                
            # Hapus key yang memiliki value kosong
            if params.get('preferensi'):
                if params['preferensi'].get('value'):
                    params['preferensi'] = {k: v for k, v in params['preferensi'].items() if v}
                    params['preferensi'].pop('value', None)
                else:
                    params.pop('preferensi', None)
            if params.get('status') and str(params.get('status')) == "TIDAK_TETAP":
                params.pop('prodi', None)

            if params.get('pakar'):
                accessible_field = dashboardDao().get_pakar_prodi(prodi=params.get('prodi'), status_dosen=params.get('status'))
                accessible_field = [item['pakar'] for item in accessible_field]
                params['pakar'] = [item for item in params['pakar'] if item in accessible_field]
                
            params = {k: v for k, v in params.items() if v}

            res = self.connection.insert_one(
                collection_name = db_dosen, 
                data            = params
            )

            # update matkul
            if params.get('matkul_ajar'):
                for matkul in params['matkul_ajar']:
                    exist = self.connection.find_one(
                        collection_name = db_matkul, 
                        filter          = {"nama": matkul}
                    )
                    if exist and exist.get('status'):
                        dosen_ajar_lama = exist['data'].get('dosen_ajar') or []
                        if params['nama'] not in dosen_ajar_lama:
                            dosen_ajar_lama.append(params['nama'])
                            self.connection.update_one(
                                collection_name = db_matkul, 
                                filter          = {"nama": matkul}, 
                                update_data     = {"dosen_ajar": dosen_ajar_lama}
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
    
    def put_dosen(self, params: dict):
        print(f"{'[ DAO ]':<25} Put Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('nip'):
                raise CustomError({ 'message': 'NIP belum diisi!' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama belum diisi!', 'target': 'input_nama' })
            elif not params.get('status'):
                raise CustomError({ 'message': 'Status Dosen belum diisi!' })
            elif not params.get('prodi') and params.get('status') != "TIDAK_TETAP":
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            
            # Check exist
            dosen_exist = self.connection.find_one(
                collection_name = db_dosen, 
                filter          = {'nip': params['nip']}
            )
            if (dosen_exist['status'] == False and dosen_exist['data'] == None):
                raise CustomError({ 'message': 'Data dengan NIP ' + params['nip'] + ' tidak ditemukan!' })

            if session['user']['role'] == "KEPALA PROGRAM STUDI":    
                if params['prodi'] != session['user']['prodi'] and params.get('status') != "TIDAK_TETAP":
                    raise CustomError({ 'message': 'Anda mengubah program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })
            
            unset = {k: "" for k, v in params.items() if not v}

            if params.get('preferensi'):
                if params['preferensi'].get('value'):
                    params['preferensi'].pop('value', None)

                    # params['preferensi'] = {k: v for k, v in params['preferensi'].items() if v}
                    preferensi = []
                    for k, v in dict(params['preferensi']).items():
                        preferensi.append(k)
                        if v:
                            params[f'preferensi.{k}'] = v
                        else:
                            unset[f'preferensi.{k}'] = ""
                        params["preferensi"].pop(k, None)

                    if all(f"preferensi.{k}" in unset for k in preferensi):
                        for k in preferensi:
                            unset.pop(f"preferensi.{k}")
                        unset["preferensi"] = ""
                else:
                    params.pop('preferensi', None)
                    unset['preferensi'] = ""
            if params.get('status') and str(params.get('status')) == "TIDAK_TETAP":
                if 'prodi' in params: 
                    unset['prodi'] = ""
                    params.pop('prodi', None)

            if params.get('pakar'):
                accessible_field = dashboardDao().get_pakar_prodi(prodi=params.get('prodi'), status_dosen=params.get('status'))
                accessible_field = [item['pakar'] for item in accessible_field]
                params['pakar'] = [item for item in params['pakar'] if item in accessible_field]
            if not params.get('pakar'):
                unset['pakar'] = ""
                params.pop('pakar', None)

            params = {k: v for k, v in params.items() if v}
                
            print(params)
            print(unset)
            res = self.connection.update_one(
                collection_name = db_dosen, 
                filter          = {'nip': params['nip']}, 
                update_data     = params, 
                unset_data      = unset
            )

            # update matkul
            if params.get('matkul_ajar'):
                for matkul in params['matkul_ajar']:
                    exist = self.connection.find_one(
                        collection_name = db_matkul, 
                        filter          = {"nama": matkul}
                    )
                    if exist and exist.get('status'):
                        dosen_ajar_lama = exist['data'].get('dosen_ajar') or []
                        if params['nama'] not in dosen_ajar_lama:
                            dosen_ajar_lama.append(params['nama'])
                            self.connection.update_one(
                                collection_name = db_matkul, 
                                filter          = {"nama": matkul}, 
                                update_data     = {"dosen_ajar": dosen_ajar_lama}
                            )

            if len(params.get('matkul_ajar') or []) < len(dosen_exist['data'].get('matkul_ajar') or []):
                matkul_ajar_lama = dosen_exist['data'].get('matkul_ajar') or []
                matkul_ajar_baru = params.get('matkul_ajar') or []
                data_dihapus = [dt for dt in matkul_ajar_lama if dt not in matkul_ajar_baru]

                for matkul in data_dihapus:
                    data_matkul = self.connection.find_one(
                        collection_name = db_matkul, 
                        filter          = {'nama': matkul}
                    )
                    if data_matkul and data_matkul.get('status'):
                        old_data = data_matkul['data']
                        old_data['dosen_ajar'].remove(params['nama'])
                        if old_data['dosen_ajar']:
                            self.connection.update_one(
                                collection_name = db_matkul, 
                                filter          = {'nama': matkul}, 
                                update_data     = {'dosen_ajar': old_data['dosen_ajar']}
                            )
                        else:
                            self.connection.update_one(
                                collection_name = db_matkul, 
                                filter          = {'nama': matkul}, 
                                update_data     = {}, 
                                unset_data      = {'dosen_ajar': ""}
                            )
                    else:
                        raise Exception
            
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
    
    def delete_dosen(self, params: dict):
        print(f"{'[ DAO ]':<25} Delete Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            raise CustomError({ 'message': 'This action has been disabled!' })
            if session['user']['role'] not in ['ADMIN']:
                params = self.connection.find_many(
                    collection_name = db_dosen, 
                    filter          = {
                            'nip': { 
                                '$in' : [item['nip'] for item in params] 
                            }
                        }, 
                    sort            = [("kode", 1)]
                )
                if params and params.get('status'):
                    params = params['data']
                    list_nip = [d['nip'] for d in params]
                    list_prodi = [d['prodi'] for d in params]
                else:
                    raise Exception

                if session['user']['role'] == "KEPALA PROGRAM STUDI":
                    if any(prodi != session['user']['prodi'] for prodi in list_prodi):
                        raise CustomError({ 'message': 'Anda mengubah program studi diluar program studi anda! (Input Anda: ' + str([prodi for prodi in list_prodi if prodi != session['user']['prodi']]) + ')' })

                for data_dosen in params:
                    matkul_ajar_dosen = data_dosen.get('matkul_ajar') or []
                    for matkul in matkul_ajar_dosen:
                        data_matkul = self.connection.find_one(
                            collection_name = db_matkul, 
                            filter          = {'nama': matkul}
                        )
                        if data_matkul and data_matkul.get('status'):
                            data_matkul = data_matkul['data']
                            data_matkul['dosen_ajar'].remove(data_dosen['nama'])
                            if data_matkul['dosen_ajar']:
                                self.connection.update_one(
                                    collection_name = db_matkul, 
                                    filter          = {'nama': matkul}, 
                                    update_data     = {'dosen_ajar': data_matkul['dosen_ajar']}
                                )
                            else:
                                self.connection.update_one(
                                    collection_name = db_matkul, 
                                    filter          = {'nama': matkul}, 
                                    update_data     = {}, 
                                    unset_data      = {'dosen_ajar': ""}
                                )
                        else:
                            raise Exception
                    
                res = self.connection.delete_many(
                    collection_name = db_dosen, 
                    filter          = { 
                            'nip' : { '$in': list_nip }, 
                        }
                )
                if res['status'] == False:
                    raise CustomError({ 'message': res['message'] })
                else:
                    result.update({ 'status': True, 'message': res['message'] })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result