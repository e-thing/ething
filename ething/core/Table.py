# coding: utf-8
from .Resource import Resource, ResourceType
from .utils.date import TzDate, utcnow, utcfromtimestamp, datetime_to_array
from .reg import *
from .Signal import ResourceSignal
from .utils import object_sort, ShortId, ObjectPath, filter_obj
from .flow import ResourceNode
import datetime
import time
import re
from dateutil.parser import parse
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
        super(TableDataAdded, self).__init__(resource, **data)


@meta(icon='mdi-table-row-plus-after', category="storage")
@attr('resource', type=ResourceType(accepted_types=('resources/Table',)))
class AppendData(ResourceNode):
    INPUTS = ['default']

    def main(self, **inputs):
        msg = inputs.get('default')
        table = self.resource

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
@attr('length', default=0, mode=READ_ONLY, description="The number of records in the table")
@attr('keys', type=Dict(), default={}, mode=READ_ONLY, description="A key/value object where the keys correspond to the fields available in this table, and the corresponding value is the number of rows where the field is set. The default keys ('id' and 'date' are not listed)")
@attr('contentModifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time the content of this table was modified.")
class Table(Resource):
    """
    The Table resource is used to store time series.

    Example::

        t = core.create('resources/Table', {
            'name': 'foo'
        })

        t.insert({
            'foo': 'bar'
        })
    """

    FIELD_VALID_CHAR = 'a-zA-Z0-9_\-'
    VALIDATE_FIELD = '^['+FIELD_VALID_CHAR+']{1,64}$'

    INVALID_FIELD_NONE = 0
    INVALID_FIELD_RENAME = 1
    INVALID_FIELD_SKIP = 2
    INVALID_FIELD_STOP = 4

    TIMESTAMP = 0
    TIMESTAMP_MS = 1
    ISO = 2

    # return an object
    def doc_serialize(self, doc, date_format=None):

        if 'date' in doc:
            dt = doc['date']
            if date_format == Table.TIMESTAMP:
                doc['date'] = int(time.mktime(dt.timetuple()))
            elif date_format == Table.TIMESTAMP_MS:
                doc['date'] = int(time.mktime(dt.timetuple())) * 1000
            elif date_format == Table.ISO:
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=pytz.utc)
                doc['date'] = dt.astimezone(self.core.local_tz).isoformat()
            else:
                pass

        return doc

    @property
    def collection_name(self):
        return 'tb.%s' % self.id

    @property
    def table(self):
        return self.core.db[self.collection_name]

    def remove(self):

        # remove all the data from this table
        self.core.db.table_drop(self.collection_name, silent=True)

        # remove the resource
        super(Table, self).remove()

    def clear(self):
        """
        Clear all the data.
        """
        with self:
            # remove all the data from this table
            self.table.clear()

            self.length = 0
            self.keys = {}
            self.contentModifiedDate = utcnow()

    def _update_meta(self, removed_rows = None, added_rows = None, reset = False):

        if removed_rows is not None:
            keys = dict(self.keys)
            nb = 0

            for row in removed_rows:
                # update the key count
                for field in row:
                    if field in keys:
                        keys[field] -= 1
                        if keys[field] <= 0:
                            del keys[field]

                nb += 1

            self.keys = keys
            self.length = self.length - nb

        if added_rows is not None:
            keys = dict(self.keys)
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

            self.keys = keys
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


            for row in self.table.select():
                for k in row:
                    if k not in keys:
                        keys[k] = 0
                    keys[k] += 1
                length += 1

            keys.pop('id', None)
            keys.pop('date', None)

            self.length = length
            self.keys = keys

        self.contentModifiedDate = utcnow()

    def remove_rows(self, row_ids):
        """
        Remove multiple rows.

        :param row_ids: an array or row id
        :return: the number of document removed
        """
        with self:
            removed_rows = []
            for row_id in row_ids:
                removed_rows.append(self.table[row_id])
                del self.table[row_id]

            self._update_meta(removed_rows=removed_rows)
            return len(removed_rows)

    def remove_row(self, row_id):
        """
        Remove a single row.

        :param row_id: a row id
        :return: True if the row has been removed
        """
        return self.remove_rows([row_id]) > 0

    def sanitize_data(self, dataArray, invalidFields=INVALID_FIELD_RENAME, skipError=True):

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

                    if k == 'date':
                        # check the format
                        try:
                            if is_number:
                                data[k] = utcfromtimestamp(v) # UTC
                            elif isinstance(v, string_types):
                                data[k] = parse(v)

                            if data[k].tzinfo is None:
                                # naive datetime
                                data[k] = self.core.local_tz.localize(data[k]).astimezone(pytz.utc)
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
        """
        Insert single row.

        :param data: row's data.
        :return: the inserted row. Or False if an error occurs.
        """
        if data:
            with self:

                # sanitize the incoming data
                dataArray = [data]
                l = self.sanitize_data(dataArray, invalidFields, False)

                if l > 0:

                    # insert the data
                    self.table.insert(dataArray[0])

                    self._update_meta(added_rows = dataArray)

                    # remove extra rows
                    length = self.length
                    maxLength = self.maxLength
                    if maxLength and length > maxLength:
                        remove_length = length - maxLength

                        # remove extra rows
                        rows_to_be_removed = self.table.select(sort=('date', True), length=remove_length)
                        self.remove_rows([r['id'] for r in rows_to_be_removed])

                    doc = self.doc_serialize(dataArray[0])
                    # generate an event
                    self.emit(TableDataAdded(self, doc))

                    return doc

        return False

    def import_data(self, dataArray, invalidFields=INVALID_FIELD_RENAME, skipError=True):

        with self:
            maxLength = self.maxLength

            # remove extra row
            if maxLength and len(dataArray) > maxLength:
                dataArray = dataArray[0:maxLength]

            # remove any previous content
            self.clear()

            # sanitize the incoming data
            length = self.sanitize_data(dataArray, invalidFields, skipError)

            if length > 0:
                # insert the data
                for doc in dataArray:
                    self.table.insert(doc)
                self._update_meta(added_rows=dataArray)

        return True

    def get_row(self, id):
        """
        Fetch a single row.

        :param id: row's id
        :return: a row or False if the row was not found
        """
        return self.doc_serialize(self.table[id])

    def replace_row_by_id(self, row_id, data, invalidFields=INVALID_FIELD_RENAME):
        if data:
            with self:

                # sanitize the incoming data
                dataArray = [data]
                l = self.sanitize_data(dataArray, invalidFields, False)

                if l > 0:
                    new_row = dataArray[0]
                    # copy id
                    new_row['id'] = row_id

                    if row_id in self.table:
                        old_row = self.table[row_id]
                        self.table[row_id] = new_row
                        self._update_meta(removed_rows=[old_row], added_rows=[new_row])
                        return self.doc_serialize(new_row)

        return False

    # replace only one row
    def replace_row(self, query, data, invalidFields=INVALID_FIELD_RENAME, upsert=False):
        if data:
            with self:

                rows = self.select(query = query, length = 1)

                if len(rows) > 0:
                    row = rows[0]

                    return self.replace_row_by_id(row['id'], data, invalidFields)
                else:
                    # not found !
                    if upsert:
                        return self.insert(data, invalidFields)

        return False

    def select(self, start=0, length=None, fields=None, sort=None, query=None, date_format=None):
        """
        Return rows.

        :param start: If start is non-negative, the returned selection will start at the start'th position in the table, counting from zero. If start is negative, the returned selection will start at the start'th position from the end of the table.
        :param length: If length is given and is positive, the selection returned will contain at most length lines beginning from start. If length is omitted, the selection starting from start until the end of the table will be returned.
        :param fields: Array of string. Only those fields will be returned.
        :param sort: Either a string (prepended by '-' if you want the sort to be in descending order) or a tupple (<field>, ascending: True|False). eg: ``('date', True)`` or '-date'.
        :param query: An ObjectPath query filter.
        :param date_format: "timestamp" or "timestamp_ms" or "rfc3339" or None(default). The format of the date field.
        :return: Array of row
        """
        if sort is None:
            # always sort by date
            sort = ('date', True)

        if isinstance(sort, string_types):
            m = re.search('^([+-]?)(.+)$', sort)
            if m is not None:
                sortField = m.group(2)
                sortAsc = bool(m.group(1) != '-')
                sort = (sortField, sortAsc)
            else:
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
        elif date_format == "rfc3339":
            date_format = Table.ISO
        elif date_format is None:
            pass
        else:
            raise Exception('invalid date_format "%s"' % date_format)

        # retrieve all the data
        rows = self.table.select()

        # apply the filter according to the query string
        # TODO: what about the date field ? doc_serialize() here ?

        if query:
            _filter = ObjectPath.generate_filter(query)
            rows = [row for row in rows if _filter(row)]

        if sort:
            sort_attr = sort[0]
            asc = sort[1] if len(sort)>1 else True
            rows = object_sort(rows, key=lambda doc: doc.get(sort_attr, None), reverse=not asc)

        if start or length:
            start = start or 0
            rows = rows[start:(length + start if length is not None else None)]

        if fields is not None:
            rows = [filter_obj(row, fields) for row in rows]

        return [self.doc_serialize(row, date_format) for row in rows]

    def compute_statistics(self, key, query=None):

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

