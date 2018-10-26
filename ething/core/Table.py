# coding: utf-8
from future.utils import string_types, integer_types
from .Resource import Resource
from .entity import *
from .rule.event import ResourceEvent, ResourceSignal
import datetime
import time
import re
from dateutil.parser import parse
from .ShortId import ShortId
import csv
import sys
import pytz

if (sys.version_info > (3, 0)):
    from io import StringIO
else:
    # cf: https://stackoverflow.com/questions/13120127/how-can-i-use-io-stringio-with-the-csv-module
    from StringIO import StringIO


class TableDataAdded(ResourceSignal):
    def __init__(self, resource, data):
        super(TableDataAdded, self).__init__(resource)
        self.data = data


class TableDataAddedEvent(ResourceEvent):
    """
    is emitted each time a new value is appended to a table
    """
    signal = TableDataAdded


@attr('repeat', type=Boolean(), default=False, description="If true, the rule will be triggered each time the value match the threshold condition. Else the rule is triggered only the first time the threshold condition is met, then the rule is disabled until the threshold condition is not met.")
@attr('threshold_value', type=Number())
@attr('threshold_mode', type=Enum(('gt', 'ge', 'lt', 'le')))
@attr('key', type=String(allow_empty = False), description="The name of the column in the table")
@attr('last_status', mode=PRIVATE, default=False)
class TableDataThresholdEvent(ResourceEvent):
    """
    is emitted each time a value is appended to a table is over or below a threshold
    """
    signal = TableDataAdded

    def _filter(self, signal, core, rule):
        ret = False

        if super(TableDataThresholdEvent, self)._filter(signal, core, rule):
            key = self.key

            if key in signal.data:
                value = signal.data.get(key)

                if isinstance(value, integer_types) or isinstance(value, float):
                    threshold_mode = self.threshold_mode
                    threshold_value = self.threshold_value

                    if threshold_mode == 'gt':
                        if value > threshold_value:
                            ret = True
                    elif threshold_mode == 'ge':
                        if value >= threshold_value:
                            ret = True
                    elif threshold_mode == 'lt':
                        if value < threshold_value:
                            ret = True
                    elif threshold_mode == 'le':
                        if value <= threshold_value:
                            ret = True

                last_status = self._last_status
                self._last_status = ret

                if not self.repeat and ret and last_status:
                    ret = False

        return ret


@throw(TableDataAdded)
@attr('maxLength', type=Nullable(Integer(min=1)), default=5000, description="The maximum of records allowed in this table. When this number is reached, the oldest records will be removed to insert the new ones (first in, first out). Set it to null or 0 to disable this feature.")
@attr('expireAfter', type=Nullable(Integer(min=1)), default=None, description="The amount of time (in seconds) after which a records will be automatically removed. Set it to null or 0 to disable this feature.")
@attr('length', default=0, mode=READ_ONLY, description="The number of records in the table")
@attr('keys', type=Dict(), default={}, mode=READ_ONLY, description="A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. __The default keys ('_id' and 'date' are not listed)__")
@attr('contentModifiedDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Last time the content of this table was modified.")
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

    # return an object
    def docSerialize(self, doc, date_format=None):

        if 'date' in doc:
            if date_format == Table.TIMESTAMP:
                doc['date'] = int(time.mktime(doc['date'].timetuple()))
            elif date_format == Table.TIMESTAMP_MS:
                doc['date'] = int(time.mktime(doc['date'].timetuple())) * 1000
            else:
                doc['date'] = doc['date'].replace(tzinfo=pytz.utc).astimezone(self.ething.local_tz).isoformat()

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

            self._length = 0
            self._keys = {}
            self._contentModifiedDate = datetime.datetime.utcnow()

    # is called regularly

    def checkExpiredData(self):

        with self:
            # remove the expired data in the current table
            expireAfter = self.expireAfter
            if expireAfter is not None:
                expiratedDate = datetime.datetime.utcnow() - datetime.timedelta(0, expireAfter)

                removed_rows = self.db.remove_table_rows_by_query(self.collectionName, 'date < "%s"' % expiratedDate.isoformat())

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
                self._length = self.length - nb

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
                self._length = self.length + nb

        if reset is True:
            meta = self.db.get_table_metadata(self.collectionName)
            self._length = meta.get('length', 0)
            self._keys = meta.get('keys', {})
            self.data = {}

        self._contentModifiedDate = datetime.datetime.utcnow()

    def updateMeta(self):
        with self:
            self._update_meta(reset = True)

    def repair(self):
        self.updateMeta()


    # return the number of document removed
    def remove_rows(self, row_ids):
        with self:

            removed_rows = self.db.remove_table_rows_by_id(self.collectionName, row_ids)
            self._update_meta(removed_rows=removed_rows)
            return len(removed_rows)

    def remove_row(self, row_id):
        return self.remove_rows([row_id]) > 0

    @staticmethod
    def sanitizeData(dataArray, invalidFields=INVALID_FIELD_RENAME, skipError=True, setDate=True):

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

                    if not(isinstance(v, integer_types) or isinstance(v, float) or isinstance(v, string_types) or isinstance(v, bool) or v is None):
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
                            data[k] = parse(v)
                        except:
                            raise Exception('Invalid date "%s"' % v)

                # add date if not already set
                if setDate and 'date' not in data:
                    # add the insertion date for that document
                    data['date'] = datetime.datetime.utcnow()

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
                l = Table.sanitizeData(dataArray, invalidFields, False)

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
            length = Table.sanitizeData(dataArray, invalidFields, skipError)

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
                l = Table.sanitizeData(dataArray, invalidFields, False)

                if l > 0:
                    new_row = dataArray[0]
                    # copy id
                    new_row['id'] = row_id

                    # insert the data
                    old_row = self.db.update_table_row(self.collectionName, new_row)

                    if old_row:
                        self._update_meta(removed_rows=[old_row], added_rows=[new_row])
                        return self.docSerialize(new_row)

        return False

    # replace only one row
    def replaceRow(self, query, data, invalidFields=INVALID_FIELD_RENAME, upsert=False):
        if data:
            with self:

                rows = self.db.get_table_rows(self.collectionName, query = query, length = 1)

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

        rows = self.db.get_table_rows(self.collectionName, query = query, sort = sort, start = start, length = length, keys = fields)

        if isinstance(date_format, string_types):
            date_format = date_format.lower()
            if date_format == "timestamp":
                date_format = Table.TIMESTAMP
            elif date_format == "timestamp_ms":
                date_format = Table.TIMESTAMP_MS
            else:
                date_format = None

        # iterate
        items = []
        for row in rows:
            items.append(self.docSerialize(row, date_format))

        return items

    def computeStatistics(self, key, query=None):
        return self.db.get_table_statistics_by_key(self.collectionName, key, query)

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