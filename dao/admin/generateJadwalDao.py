from dao import Database
from config import MONGO_DB, MONGO_LECTURERS_COLLECTION as db_dosen, MONGO_OPEN_COURSES_COLLECTION as db_matkul_simpanan, MONGO_CLASSES_COLLECTION as db_kelas
from config import MONGO_SCHEDULE_COLLECTION as db_jadwal
from flask import session
from dao.kaprodi.dataMataKuliahDao import dataMataKuliahDao
from global_func import CustomError

dao_matkul = dataMataKuliahDao()

class generateJadwalDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_dosen(self):
        print(f"{'[ DAO ]':<25} Get Dosen")
        result = self.connection.find_many(
            collection_name = db_dosen,
            filter          = {
                'status': { '$ne': 'TIDAK_AKTIF' }
            }
        )
        return result['data'] if result and result.get('status') else []
    
    def get_simpanan_prodi(self, list_prodi: list = []):
        print(f"{'[ DAO ]':<25} Get Simpanan Prodi")
        data_simpanan = self.connection.find_many(
            collection_name = db_matkul_simpanan, 
            filter          = {
                    'u_id': { 
                        "$regex": "^" + (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan']).upper() 
                    }
                }
        )
        prodi_done = [data["u_id"].split('_')[2] for data in data_simpanan["data"]] if data_simpanan and data_simpanan.get('status') else []
        final_data = []
        for prodi in list_prodi:
            final_data.append({
                "prodi" : prodi, 
                "status": True if (prodi.split()[0] + ''.join(hrf[0] for hrf in prodi.split()[1:])) in prodi_done else False
            })
        return sorted(final_data, key=lambda x: x["status"], reverse=True)
        # return {k: True if (k.split()[0] + ''.join(hrf[0] for hrf in k.split()[1:])) in prodi_done else False for k in list_prodi}
    
    def get_open_matkul(self):
        print(f"{'[ DAO ]':<25} Get Matkul")
        result = self.connection.find_many(
            collection_name = db_matkul_simpanan, 
            filter          = {
                    'u_id': { 
                        "$regex": "^" + (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan']).upper() 
                    }
                }
        )
        list_matkul = []
        if result and result.get('status'):
            resultData = [data for data in result['data']] # [ [{}], [{}] ]
            list_kode_matkul = []
            for dt in resultData:
                list_kode_matkul.extend([matkul['kode'] for matkul in dt['list_matkul']])

            list_matkul = dao_matkul.get_matkul_by_kode(list_kode_matkul)
            for matkul in list_matkul:
                for data in resultData:
                    jumlah_kelas = next((data['jumlah_kelas'] for data in data['list_matkul'] if data['kode'] == matkul['kode']), None)
                    if jumlah_kelas:
                        matkul['jumlah_kelas'] = int(jumlah_kelas)
                    matkul['jumlah_mahasiswa'] = data['jumlah_mahasiswa']
            dt['list_matkul'] = [matkul for matkul in list_matkul]
        return list_matkul
    
    def get_kelas(self):
        print(f"{'[ DAO ]':<25} Get kelas")
        result = self.connection.find_many(
            collection_name = db_kelas
        )
        return result['data'] if result and result.get('status') else []

    def get_jadwal(self):
        print(f"{'[ DAO ]':<25} Get jadwal")
        u_id = str(session['academic_details']['semester_depan']) + "_" + str(session['academic_details']['tahun_ajaran_berikutnya']).replace("/", "-")
        result = self.connection.find_one(
            collection_name = db_jadwal, 
            filter          = {'u_id': u_id}
        )
        return result['data'] if result and result.get('status') else []
    
    def upload_jadwal(self, jadwal):
        print(f"{'[ DAO ]':<25} Upload Jadwal")
        result = { 'status': False }

        try:
            if session['user']['role'] == "ADMIN":
                u_id = str(session['academic_details']['semester_depan']) + "_" + str(session['academic_details']['tahun_ajaran_berikutnya']).replace("/", "-")
                res = self.connection.find_one(
                    collection_name = db_jadwal, 
                    filter          = {'u_id': u_id}
                )
                data = {
                    "u_id": u_id,
                    "jadwal": jadwal
                }
                if (res['status'] == True):
                    res = self.connection.update_one(
                        collection_name = db_jadwal, 
                        filter          = {'u_id': data['u_id']}, 
                        update_data     = data
                    )

                    if res['status'] == True:
                        result.update({ 'message': 'Jadwal untuk semester ' + session['academic_details']['semester_depan'] + ' tahun ajaran ' + session['academic_details']['tahun_ajaran_berikutnya'] + ' berhasil diperbaharui!' })
                    else:
                        raise CustomError({ 'message': res['message'] })
                else:
                    res = self.connection.insert_one(
                        collection_name = db_jadwal, 
                        data            = data
                    )

                    if res['status'] == True:
                        result.update({ 'message': 'Jadwal untuk semester ' + session['academic_details']['semester_depan'] + ' tahun ajaran ' + session['academic_details']['tahun_ajaran_berikutnya'] + ' berhasil ditambahkan!' })
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