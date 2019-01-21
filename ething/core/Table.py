# coding: utf-8
from future.utils import string_types, integer_types
from .Resource import Resource, ResourceType
from .date import TzDate, utcnow, utcfromtimestamp
from .entity import *
from .Signal import ResourceSignal
from .TableQueryParser import TableQueryParser
from .query import attribute_compiler
from .Helpers import filter_obj
from .utils import object_sort
from .Flow import ResourceActionNode
import datetime
import time
import re
from dateutil.parser import parse
from .ShortId import ShortId
import csv
import sys
import pytz
import math

if (sys.version_info > (3, 0)):
    from io import StringIO
else:
    # cf: https://stackoverflow.com/questions/13120127/how-can-i-use-io-stringio-with-the-csv-module
    from StringIO import StringIO


number_types = integer_types + (float, )


@meta(icon='mdi-table-row-plus-after')
class TableDataAdded(ResourceSignal):
    """
    is emitted each time a new value is appended to a table
    """
    def __init__(self, resource, data):
        super(TableDataAdded, self).__init__(resource)
        self.data = data


@meta(icon='mdi-table-row-plus-after')
@attr('resource', type=ResourceType(accepted_types=('resources/Table',)))
class AppendData(ResourceActionNode):
    def run(self, msg, core):
        table = core.get(self.resource)

        if table is None:
            raise Exception("the table has been removed")

        data = {}
        payload = msg.payload
        for k in payload:
            v = payload[k]
            if isinstance(v, number_types) or isinstance(v, string_types) or isinstance(v, bool) or v is None:
                data[k] = v

        if data:
            table.insert(data)


@throw(TableDataAdded)
@attr('maxLength', type=Nullable(Integer(min=1)), default=5000, description="The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature.")
@attr('expireAfter', type=Nullable(Integer(min=1)), default=None, description="The amount of time (in seconds) after which a records will be automatically removed. Set it to null or 0 to disable this feature.")
@attr('length', default=0, mode=READ_ONLY, description="The number of records in the table")
@attr('keys', type=Dict(), default={}, mode=READ_ONLY, description="A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. __The default keys ('id' and 'date' are not listed)__")
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this table was modified.")
class Table(Resource):

    FIELD_VALID_CHAR = 'a-zA-Z0-9_\-'
    VALIDATE_FIELD = '^['+FIELD_VALID_CHAR+']{1,64}$'

    reservedKeys = ['_id'] # mongodb reserved key

    INVALID_FIELD_NONE = 0
    INVALID_FIELD_RENAME = 1
    INVALID_FIELD_SKIP = 2
    INVALID_FIELD_STOP = 4

    TIMESTAMP = 0
    TIMESTAMP_MS = 1

    # return an object
    def docSerialize(self, doc, date_format=None):

        if 'date' in doc:
            dt = doc['date']
            if date_format == Table.TIMESTAMP:
                doc['date'] = int(time.mktime(dt.timetuple()))
            elif date_format == Table.TIMESTAMP_MS:
                doc['date'] = int(time.mktime(dt.timetuple())) * 1000
            else:
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.utc)
                doc['date'] = dt.astimezone(self.ething.local_tz).isoformat()

        return doc

    @property
    def collectionName(self):
        return 'tb.%s' % self.id

    @property
    def db(self):
        return self.ething.db

    def _insert(self):
        super(Table, self)._insert()
        self.db.create_table(self.collectionName)

    def remove(self, removeChildren=False):

        # remove all the data from this table
        self.db.remove_table(self.collectionName)

        # remove the resource
        super(Table, self).remove(removeChildren)

    def clear(self):
        with self:
            # remove all the data from this table
            self.db.remove_table(self.collectionName)
            self.db.create_table(self.collectionName)

            self.length = 0
            self.keys = {}
            self.contentModifiedDate = utcnow()

    # is called regularly

    def checkExpiredData(self):

        with self:
            # remove the expired data in the current table
            expireAfter = self.expireAfter
            if expireAfter is not None:
                expiratedDate = utcnow() - datetime.timedelta(0, expireAfter)

                rows_to_be_removed = self.select(query='date < "%s"' % expiratedDate.isoformat())
                removed_rows = self.db.remove_table_rows_by_id(self.collectionName, [row.get('id') for row in rows_to_be_removed], return_old=True)

                self._update_meta(removed_rows = removed_rows)

    def _update_meta(self, removed_rows = None, added_rows = None, reset = False):

        if removed_rows is not None:
            keys = self.keys
            nb = 0

            for row in removed_rows:
                # update the key count
                for field in row:
                    if field in keys:
                        keys[field] -= 1
                        if keys[field] <= 0:
                            del keys[field]

                nb += 1

            if nb > 0:
                self.length = self.length - nb

        if added_rows is not None:
            keys = self.keys
            nb = 0

            for row in added_rows:
                # update the key count
                for field in row:
                    if field == 'id' or field == 'date':
                        continue
                    if field not in keys:
                        keys[field] = 0
                    keys[field] += 1

                nb += 1

            if nb > 0:
                self.length = self.length + nb

        if reset is True:
            """
            compute the length and list the keys (except the id and date keys)
            {
                length: int,
                keys: { key: number }
            }
            """
            keys = {}
            length = 0

            for row in self.db.get_table_rows(self.collectionName):
                for k in row:
                    if k not in keys:
                        keys[k] = 0
                    keys[k] += 1
                length += 1

            keys.pop('id', None)
            keys.pop('date', None)

            self.length = length
            self.keys = keys
            self.data = {}

        self.contentModifiedDate = utcnow()

    def updateMeta(self):
        with self:
            self._update_meta(reset = True)

    def repair(self):
        self.updateMeta()


    # return the number of document removed
    def remove_rows(self, row_ids):
        with self:

            removed_rows = self.db.remove_table_rows_by_id(self.collectionName, row_ids, True)
            self._update_meta(removed_rows=removed_rows)
            return len(removed_rows)

    def remove_row(self, row_id):
        return self.remove_rows([row_id]) > 0

    def sanitizeData(self, dataArray, invalidFields=INVALID_FIELD_RENAME, skipError=True):

        if isinstance(invalidFields, string_types):
            if invalidFields == "stop":
                invalidFields = Table.INVALID_FIELD_STOP
            elif invalidFields == "none":
                invalidFields = Table.INVALID_FIELD_NONE
            elif invalidFields == "skip":
                invalidFields = Table.INVALID_FIELD_SKIP
            else:
                invalidFields = Table.INVALID_FIELD_RENAME

        length = 0

        reValidField = re.compile(Table.VALIDATE_FIELD)
        reRenameField = re.compile('[^'+Table.FIELD_VALID_CHAR+']+')

        i = 0
        while i < len(dataArray):
            data = dataArray[i]

            try:

                if not isinstance(data, dict):
                    raise Exception('invalid data: [%s] %s' % (
                        type(data).__name__, str(data)))

                # key/field validation
                if 'id' in data:
                    del data['id']  # will be auto generated !

                for k in data:
                    v = data[k]

                    is_number = isinstance(v, number_types)

                    if not(is_number or isinstance(v, string_types) or isinstance(v, bool) or v is None):
                        raise Exception(
                            'The value must either be a string or a number or a boolean or null.')

                    if not reValidField.search(k):

                        if invalidFields == Table.INVALID_FIELD_SKIP:
                            del data[k]

                        elif invalidFields == Table.INVALID_FIELD_RENAME:
                            del data[k]
                            k = reRenameField.sub('_', k) if len(k) else '_'
                            data[k] = v

                        else:
                            raise Exception(
                                'invalid key "%s", must only contain alphanumeric, underscore or dashes characters. Keys must not be empty' % k)

                    if k in Table.reservedKeys:

                        if invalidFields == Table.INVALID_FIELD_SKIP:
                            del data[k]

                        elif invalidFields == Table.INVALID_FIELD_RENAME:
                            del data[k]
                            k = k + '_'
                            data[k] = v

                        else:
                            raise Exception('invalid key "%s", must not be one of the following values: %s' % (
                                k, ",".join(Table.reservedKeys)))

                    if k == 'date':
                        # check the format
                        try:
                            if is_number:
                                data[k] = utcfromtimestamp(v) # UTC
                            elif isinstance(v, string_types):
                                data[k] = parse(v)

                            if data[k].tzinfo is None:
                                # naive datetime
                                data[k] = self.ething.local_tz.localize(data[k]).astimezone(pytz.utc)
                            else:
                                # make it UTC
                                data[k] = data[k].astimezone(pytz.utc)
                        except:
                            raise Exception('Invalid date "%s"' % v)

                # add date if not already set
                if 'date' not in data:
                    # add the insertion date for that document
                    data['date'] = utcnow() # UTC

                data['id'] = ShortId.generate()

                length += 1

            except:
                if skipError:
                    del dataArray[i]
                    i -= 1
                else:
                    raise

            i += 1

        return length

    def insert(self, data, invalidFields=INVALID_FIELD_RENAME):
        if data:
            with self:

                # sanitize the incoming data
                dataArray = [data]
                l = self.sanitizeData(dataArray, invalidFields, False)

                if l > 0:

                    # insert the data
                    self.db.insert_table_row(self.collectionName, dataArray[0])

                    self._update_meta(added_rows = dataArray)

                    self.data = dataArray[0]

                    # remove extra rows
                    length = self.length
                    maxLength = self.maxLength
                    if maxLength and length > maxLength:
                        remove_length = length - maxLength

                        # remove extra rows
                        rows_to_be_removed = self.db.get_table_rows(self.collectionName, sort = [('date', True)], length = remove_length)
                        self.remove_rows([r['id'] for r in rows_to_be_removed])

                    doc = self.docSerialize(dataArray[0])
                    # generate an event
                    self.dispatchSignal(TableDataAdded(self, doc))

                    return doc

        return False

    def importData(self, dataArray, invalidFields=INVALID_FIELD_RENAME, skipError=True):

        with self:
            maxLength = self.maxLength

            # remove extra row
            if maxLength and len(dataArray) > maxLength:
                dataArray = dataArray[0:maxLength]

            # remove any previous content
            self.clear()

            # sanitize the incoming data
            length = self.sanitizeData(dataArray, invalidFields, skipError)

            if length > 0:
                # insert the data
                self.db.insert_table_rows(self.collectionName, dataArray)
                self._update_meta(added_rows=dataArray)
                self.data = dataArray[-1]

        return True

    def getRow(self, id):
        r = self.db.get_table_row_by_id(self.collectionName, id)
        return self.docSerialize(r) if r is not None else None

    def replaceRowById(self, row_id, data, invalidFields=INVALID_FIELD_RENAME):
        if data:
            with self:

                # sanitize the incoming data
                dataArray = [data]
                l = self.sanitizeData(dataArray, invalidFields, False)

                if l > 0:
                    new_row = dataArray[0]
                    # copy id
                    new_row['id'] = row_id

                    # insert the data
                    old_row = self.db.update_table_row(self.collectionName, new_row, True)

                    if old_row:
                        self._update_meta(removed_rows=[old_row], added_rows=[new_row])
                        return self.docSerialize(new_row)

        return False

    # replace only one row
    def replaceRow(self, query, data, invalidFields=INVALID_FIELD_RENAME, upsert=False):
        if data:
            with self:

                rows = self.select(query = query, length = 1)

                if len(rows) > 0:
                    row = rows[0]

                    return self.replaceRowById(row['id'], data, invalidFields)
                else:
                    # not found !
                    if upsert:
                        return self.insert(data, invalidFields)

        return False

    def select(self, start=0, length=None, fields=None, sort=None, query=None, date_format=None):
        # If start is non-negative, the returned selection will start at the start'th position in the table, counting from zero.
        # If start is negative, the returned selection will start at the start'th position from the end of the table.
        # If length is given and is positive, the selection returned will contain at most length lines beginning from start.
        # If length is omitted, the selection starting from start until the end of the table will be returned.
        # length >= 0

        if sort is None:
            # always sort by date
            sort = [('date', True)]

        if isinstance(sort, string_types):
            parts = sort.split(',')
            sort = []
            for p in parts:
                m = re.search('^([+-]?)(.+)$', p)
                if m is not None:
                    sortField = m.group(2)
                    sortAsc = bool(m.group(1) != '-')
                    sort.append((sortField, sortAsc))
            if not sort:
                sort = None

        # define the start point and the length of the returning set
        if start < 0:
            start = self.length + start
            if start < 0:
                if length is not None:
                    length += start
                start = 0

        if isinstance(date_format, string_types):
            date_format = date_format.lower()
            if date_format == "timestamp":
                date_format = Table.TIMESTAMP
            elif date_format == "timestamp_ms":
                date_format = Table.TIMESTAMP_MS
            else:
                date_format = None

        if not query:
            # let the sorting/offset/limit by the DB driver
            rows = self.db.get_table_rows(self.collectionName, sort = sort, start = start, length = length, keys = fields)
        else:
            # retrieve all the data
            rows = self.db.get_table_rows(self.collectionName)

            # apply the filter according to the query string
            parser = TableQueryParser(compiler=attribute_compiler, tz=getattr(self, 'tz', None))
            filter_fn = parser.compile(query)
            rows = [row for row in rows if filter_fn(row)]

            if sort:
                sort_attr = sort[0][0]
                asc = sort[0][1]
                rows = object_sort(rows, key=lambda doc: doc.get(sort_attr, None), reverse=not asc)

            if start or length:
                start = start or 0
                rows = rows[start:(length + start if length is not None else None)]

            if fields is not None:
                rows = [filter_obj(row, fields) for row in rows]

        return [self.docSerialize(row, date_format) for row in rows]

    def computeStatistics(self, key, query=None):

        sum = 0
        sum2 = 0
        min = None
        min_date = None
        min_id = None
        max = None
        max_date = None
        max_id = None
        count = 0
        start_date = None
        end_date = None
        n = 0
        avg = None
        variance = None
        stddev = None

        for row in self.select(query=query):
            count += 1
            value = row[key]
            date = row['date']
            id = row['id']

            if start_date is None or date < start_date:
                start_date = date

            if end_date is None or date > end_date:
                end_date = date

            if isinstance(value, number_types):
                n += 1
                sum += value
                sum2 += value * value

                if min is None or value < min:
                    min = value
                    min_date = date
                    min_id = id

                if max is None or value > max:
                    max = value
                    max_date = date
                    max_id = id

        if n > 0:
            avg = sum / n
            variance = (sum2 / n) - avg
            stddev = math.sqrt(variance)

        return {
            'min': min,
            'min_date': min_date,
            'min_id': min_id,
            'max': max,
            'max_date': max_date,
            'max_id': max_id,
            'count': count,
            'start_date': start_date,
            'end_date': end_date,
            'avg': avg,
            'variance': variance,
            'stddev': stddev,
        }

    def writeCSV(self, show_header=True, **kwargs):

        content = ''
        selection = self.select(**kwargs)

        if len(selection) > 0:
            keys = [u'id', u'date'] + list(self.keys)
            buffer = StringIO()
            csvw = csv.DictWriter(
                buffer, keys, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if show_header:
                csvw.writeheader()
            csvw.writerows(selection)
            content = buffer.getvalue()
            buffer.close()

        return content

    def export_instance(self):
        s = super(Table, self).export_instance()
        d = self.select()
        return {
            'object': s,
            'content': d
        }

    @classmethod
    def import_instance(cls, data, context = None):
        instance = super(Table, cls).import_instance(data.get('object'), context)
        instance.importData(data.get('content'))
        return instance

