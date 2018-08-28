from ething.Helpers import toJson
import base64


def export_data(core):

    data = {}

    # resources
    data['resources'] = core.db.list_resources()

    # tables
    tables = {}
    for table_id in core.db.list_tables():
        tables[table_id] = core.db.get_table_rows(table_id)
    data['tables'] = tables

    # files
    files = {}
    for file_id in core.db.listFiles():
        files[file_id] = {
            'metadata': core.db.getFileMeta(file_id),
            'content': base64.b64encode(core.db.retrieveFile(file_id))
        }
    data['files'] = files

    return toJson(data)

def import_data(core, data):

    # resources
    for r in data['resources']:
        core.db.insert_resource(r)

    # tables
    for table_id in data['tables']:
        core.db.insert_table_rows(table_id, data['tables'][table_id]

    # files
    for file_id in data['files']:
        f = data['files'][file_id]
        core.db.storeFile(??, base64.b64decode(f['content']), f['metadata'], file_id)
