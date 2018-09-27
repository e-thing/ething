from ..Helpers import toJson
import datetime
from ..reg import get_registered_class


def export_data(core):

    data = {
        'version': core.version,
        'date': datetime.datetime.now()
    }

    # config
    data['config'] = core.config

    # resources
    resources = []
    for r in core.find():
        resources.append({
            'id': r.id,
            'type': r.type,
            'resource': r.export_instance()
        })
    data['resources'] = resources

    # plugins
    plugins_export = dict()
    for p in core.plugins:
        d = p.export_data()
        if d is not None:
            plugins_export[p.name] = d
    data['plugins'] = plugins_export

    return toJson(data)


def import_data(core, data):

    if core.version != data.get('version'):
        raise Exception('unable to import: version numbers differ %s != %s' % (core.version, data.get('version')))

    # config
    config = data.get('config')
    if config:
        core.config.set(config)

    # resources
    for r in data.get('resources', []):
        cls = get_registered_class(r.get('type'))
        if cls:
            cls.import_instance(r.get('resource'), ething=core)

    # plugins
    plugins_export = data.get('plugins')
    if plugins_export:
        for p in core.plugins:
            if p.name in plugins_export:
                p.import_data(plugins_export.get(p.name))

