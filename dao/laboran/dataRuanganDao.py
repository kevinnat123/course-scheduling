from dao import Database
from config import MONGO_DB, MONGO_CLASSES_COLLECTION as db_kelas
from flask import session
import copy

from global_func import CustomError

# PRAKTIKUM_RELATED = ['os', 'processor', 'ram', 'storage']

class dataRuanganDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_kelas(self):
        print(f"{'[ DAO ]':<25} Get Kelas")
        if session['user']['role'] in ["ADMIN", "LABORAN"]:
            result = self.connection.find_many(
                collection_name = db_kelas, 
                sort            = [ ("kode", 1) ]
            )
            for kelas in result['data']:
                toCheck = copy.deepcopy(session['user']['list_prodi'])
                toCheck.extend(["GENERAL"])
                if kelas.get("plot") and kelas["plot"][0] in toCheck:
                    kelas["prodi"] = kelas["plot"].pop(0) # pop index ke 0
        return result['data'] if result and result.get('status') else []

    def post_kelas(self, params):
        print(f"{'[ DAO ]':<25} Post Kelas (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Ruangan belum diisi!' })
            elif not params.get('tipe_ruangan'):
                raise CustomError({ 'message': 'Tipe Ruangan belum diisi!' })
            elif not params.get('kapasitas'):
                raise CustomError({ 'message': 'Kapasitas Ruangan belum diisi!' })
            
            isExist = self.connection.find_one(
                collection_name = db_kelas, 
                filter          = {'kode': params['kode']}
            )
            if isExist['status'] == True:
                raise CustomError({ 'message': f"Data dengan Kode Ruangan {params['kode']} sudah ada!" })

            if params["prodi"] != "default":
                plot = [params["prodi"]]
                plot.extend(params["plot"])
                params["plot"] = plot
            params.pop("prodi", None)

            # if params['tipe_ruangan'] != "PRAKTIKUM":
            #     for x in PRAKTIKUM_RELATED:
            #         params.pop(x, None)
            params = {k: v for k, v in params.items() if v}

            res = self.connection.insert_one(
                collection_name = db_kelas, 
                data            = params
            )
            if res['status'] == True:
                result.update({ 'status': True, 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def put_kelas(self, params):
        print(f"{'[ DAO ]':<25} Put Kelas (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Ruangan belum diisi!' })
            elif not params.get('tipe_ruangan'):
                raise CustomError({ 'message': 'Tipe Ruangan belum diisi!' })
            elif not params.get('kapasitas'):
                raise CustomError({ 'message': 'Kapasitas Ruangan belum diisi!' })
            
            isExist = self.connection.find_one(
                collection_name = db_kelas, 
                filter          = {'kode': params['kode']}
            )
            if isExist['status'] == False:
                raise CustomError({ 'message': f"Data dengan Kode Ruangan {params['kode']} tidak ada!" })

            if params["prodi"] != "default":
                plot = [params["prodi"]]
                plot.extend(params["plot"])
                params["plot"] = plot
            params.pop("prodi", None)

            unset = {k: "" for k, v in params.items() if not v}
            # if params['tipe_ruangan'] != "PRAKTIKUM":
            #     for x in PRAKTIKUM_RELATED:
            #         params.pop(x, None)
            #         if x not in unset: unset[x] = ""
            params = {k: v for k, v in params.items() if v}

            res = self.connection.update_one(
                collection_name = db_kelas, 
                filter          = {'kode': params['kode']}, 
                update_data     = params, 
                unset_data      = unset
            )
            if res['status'] == True:
                result.update({ 'status': True, 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def delete_kelas(self, params):
        print(f"{'[ DAO ]':<25} Delete Kelas (Params: {params})")
        result = { 'status': False }

        try:
            list_kode = [data["kode"] for data in params]
            
            res = self.connection.delete_many(
                collection_name = db_kelas, 
                filter          = {'kode': { '$in': list_kode }}
            )
            if res['status'] == True:
                result.update({ 'status': True, 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result