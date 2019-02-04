from .date import utcnow
import datetime
from ..reg import get_registered_class
from dateutil import parser
import json
import sys


if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat()
            }
        if py3 and isinstance(obj, bytes):
            return {
                "_type": "bytes",
                "value": obj.decode('utf8')
            }
        # Let the base class default method raise the TypeError
        return super(Encoder, self).default(obj)


class Decoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' in obj:
            type = obj['_type']
            if type == 'datetime':
                return parser.parse(obj['value'])
            if type == 'bytes':
                return obj['value'].encode('utf8')
        return obj


def export_data(core):

    data = {
        'version': core.version,
        'date': utcnow()
    }

    # config
    data['config'] = core.config.toJson()

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

    return json.dumps(data, cls=Encoder, indent=2)


def import_data(core, data, import_config=False):

    try:
        data = json.loads(data, cls=Decoder)
    except Exception as e:
        raise Exception('unable to decode data: %s' % str(e))

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

