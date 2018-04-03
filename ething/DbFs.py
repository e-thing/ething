


# gridfs helpers

import gridfs

class DbFs(object):

    
    def __init__ (self, db):
        
        self.db = db
        
    
    
    def storeFile (self, filename, contents, metadata = None):
        if contents:
            bucket = gridfs.GridFSBucket(self.db)
            
            grid_in = bucket.open_upload_stream(filename, metadata=metadata)
            
            grid_in.write(contents)
            grid_in.close()
            
            return grid_in._id
        
        return None
    
    
    def retrieveFile (self, id):
        if id:
            bucket = gridfs.GridFSBucket(self.db)
            try :
                grid_out = bucket.open_download_stream(id)
                return grid_out.read()
            except gridfs.errors.NoFile:
                pass
        
        return None
    
    
    def removeFile (self, id):
        if id:
            bucket = gridfs.GridFSBucket(self.db)
            try :
                bucket.delete(id)
            except gridfs.errors.NoFile:
                pass
        
    
    
    def getFileMetadata (self, id):
        metadata = {}
        
        if id:
            fs = gridfs.GridFS(self.db)
            file = fs.find_one(id)
            if file is not None:
                metadata = file.metadata
        
        return metadata
    
    
    def getFileSize (self, id):
        if id:
            fs = gridfs.GridFS(self.db)
            file = fs.find_one(id)
            if file is not None:
                return file.length    
        
        return 0
    
    
    def listFiles (self):
        fs = gridfs.GridFS(self.db)
        return fs.list()
    
    
if __name__ == "__main__":
    
    import pymongo
    
    mongoClient = pymongo.MongoClient()
    
    dbfs = DbFs(mongoClient.test_fs_database)
    id = dbfs.storeFile('file1.txt', 'content of file1', {
        'attr' : 'attrvalue'
    })
    
    print dbfs.getFileMetadata(id)
    print dbfs.getFileSize(id)
    print dbfs.retrieveFile(id)
    
    print dbfs.listFiles()
    
    dbfs.removeFile(id)


