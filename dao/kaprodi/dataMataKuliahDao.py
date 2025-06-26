from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_COURSES_COLLECTION as db_matkul, MONGO_LECTURERS_COLLECTION as db_dosen
from config import MONGO_MAJOR_COLLECTION as db_prodi
from flask import session

from global_func import CustomError

ASISTENSI_RELATED = ['asistensi', 'tipe_kelas_asistensi', 'integrated_class']
TEAM_TEACHING_RELATED = ['team_teaching', 'jumlah_dosen']

class dataMataKuliahDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_kelompok(self, prodi):
        print(f"{'[ DAO ]':<25} Get Kelompok (Prodi: {prodi})")
        result = self.connection.find_one(
            collection_name = db_prodi, 
            filter          = { 'program_studi': prodi }
        )
        if result and result.get('status'):
            if result['data'].get('kelompok_matkul'):
                return result['data']['kelompok_matkul']
        return []

    def get_matkul(self):
        print(f"{'[ DAO ]':<25} Get Matkul")
        if session['user']['role'] == "KEPALA PROGRAM STUDI":
            result = self.connection.find_many(
                collection_name = db_matkul, 
                filter          = {'prodi': { '$in' : [session['user']['prodi']] }}, 
                # { '$in' : ['GENERAL', session['user']['prodi']] }
                sort            = [("kode", 1)]
            )
        elif session['user']['role'] == "ADMIN":
            result = self.connection.find_many(
                collection_name = db_matkul, 
                sort            = [ ("prodi", 1), ("kode", 1) ]
            )
        if result and result.get('status'):
            for matkul in result['data']:
                matkul.setdefault('kelompok', None)
                matkul.setdefault('asistensi', None)
                matkul.setdefault('prodi', None)
        return result['data'] if result and result.get('status') else []
    
    def get_matkul_by_prodi(self, prodi=""):
        print(f"{'[ DAO ]':<25} Get Matkul By Prodi (prodi: {prodi})")
        result = self.connection.find_many(
            collection_name = db_matkul, 
            filter          = {'prodi': prodi}, 
            sort            = [ ("kode", 1) ]
        )
        if result and result.get('status'):
            for matkul in result['data']:
                matkul.setdefault('kelompok', None)
                matkul.setdefault('asistensi', None)
                matkul.setdefault('prodi', None)
        return result['data'] if result and result.get('status') else []
    
    def get_matkul_by_kode(self, list_kode=[]):
        print(f"{'[ DAO ]':<25} Get Matkul By Kode (list_kode: {str(list_kode)})")
        result = self.connection.find_many(
            collection_name = db_matkul, 
            filter          = { 'kode': {'$in': list_kode} }, 
            sort            = [ ("kode", 1) ]
        )
        if result and result.get('status'):
            for matkul in result['data']:
                matkul.setdefault('kelompok', None)
                matkul.setdefault('asistensi', None)
                matkul.setdefault('prodi', None)
        return result['data'] if result and result.get('status') else []
    
    def post_matkul(self, params: dict):
        print(f"{'[ DAO ]':<25} Post Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Matkul belum diisi!', 'target': 'input_kode' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama Matkul belum diisi!', 'target': 'input_nama' })
            elif not params.get('sks_akademik') or not params.get('sks_bayar'):
                raise CustomError({ 'message': 'SKS Akademik / Bayar belum diisi!', 'target': 'input_sksA' if not params.get('sks_akademik') else 'input_sksB' })
            elif not params.get('prodi'):
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            elif not params.get('tipe_kelas'):
                raise CustomError({ 'message': 'Tipe Kelas belum diisi!' })
            elif params.get('asistensi') and not params.get('integrated_class') and not params.get('tipe_kelas_asistensi'):
                raise CustomError({ 'message': 'Tipe Kelas Asistensi belum diisi!' })
            elif params.get('team_teaching') and not params.get('jumlah_dosen'):
                raise CustomError({ 'message': 'Jumlah Dosen Pengajar belum diisi!' })

            if session['user']['role'] == "KEPALA PROGRAM STUDI":
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })

            # Check exist
            isExist = self.connection.find_one(
                collection_name = db_matkul, 
                filter          = {'kode': params['kode']}
            )
            if (isExist['status'] == True):
                raise CustomError({ 'message': 'Data dengan Kode Matkul ' + params['kode'] + ' sudah ada!' })

            # Hapus key yang memiliki value kosong
            if not params.get('asistensi'):
                for x in ASISTENSI_RELATED:
                    params.pop(x, None)
            else:
                if params.get('integrated_class'):
                    params.pop('tipe_kelas_asistensi', None)
            if not params.get('team_teaching'):
                for x in TEAM_TEACHING_RELATED:
                    params.pop(x, None)
            params = {k: v for k, v in params.items() if v}

            # Update Dosen
            if params.get('dosen_ajar'):
                for dosen in params['dosen_ajar']:
                    data_dosen = self.connection.find_one(
                        collection_name = db_dosen, 
                        filter          = {'nama': dosen}
                    )
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data'].get('matkul_ajar') or []
                        if params['nama'] not in data_dosen:
                            data_dosen.append(params['nama'])
                            self.connection.update_one(
                                collection_name = db_dosen, 
                                filter          = {'nama': dosen}, 
                                update_data     = {'matkul_ajar': data_dosen})

            res = self.connection.insert_one(
                collection_name = db_matkul, 
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

        print(f"{'':<25} Result: {result}")
        return result
    
    def put_matkul(self, params: dict):
        print(f"{'[ DAO ]':<25} Put Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Matkul belum diisi!', 'target': 'input_kode' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama Matkul belum diisi!', 'target': 'input_nama' })
            elif not params.get('sks_akademik') or not params.get('sks_bayar'):
                raise CustomError({ 'message': 'SKS Akademik / Bayar belum diisi!', 'target': 'input_sksA' if not params.get('sks_akademik') else 'input_sksB' })
            elif not params.get('prodi'):
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            elif not params.get('tipe_kelas'):
                raise CustomError({ 'message': 'Tipe Kelas belum diisi!' })
            elif params.get('asistensi') and not params.get('integrated_class') and not params.get('tipe_kelas_asistensi'):
                raise CustomError({ 'message': 'Tipe Kelas Asistensi belum diisi!' })
            elif params.get('team_teaching') and not params.get('jumlah_dosen'):
                raise CustomError({ 'message': 'Jumlah Dosen Pengajar belum diisi!' })
                
            if session['user']['role'] == "KEPALA PROGRAM STUDI":
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })
                
            isExist = self.connection.find_one(
                collection_name = db_matkul, 
                filter          = {'kode': params['kode']}
            )
            if isExist['status'] == False:
                raise CustomError({ 'message': 'Data dengan Kode Matkul ' + params['kode'] + ' tidak ditemukan!' })
            
            # Hapus key yang memiliki value kosong
            unset = {k: "" for k, v in params.items() if not v}
            if not params.get('asistensi'):
                for x in ASISTENSI_RELATED:
                    params.pop(x, None)
                    if x not in unset: unset[x] = ""
            else:
                if params.get('integrated_class'):
                    if 'tipe_kelas_asistensi' in params: 
                        unset['tipe_kelas_asistensi'] = ""
                        params.pop('tipe_kelas_asistensi', None)
            if not params.get('team_teaching'):
                for x in TEAM_TEACHING_RELATED:
                    params.pop(x, None)
                    if x not in unset: unset[x] = ""
            params = {k: v for k, v in params.items() if v}
            
            res = self.connection.update_one(
                collection_name = db_matkul, 
                filter          = {'kode': params['kode']}, 
                update_data     = params, 
                unset_data      = unset
            )

            # Update Dosen
            if params.get('dosen_ajar'):
                for dosen in params['dosen_ajar']:
                    data_dosen = self.connection.find_one(
                        collection_name = db_dosen, 
                        filter          = {'nama': dosen}
                    )
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data'].get('matkul_ajar') or []
                        if params['nama'] not in data_dosen:
                            data_dosen.append(params['nama'])
                            self.connection.update_one(
                                collection_name = db_dosen, 
                                filter          = {'nama': dosen}, 
                                update_data     = {'matkul_ajar': data_dosen}
                            )
                    else:
                        raise Exception

            if len(params.get('dosen_ajar') or []) < len(isExist['data'].get('dosen_ajar') or []):
                dosen_ajar_lama = isExist['data'].get('dosen_ajar') or []
                dosen_ajar_baru = params.get('dosen_ajar') or []
                data_dihapus = [dt for dt in dosen_ajar_lama if dt not in dosen_ajar_baru]

                for dosen in data_dihapus:
                    data_dosen = self.connection.find_one(
                        collection_name = db_dosen, 
                        filter          = {'nama': dosen}
                    )
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data']
                        data_dosen['matkul_ajar'].remove(params['nama'])
                        if data_dosen['matkul_ajar']:
                            self.connection.update_one(
                                collection_name = db_dosen, 
                                filter          = {'nama': dosen}, 
                                update_data     = {'matkul_ajar': data_dosen["matkul_ajar"]}
                            )
                        else:
                            self.connection.update_one(
                                collection_name = db_dosen, 
                                filter          = {'nama': dosen}, 
                                update_data     = {}, 
                                unset_data      = {'matkul_ajar': ''}
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

        print(f"{'':<25} Result: {result}")
        return result
    
    def delete_matkul(self, params: dict):
        print(f"{'[ DAO ]':<25} Delete Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            params = self.connection.find_many(
                collection_name = db_matkul, 
                filter          = {'kode': { '$in' : [item['kode'] for item in params] }}, 
                sort            = [ ("kode", 1) ]
            )
            if params and params.get('status'):
                params = params['data']
                list_kode = [item["kode"] for item in params]
                list_prodi = [item["prodi"] for item in params]
            else:
                raise Exception
            
            if session['user']['role'] == "KAPRODI":
                if any(prodi != session['user']['prodi'] for prodi in list_prodi):
                    raise CustomError({ 'message': 'Anda mengubah program studi diluar program studi anda! (Input Anda: ' + str([prodi for prodi in list_prodi if prodi != session['user']['prodi']]) + ')' })
                if 'GENERAL' in list_prodi:
                    raise CustomError({ 'message': 'Matkul ' + [item.get('kode') for item in params if item["prodi"] == "GENERAL"] + ' tidak bisa dihapus!' })
            
            for matkul in params:
                dosen_ajar_matkul = matkul.get('dosen_ajar') or []
                for dosen in dosen_ajar_matkul:
                    data_dosen = self.connection.find_one(
                        collection_name = db_dosen, 
                        filter          = {'nama': dosen}
                    )
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data']
                        data_dosen['matkul_ajar'].remove(matkul['nama'])
                        if data_dosen['matkul_ajar']:
                            self.connection.update_one(
                                collection_name = db_dosen, 
                                filter          = {'nama': dosen}, 
                                update_data     = {'matkul_ajar': data_dosen['matkul_ajar']}
                            )
                        else:
                            self.connection.update_one(
                                collection_name = db_dosen, 
                                filter          = {'nama': dosen}, 
                                update_data     = {}, 
                                unset_data      = {'matkul_ajar': ""})
                    else:
                        raise Exception
            
            res = self.connection.delete_many(
                collection_name = db_matkul, 
                filter          = { 
                        'kode' : { '$in': list_kode }, 
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