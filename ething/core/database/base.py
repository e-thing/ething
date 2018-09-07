# coding: utf-8

from future.utils import integer_types
import math
import logging


number_types = integer_types + (float, )


class BaseClass (object):

    def __init__(self, **config):
        self.log = logging.getLogger('ething.db')

        for k in config:
            setattr(self, k, config[k])

    def connect(self):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def get_usage(self):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()


    #
    # Resources
    #

    def list_resources(self):
        raise NotImplementedError()

    def update_resource(self, resource):
        raise NotImplementedError()

    def insert_resource(self, resource):
        raise NotImplementedError()

    def remove_resource(self, resource):
        raise NotImplementedError()


    #
    # File System (used for storing images, text ...)
    #

    def storeFile(self, filename, contents, metadata=None, id=None):
        """return the file id"""
        raise NotImplementedError()

    def retrieveFile(self, file_id):
        raise NotImplementedError()

    def removeFile(self, file_id):
        raise NotImplementedError()

    def getFileMetadata(self, file_id):
        raise NotImplementedError()

    def getFileSize(self, file_id):
        raise NotImplementedError()

    def listFiles(self):
        raise NotImplementedError()


    #
    # Table (used for storing data time series)
    #

    def create_table(self, table_id):
        raise NotImplementedError()

    def remove_table(self, table_id):
        raise NotImplementedError()

    def get_table_rows(self, table_id, query = None, start=0, length=None, keys=None, sort=None):
        raise NotImplementedError()

    def get_table_row_by_id(self, table_id, row_id):
        rows = self.get_table_rows(table_id, query = "id == %s" % row_id, length = 1)
        return rows[0] if len(rows) > 0 else None

    def get_table_metadata(self, table_id):
        """
        compute the length and list the keys (except the id and date keys)
        {
            length: int,
            keys: { key: number }
        }
        """
        keys = {}
        length = 0

        for row in self.get_table_rows(table_id):
            for k in row:
                if k not in keys:
                    keys[k] = 0
                keys[k] += 1
            length += 1

        keys.pop('id', None)
        keys.pop('date', None)

        return {
            'length': length,
            'keys': keys
        }

    def insert_table_row(self, table_id, row_data):
        raise NotImplementedError()

    def insert_table_rows(self, table_id, rows_data):
        for row_data in rows_data:
            self.insert_table_row(table_id, row_data)

    def update_table_row(self, table_id, row_id, row_data):
        """return the old row"""
        raise NotImplementedError()

    def remove_table_row(self, table_id, row_id):
        """return the removed row"""
        raise NotImplementedError()

    def remove_table_rows_by_id(self, table_id, row_ids):
        removed_rows = []
        for row_id in row_ids:
            removed_row = self.remove_table_row(table_id, row_id)
            if removed_row:
                removed_rows.append(removed_row)
        return removed_rows

    def remove_table_rows_by_query(self, table_id, query):
        rows_to_be_removed = self.get_table_rows(table_id, query = query)
        return self.remove_table_rows_by_id(table_id, [row.get('id') for row in rows_to_be_removed])

    def get_table_statistics_by_key(self, table_id, key, query = None):

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


        rows = self.get_table_rows(table_id, query = query, keys = ['id', 'date', key])

        for row in rows:
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
