# coding: utf-8

from .base import BaseClass
from ..ShortId import ShortId
import pymongo
import gridfs
import re
import bson


class MongoDB(BaseClass):

    def __init__(self, core, **config):
        self.host = 'localhost'
        self.port = 27017
        self.user = None
        self.password = None
        super(MongoDB, self).__init__(core, **config)

    def connect(self):
        server = 'mongodb://' + self.host + ':' + str(self.port)

        mongoClient = pymongo.MongoClient(server, username=self.user, password=self.password, connect=True, serverSelectionTimeoutMS=5)

        info = mongoClient.server_info()

        self.mongoClient = mongoClient
        self.db = mongoClient[self.database]

        if self.db is None:
            raise Exception('unable to connect to the database')

        self.log.info('connected to database: %s' % server)
        self.log.info('mongodb version: %s' % mongoClient.server_info().get('version'))

    def disconnect(self):
        pass

    def get_usage(self):
        # table
        tbinfo = {
            'count': 0,
            'size': 0
        }

        for name in self.list_tables():
            try:
                i = self.db.command('collstats', name)
                tbinfo['count'] += i['count']
                tbinfo['size'] += i['size']
            except:
                pass

        # other
        resource_size = 0
        c = self.db["resources"]
        res = c.aggregate([{
            '$match': {
                "size": {'$exists': True}
            }
        }, {
            '$group': {
                "_id": None,
                "size": {'$sum': '$size'}
            }
        }])

        try:
            result = res.next()
            resource_size = result["size"]
        except:
            pass

        res.close()

        return resource_size + tbinfo['size']

    def clear(self):
        db_name = self.db.name
        db_client = self.db.client
        db_client.drop_database(db_name)
        self.db = db_client[db_name]


    #
    # File System (used for storing images, text ...)
    #

    def storeFile(self, filename, contents, metadata=None):
        if contents:

            bucket = gridfs.GridFSBucket(self.db)

            id = ShortId.generate()

            grid_in = bucket.open_upload_stream_with_id(id, filename, metadata=metadata or {})


            grid_in.write(contents)
            grid_in.close()

            return id

        return None

    def retrieveFile(self, file_id):
        content = None
        if file_id:
            bucket = gridfs.GridFSBucket(self.db)
            try:
                grid_out = bucket.open_download_stream(file_id)
                content = grid_out.read()

            except gridfs.errors.NoFile:
                pass

        return content

    def removeFile(self, file_id):
        if file_id:
            bucket = gridfs.GridFSBucket(self.db)
            try:
                bucket.delete(file_id)
            except gridfs.errors.NoFile:
                pass

    def getFileMetadata(self, file_id):
        metadata = {}

        if file_id:
            fs = gridfs.GridFS(self.db)
            file = fs.find_one(file_id)
            if file is not None:
                metadata = file.metadata

        return metadata

    def getFileSize(self, file_id):
        if file_id:
            fs = gridfs.GridFS(self.db)
            file = fs.find_one(file_id)
            if file is not None:
                return file.length

        return 0

    def listFiles(self):
        fs = gridfs.GridFS(self.db)
        return [{
            'id': str(f._id),
            'filename': f.filename,
            'metadata': getattr(f, 'metadata', {}),
            'size': f.length
        } for f in fs.find()]


    #
    # Table (used for storing data time series)
    #

    def list_tables(self):
        if hasattr(self.db, 'collection_names'):
            return self.db.collection_names(include_system_collections=False)
        else:
            return self.db.list_collection_names()

    def create_table(self, table_name):
        pass

    def remove_table(self, table_name):
        try:
            self.db[table_name].drop()
        except:
            pass

    def get_table_rows(self, table_name, start=0, length=None, keys=None, sort=None):

        c = self.db[table_name]
        q = {}

        opt = {
            'sort': None,
            'skip': 0,
            'limit': 0,
            'projection': None
        }

        # sort
        if sort:
            opt['sort'] = [(s[0] if s[0] != 'id' else '_id', pymongo.ASCENDING if s[1] else pymongo.DESCENDING) for s in sort]

        opt['skip'] = start
        if length is not None:
            opt['limit'] = length

        # return only specific fields
        if keys is not None:
            _fields = {}
            _fields['_id'] = False  # by default, the '_id' field is shown
            for field in keys:
                # handle special key '_id'
                if field == 'id':
                    _fields['_id'] = True
                else:
                    _fields[field] = True
            opt['projection'] = _fields

        cursor = c.find(q, projection=opt['projection'], skip=opt['skip'], limit=opt['limit'], sort=opt['sort'])

        # iterate
        items = []
        for row in cursor:
            row['id'] = row['_id']
            del row['_id']
            items.append(row)

        return items

    def get_table_row_by_id(self, table_name, row_id):
        row = self.db[table_name].find_one({'_id': row_id})
        if row:
            row['id'] = row['_id']
            del row['_id']
            return row

    def insert_table_row(self, table_name, row_data):
        row_data = row_data.copy()
        row_data['_id'] = row_data['id']
        del row_data['id']
        self.db[table_name].insert_one(row_data)

    def insert_table_rows(self, table_name, rows_data):
        for row_data in rows_data:
            row_data['_id'] = row_data['id']
            del row_data['id']
        self.db[table_name].insert_many(rows_data, ordered=False)

    def update_table_row(self, table_name, row_id, row_data, return_old):
        """return the old row"""
        old_row = self.db[table_name].find_one_and_replace({'_id': row_id}, row_data)
        if return_old and old_row:
            old_row['id'] = old_row['_id']
            del old_row['_id']
            return old_row

    def remove_table_row(self, table_name, row_id, return_old):
        """return the removed row"""
        try:
            old_row = self.db[table_name].find_one_and_delete({
                '_id': row_id
            })

            if return_old and old_row:
                old_row['id'] = old_row['_id']
                del old_row['_id']
                return old_row
        except:
            pass  # invalid id or unable to remove the document

    def clear_table(self, table_name):
        self.db.drop_collection(table_name)

