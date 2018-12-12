from future.utils import string_types
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
    for r in core.find(sort='+createdDate'):
        resources.append({
            'id': r.id,
            'type': r.type,
            'name': r.name,
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

    return data


def import_data(core, data, import_config=False):

    if core.version != data.get('version'):
        raise Exception('unable to import: version numbers differ %s (current) != %s (import)' % (core.version, data.get('version')))

    # config
    if import_config:
        config = data.get('config')
        if config:
            core.config.update(config)

    # resources
    for r in data.get('resources', []):
        cls = get_registered_class(r.get('type'))
        if cls:
            core.log.info('importing resource id=%s name=%s type=%s' % (r.get('id'), r.get('name', '?'), r.get('type')))
            try:
                cls.import_instance(r.get('resource'), context={'ething': core})
            except:
                core.log.exception('resource import error id=%s name=%s type=%s' % (r.get('id'), r.get('name', '?'), r.get('type')))

    # plugins
    plugins_export = data.get('plugins')
    if plugins_export:
        for p in core.plugins:
            if p.name in plugins_export:
                core.log.info('importing plugin %s' % (p.name,))
                try:
                    p.import_data(plugins_export.get(p.name))
                except:
                    core.log.exception('plugin import error %s' % p.name)

