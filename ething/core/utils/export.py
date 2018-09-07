from ..Helpers import toJson
import base64
import datetime


def export_data(core):

    data = {
        'version': core.version,
        'date': datetime.datetime.now()
    }

    # resources
    data['resources'] = core.db.list_resources()

    # tables
    tables = {}
    for table_id in core.db.list_tables():
        tables[table_id] = core.db.get_table_rows(table_id)
    data['tables'] = tables

    # files
    files = {}
    for file in core.db.listFiles():
        file_id = file['id']
        files[file_id] = {
            'metadata': file['metadata'],
            'filename': file['filename'],
            'content': base64.b64encode(core.db.retrieveFile(file_id))
        }
    data['files'] = files

    return toJson(data)

def import_data(core, data):

    if core.version != data.get('version'):
        raise Exception('unable to import: version numbers differ %s != %s' % (core.version, data.get('version')))

    # resources
    for r in data['resources']:
        core.db.insert_resource(r)

    # tables
    for table_id in data['tables']:
        core.db.insert_table_rows(table_id, data['tables'][table_id])

    # files
    for file_id in data['files']:
        file = data['files'][file_id]
        core.db.storeFile(file['filename'], base64.b64decode(file['content']), file['metadata'], file_id)
