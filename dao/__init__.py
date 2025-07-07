from pymongo import MongoClient, errors
import config
import sys

class Database:
    def __init__(self, dbname):
        try:
            self.connection = MongoClient(config.MONGO_URI)
            self.db = self.connection[dbname]
        except errors.ConnectionFailure as conn_fail:
            print(f"Gagal Membuat Koneksi | {conn_fail}")
        except Exception as err:
            print(f"Gagal membuat koneksi (Others) | {err}")

    # def to_uppercase(self, value):
    #     if isinstance(value, str):
    #         return value.upper()
    #     elif isinstance(value, list):
    #         return [self.to_uppercase(item) for item in value]
    #     elif isinstance(value, dict):
    #         return {key: self.to_uppercase(val) for key, val in value.items()}
    #     else:
    #         return value  # Jika bukan string, list, atau dict, biarkan tetap

    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def find_one(self, collection_name, filter={}):
        try:
            collection = self.get_collection(collection_name)
            result = collection.find_one(filter)
            if result:
                result['_id'] = str(result['_id']) 
                del result['_id']
                return {'status': True, 'data': result, 'message': 'Data ditemukan'}
            return {'status': False, 'data': None, 'message': 'Data tidak ditemukan'}
        except errors.PyMongoError as e:
            return {'status': False, 'data': None, 'message': f'Error pymongo: {e}'}
    
    def find_many(self, collection_name, filter={}, per_page=None, sort=None):
        try:
            collection = self.get_collection(collection_name)
            query_filter = filter
            
            cursor = collection.find(query_filter)
            if sort:
                cursor = cursor.sort(sort)
            
            # Jika per_page None, ambil semua data
            data = [{**doc, '_id': str(doc['_id'])} for doc in cursor]
            for doc in data:
                doc.pop('_id', None)  # Hapus _id jika ada

            total_documents = collection.count_documents(query_filter)

            return {'status': True, 'data': data, 'total_documents': total_documents, 'message': 'Data ditemukan'}
        except errors.PyMongoError as e:
            return {'status': False, 'data': None, 'message': f'Error pymongo: {e}'}

    
    def find_many_page(self, collection_name, filter={}, page=1, per_page=10, sort=None):
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter).skip((page - 1) * per_page).limit(per_page)
            if sort:
                cursor = cursor.sort(sort)
            
            data = [{**doc, '_id': str(doc['_id'])} for doc in cursor]
            for doc in data:
                doc.pop('_id', None)  # Hapus _id, jika ada

            total_documents = collection.count_documents(filter)
            
            return {'status': True, 'data': data, 'total_documents': total_documents, 'message': 'Data ditemukan'}
        except errors.PyMongoError as e:
            return {'status': False, 'data': None, 'message': f'Error pymongo: {e}'}
    
    def insert_one(self, collection_name, data):
        try:
            collection = self.get_collection(collection_name)
            insert_result = collection.insert_one(data)
            return {'status': True, 'data': {'inserted_id': str(insert_result.inserted_id)}, 'message': 'Data berhasil ditambahkan'}
        except errors.PyMongoError as e:
            return {'status': False, 'data': None, 'message': f'Error pymongo: {e}'}
    
    def insert_many(self, collection_name, data):
        try:
            collection = self.get_collection(collection_name)
            insert_result = collection.insert_many(data)
            return {'status': True, 'data': {'inserted_ids': [str(id) for id in insert_result.inserted_ids]}, 'message': 'Data berhasil ditambahkan'}
        except errors.PyMongoError as e:
            return {'status': False, 'data': None, 'message': f'Error pymongo: {e}'}
    
    def update_one(self, collection_name, filter, update_data, unset_data={}):
        try:
            collection = self.get_collection(collection_name)

            update_query = {'$set': update_data}
            if unset_data: update_query['$unset'] = unset_data
            update_result = collection.update_one(filter, update_query)
            # {'$set': update_data if sensitive else self.update_data}
            if update_result.modified_count > 0:
                return {'status': True, 'message': 'Data berhasil diperbarui'}
            return {'status': False, 'message': 'Tidak ada data yang diperbarui'}
        except errors.PyMongoError as e:
            return {'status': False, 'message': f'Error pymongo: {e}'}
        
    def update_many(self, collection_name, filter, update_data, unset_data={}):
        try:
            collection = self.get_collection(collection_name)

            update_query = {'$set': update_data}
            if unset_data: update_query['$unset'] = unset_data
            update_result = collection.update_many(filter, update_query)
            if update_result.modified_count > 0:
                return {'status': True, 'modified_count': update_result.modified_count, 'message': 'Data berhasil diperbarui'}
            return {'status': False, 'modified_count': 0, 'message': 'Tidak ada data yang diperbarui'}
        except errors.PyMongoError as e:
            return {'status': False, 'message': f'Error pymongo: {e}'}
    
    def delete_one(self, collection_name, filter):
        try:
            collection = self.get_collection(collection_name)
            delete_result = collection.delete_one(filter)
            if delete_result.deleted_count > 0:
                return {'status': True, 'message': 'Data berhasil dihapus'}
            return {'status': False, 'message': 'Data tidak ditemukan'}
        except errors.PyMongoError as e:
            return {'status': False, 'message': f'Error pymongo: {e}'}
        
    def delete_many(self, collection_name, filter):
        try:
            collection = self.get_collection(collection_name)
            delete_result = collection.delete_many(filter)
            if delete_result.deleted_count > 0:
                return {'status': True, 'deleted_count': delete_result.deleted_count, 'message': 'Data berhasil dihapus'}
            return {'status': False, 'deleted_count': 0, 'message': 'Tidak ada data yang dihapus'}
        except errors.PyMongoError as e:
            return {'status': False, 'message': f'Error pymongo: {e}'}
    
    def count_documents(self, collection_name, filter={}):
        try:
            collection = self.get_collection(collection_name)
            return {'status': True, 'count': collection.count_documents(filter)}
        except errors.PyMongoError as e:
            return {'status': False, 'count': 0, 'message': f'Error pymongo: {e}'}
    
    # def __del__(self):
    #     self.connection.close()

    def __del__(self):
        if hasattr(self, 'client') and self.client:
            if sys.meta_path is not None:  # Cek kalau Python belum shutdown
                try:
                    self.connection.close()
                except Exception as e:
                    print("[WARNING] Error closing MongoDB connection:", e)