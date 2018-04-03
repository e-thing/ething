

from Resource import Resource
from TableQueryParser import TableQueryParser
import datetime
import time
import re
from dateutil.parser import parse
from ShortId import ShortId
import bson
import os, sys
import pymongo
from Helpers import dict_recursive_update
import csv, cStringIO
from rule.event import TableDataAdded
from base import attr, isBool, isString, isNone, isInteger, READ_ONLY, PRIVATE


@attr('maxLength', validator = isNone() | isInteger(min=1), default = 5000, description="The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature.")
@attr('expireAfter', validator = isNone() | isInteger(min=1), default = None, description="The amount of time (in seconds) after which a records will be automatically removed. Set it to null or 0 to disable this feature.")
@attr('length', default = 0, mode = READ_ONLY, description="The number of records in the table")
@attr('keys', default = {}, mode = READ_ONLY, description="A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. __The default keys ('_id' and 'date' are not listed)__")
@attr('contentModifiedDate', default = datetime.datetime.utcnow(), mode = READ_ONLY, description="Last time the conten of this resource was modified.")
class Table(Resource):

    
    FIELD_VALID_CHAR = 'a-zA-Z0-9_\-'
    VALIDATE_FIELD = '^['+FIELD_VALID_CHAR+']{1,64}$'
    
    reservedKeys = ['_id']
    
    INVALID_FIELD_NONE = 0
    INVALID_FIELD_RENAME = 1
    INVALID_FIELD_SKIP = 2
    INVALID_FIELD_STOP = 4
    
    
    TIMESTAMP = 0
    TIMESTAMP_MS = 1
        
    _parser = None
    
    
    
    # return an object
    @staticmethod
    def docSerialize (doc, date_format = None):
        if '_id' in doc:
            doc['id'] = doc['_id']
            del doc['_id']
        
        if 'date' in doc:
            if date_format == Table.TIMESTAMP:
                doc['date'] = int(time.mktime(doc['date'].timetuple()))
            elif date_format == Table.TIMESTAMP_MS:
                doc['date'] = int(time.mktime(doc['date'].timetuple())) * 1000
            else:
                doc['date'] = doc['date'].isoformat()
        
        return doc
    
    @property
    def collectionName (self):
        return 'tb.%s' % self.id
    
    @property
    def collection (self):
        return self.ething.db[self.collectionName]
    
    def remove (self, removeChildren = False):
        
        # remove all the data from this table
        self.clear()
        
        # remove the resource
        super(Table, self).remove(removeChildren)
        
    
    
    def clear (self):
        
        # remove all the data from this table
        try:
            self.collection.drop()
        except:
            pass
        
        self._length = 0
        self._keys = {}
        self._contentModifiedDate = datetime.datetime.utcnow()
        self.save()
    
    
    # is called regularly
    def checkExpiredData (self):
        
        # remove the expired data in the current table
        expireAfter = self.expireAfter
        if expireAfter is not None:
            expiratedDate = datetime.datetime.utcnow() - datetime.timedelta(0,expireAfter)
            c = self.collection
            cursor = c.find(filter={
                'date' : {
                    '$lt' : expiratedDate
                }
            }, projection={'_id' : True})
            
            idToBeRemoved = []
            for doc in cursor:
                idToBeRemoved.append(doc['_id'])
            
            if len(idToBeRemoved)>0:
                self.remove_rows(idToBeRemoved)
    
    
    
    def updateMeta (self):
        
        keys = {}
        length = 0
        
        c = self.collection
        cursor = c.find(projection={
                '_id' : 0,
                'date' : 0
        })
        
        for doc in cursor:
            for k in doc:
                if k not in keys:
                    keys[k]=0
                keys[k] += 1
            length += 1
        
        self._length = length
        self._keys = keys
        self.save()
    
    
    def repair (self):
        self.updateMeta()
    
    
    # return the number of document removed
    def remove_rows (self, row_ids):
        
        nb = 0
        
        c = self.collection
        
        keys = self.keys
        
        for row_id in row_ids:
            
            try:
                removedDoc = c.find_one_and_delete({
                    '_id' : row_id
                })
            
                # update the key count
                if removedDoc:
                    for field in removedDoc:
                        if field in keys:
                            keys[field]-=1
                            if keys[field]<=0:
                                del keys[field]
                    
                    nb+=1
                
            
            except:
                pass # invalid id or unable to remove the document
        
        
        if nb>0 :
            self._length = self.length - nb
            self.setDirtyAttr('keys')
            self._contentModifiedDate = datetime.datetime.utcnow()
            self.save()
        
        
        return nb
    
    
    def remove_row (self, row_id):
        return self.remove_rows([row_id]) > 0;
    
    
    @staticmethod
    def sanitizeData (dataArray, keys = None, invalidFields = INVALID_FIELD_RENAME, skipError = True, setDate = True):
        
        if isinstance(invalidFields, basestring):
            if invalidFields == "stop":
                invalidFields = Table.INVALID_FIELD_STOP
            elif invalidFields == "none":
                invalidFields = Table.INVALID_FIELD_NONE
            elif invalidFields == "skip":
                invalidFields = Table.INVALID_FIELD_SKIP
            else:
                invalidFields = Table.INVALID_FIELD_RENAME
        
        if keys is None:
            keys = {}
        
        length = 0
        
        reValidField = re.compile(Table.VALIDATE_FIELD)
        reRenameField = re.compile('[^'+Table.FIELD_VALID_CHAR+']+')
        
        i=0
        while i<len(dataArray):
            data = dataArray[i]
            
            try:
                
                if not isinstance(data, dict):
                    raise Exception('invalid data')
                                
                # key/field validation
                if 'id' in data:
                    del data['id']; # will be auto generated !
                
                for k in data:
                    v = data[k]
                    
                    if not(isinstance(v,int) or isinstance(v,float) or isinstance(v,basestring) or isinstance(v,bool) or v is None):
                        raise Exception('The value must either be a string or a number or a boolean or null.')
                    
                    
                    if not reValidField.search(k):
                            
                        if invalidFields == Table.INVALID_FIELD_SKIP:
                            del data[k]
                        
                        elif invalidFields == Table.INVALID_FIELD_RENAME:
                            del data[k]
                            k = reRenameField.sub('_',k) if len(k) else '_'
                            data[k] = v
                            
                        else:
                            raise Exception('invalid key "%s", must only contain alphanumeric, underscore or dashes characters. Keys must not be empty' % k)
                    
                    
                    if k in Table.reservedKeys:
                        
                        if invalidFields == Table.INVALID_FIELD_SKIP:
                            del data[k]
                        
                        elif invalidFields == Table.INVALID_FIELD_RENAME:
                            del data[k]
                            k = k + '_'
                            data[k] = v
                            
                        else:
                            raise Exception('invalid key "%s", must not be one of the following values' % (k,",".join(Table.reservedKeys)))
                    
                    
                    if(k=='date'):
                        # check the format
                        try:
                            data[k] = parse(v)
                        except:
                            raise Exception('Invalid date "%s"' % v)
                
                
                # update the key count
                for k in data:
                    if k != 'date':
                        if k not in keys:
                            keys[k] = 0
                        keys[k]+=1
                
                
                # add date if not already set
                if setDate and 'date' not in data:
                    data['date'] = datetime.datetime.utcnow() # add the insertion date for that document
                
                
                length+=1
                
            
            except:
                if skipError:
                    del dataArray[i]
                    i -= 1
                else:
                    raise Exception(sys.exc_info()[1])
                
            i += 1
        
        
        return length
    
    
    def insert (self, data, invalidFields = INVALID_FIELD_RENAME):
        if data:
            
            keys = self.keys
            length = self.length
            maxLength = self.maxLength
            
            # sanitize the incoming data
            dataArray = [data]
            length += Table.sanitizeData(dataArray,keys,invalidFields,False)
            
            # add meta data
            for d in dataArray:
                d['_id'] = ShortId.generate()
            
            
            # insert the data
            c = self.collection
            c.insert_one(dataArray[0])
            # remove extra row
            if maxLength and length > maxLength :
                
                # remove the oldest document
                removedDoc = c.find_one_and_delete({}, sort=[('date',pymongo.ASCENDING)])
                
                length-=1
                
                # update the key count
                for field in removedDoc:
                    if field in keys:
                        keys[field]-=1
                        if keys[field]<=0:
                            del keys[field]
            
            
            self._length = length
            self.setDirtyAttr('keys')
            self._contentModifiedDate = datetime.datetime.utcnow()
            self.save()
            
            doc = Table.docSerialize(dataArray[0])
            # generate an event
            self.dispatchSignal(TableDataAdded.emit(self, doc))
            # mqtt publish
            #self.ething.mqttPublish("resource/table/%s/data" % self.id, doc, True)
            
            return doc
        
        
        return False
    
    
    
    def importData(self, dataArray = [], invalidFields = INVALID_FIELD_RENAME, skipError = True):
        
        maxLength = self.maxLength
        
        # remove extra row
        if( maxLength and len(dataArray) > maxLength ):
            dataArray = dataArray[0:maxLength]
        
        
        # remove any previous content
        self.clear()
        
        # sanitize the incoming data
        keys = {}
        length = Table.sanitizeData(dataArray,keys,invalidFields,skipError)
        
        if dataArray:
            # add meta data
            for d in dataArray:
                d['_id'] = ShortId.generate()
            
            
            # insert the data
            c = self.collection
            c.insert_many(dataArray, ordered = False)
        
        
        self._keys = keys
        self._length = length
        
        self.save()
        
        return True
    
    
    # no sanitize is made, internal purpose only
    def __importRaw (self, dataArray, keys):
        if not dataArray:
            return True
        
        maxLength = self.maxLength
        
        # remove extra row
        if( maxLength and len(dataArray) > maxLength ):
            dataArray = dataArray[0:maxLength]
        
        
        # remove any previous content
        self.clear()
        
        # add meta data
        for d in dataArray:
            d['_id'] = ShortId.generate()
        
        
        # insert the data
        c = self.collection
        c.insert_many(dataArray, ordered = False)
        
        # update the metadata
        self._length = len(dataArray)
        keys_ = self.keys
        
        for k in keys:
            if k not in keys_:
                keys_[k] = 0
            keys_[k] += keys[k]
        
        self.setDirtyAttr('keys')
        self._contentModifiedDate = datetime.datetime.utcnow()
        self.save()
        
        return True
    
    
    
    def getRow (self, id, fields = None):
        
        # return only specific fields
        _fields = {}
        if fields is not None:
            _fields['_id'] = False; # by default, the '_id' field is shown
            for field in fields:
                # handle special key '_id' 
                if field=='id':
                    _fields['_id'] = True
                elif field not in Table.reservedKeys:
                    _fields[field] = True
        
        c = self.collection
        r = c.find_one({'_id' : id},projection=_fields)
        
        return Table.docSerialize(r) if r is not None else None
    
    
    def replaceRowById (self, row_id, data, invalidFields = INVALID_FIELD_RENAME):
        if data:
            
            keys = self.keys
            
            # sanitize the incoming data
            dataArray = [data]
            Table.sanitizeData(dataArray,keys,invalidFields,False)
            
            # add meta data
            dataArray[0]['_id'] = row_id
            
            # insert the data
            c = self.collection
            original = c.find_one_and_replace({'_id' : row_id}, dataArray[0])
            
            if original is not None:
                for field in original:
                    if field in keys:
                        keys[field]-=1
                        if keys[field]<=0:
                            del keys[field]
                
                self._contentModifiedDate = datetime.datetime.utcnow()
                self.setDirtyAttr('keys')
                self.save()
                
                return Table.docSerialize(dataArray[0])
        
        return False
    
    
    # replace only one row
    def replaceRow (self, query, data, invalidFields = INVALID_FIELD_RENAME, upsert = False):
        if data:
            
            if isinstance(query, basestring):
                # parse the query string
                q = self.parser.parse(query)
            
            elif isinstance(query, dict):
                q = query
            else:
                q = {}
            
            c = self.collection
            
            original = c.find_one(q)
            
            if original is not None:
                # the document was found !
                
                keys = self.keys
                
                # sanitize the incoming data
                dataArray = [data]
                Table.sanitizeData(dataArray,keys,invalidFields,False)
                
                # add meta data
                dataArray[0]['_id'] = original['_id']; # keep the same id !
                
                #replace it !
                c.replace_one({'_id' : original['_id']}, dataArray[0])
                
                for field in original:
                    if field in keys:
                        keys[field]-=1
                        if keys[field]<=0:
                            del keys[field]
                
                self._contentModifiedDate = datetime.datetime.utcnow()
                self.setDirtyAttr('keys')
                self.save()
                
                return Table.docSerialize(dataArray[0])
            else:
                # not found !
                if upsert:
                    return self.insert(data, invalidFields)
        
        return False
    
    @property
    def parser (self):
        if Table._parser is None:
            Table._parser = TableQueryParser()
        return Table._parser
    
    
    def find (self, query = None):
        return self.select(query = query)
    
    
    def select (self, start = 0, length = None, fields = None, sort = None, query = None, date_format = None):
    # If start is non-negative, the returned selection will start at the start'th position in the table, counting from zero.
    # If start is negative, the returned selection will start at the start'th position from the end of the table.
    # If length is given and is positive, the selection returned will contain at most length lines beginning from start.
    # If length is omitted, the selection starting from start until the end of the table will be returned.
    # length >= 0
        
        c = self.collection
        
        if isinstance(date_format, basestring):
            date_format = date_format.lower()
            if date_format == "timestamp":
                date_format = Table.TIMESTAMP
            elif date_format == "timestamp_ms":
                date_format = Table.TIMESTAMP_MS
            else:
                date_format = None
        
        
        if isinstance(query, basestring):
            # parse the query string
            q = self.parser.parse(query)
        
        elif isinstance(query, dict):
            q = query
        else:
            q = {}
        
        opt = {
            'sort': [('date',pymongo.ASCENDING)], # always sort by date
            'skip': 0,
            'limit': 0,
            'projection': None
        }
        
        # sort
        if isinstance(sort, basestring):
            opt['sort'] = []
            parts = sort.split(',')
            for p in parts:
                m = re.search('^([+-]?)(.+)$',p)
                if m is not None:
                    sortField=m.group(2)
                    sortAsc=pymongo.ASCENDING if m.group(1)!='-' else pymongo.DESCENDING
                    opt['sort'].append((sortField,sortAsc))
            if not opt['sort']:
                opt['sort'] = None
        elif isinstance(sort, list):
            opt['sort'] = sort
        
        
        # define the start point and the length of the returning set
        if start<0:
            start = self.length + start
            if start < 0:
                if length is not None:
                    length+=start
                start = 0
            
        
        opt['skip'] = start
        if length is not None:
            opt['limit'] = length
        
        
        # return only specific fields
        if fields is not None:
            _fields = {}
            _fields['_id'] = False; # by default, the '_id' field is shown
            for field in fields:
                # handle special key '_id' 
                if field=='id':
                    _fields['_id'] = True
                elif field not in Table.reservedKeys:
                    _fields[field] = True
            opt['projection'] = _fields
        
        cursor = c.find(q, projection=opt['projection'], skip=opt['skip'], limit=opt['limit'], sort=opt['sort'])
        
        
        # iterate
        items = []
        for doc in cursor:
            items.append(Table.docSerialize(doc, date_format))
        
        return items
    
    
    
    def computeStatistics (self, key, query = None):
        
        
        map = bson.code.Code(open(os.path.join(os.path.dirname(__file__), './mongodb/statistics/map.js')).read(1000).replace('<KEY>',key))
        reduce = bson.code.Code(open(os.path.join(os.path.dirname(__file__), './mongodb/statistics/reduce.js')).read(1000))
        finalize = bson.code.Code(open(os.path.join(os.path.dirname(__file__), './mongodb/statistics/finalize.js')).read(1000))
        
        queries = []
        queries.append({
            key : {'$exists' : True}
        })
        
        if isinstance(query, basestring):
            # parse the query string
            queries.append(self.parser.parse(query))
        
        elif isinstance(query, dict):
            queries.append(query)
        
        out = {}
        
        res = self.collection.map_reduce(map, reduce, {
            'inline': 1
        }, query={
                '$and' : queries
            }, finalize=finalize, full_response=True)
        
        if res['ok'] and len(res['results'])>0:
            return self.ething.r_encode(res['results'][0]['value'])

        return False
    
    
    def writeCSV(self, show_header = True, **kwargs):
        
        content = ''
        selection = self.select(**kwargs)
        
        if len(selection)>0:
            keys = ['id', 'date'] + self.keys.keys()
            buffer = cStringIO.StringIO()
            csvw = csv.DictWriter(buffer, keys, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if show_header:
                csvw.writeheader()
            csvw.writerows(selection)
            content = buffer.getvalue()
            buffer.close()
        
        return content
    
    

    
if __name__ == '__main__':
    
    from ething.core import Core
    
    ething = Core({
        'db':{
            'database': 'test'
        },
        'log':{
            'level': 'debug'
        }
    })
    
    def testCreate():
        f = ething.create('Table', {
            'name' : 'file1.txt'
        })
        
        f.importData([{
            "a":1,
            "b": False,
            "c": 4.5,
            "d": "string"
        },{
            "a":2
        },{
            "a":3
        }])
        
        print f.toJson()
        
        print f.length
        
        print f.select()
        
        print f.computeStatistics('a')
    
    def testPrint():
        f = ething.findOne({ 'type': 'Table' })
        
        print f.name
        
        print f.length
        
        print f.select()
        
        print f.writeCSV()
    
    def testQuery():
        
        name = 'table_test_query.bd'
        
        f = ething.findOne({"name": name})
        
        #if f:
        #    f.insert({"a": 6})
        #    return
        
        if not f:
            f = ething.create('Table', {
                'name' : name
            })
            
            f.importData([{
                "a":1
            },{
                "a":2
            },{
                "a":3
            },{
                "a":4
            },{
                "a":5
            }])
        
        print len(f.select())
        print len(f.select( query = u'a>3'))
        print len(f.select( query = u'date> "30 minutes ago" '))
        
        
        
    
    #testCreate()
    #testPrint()
    testQuery()
    


