# coding: utf-8

from ething.core.Device import *
import requests
from ething.plugins.ping import pingable


REQUESTS_TIMEOUT=None


@pingable()
@attr('secure', type=Boolean(), default=False, description="Wether use https over http")
@attr('port', type=Integer(min=0, max=65535), default=80, description="The port number of the device to connect to. The default port number is 80.")
@attr('host', type=String(allow_empty=False), description="The ip address or hostname of the device to connect to.")
class HTTP(Device):
    """
    HTTP Device resource representation
    """

    def _make_request(self, method, path='', params = None, body = None, headers = None, **options):

        args = dict(params=params)
        args["timeout"] = REQUESTS_TIMEOUT

        url = 'http'

        if self.secure:
            url += 's'

        url += '://' + self.host

        if self.port != 80:
            url += ':' + str(self.port)

        if not path.startswith('/'):
            url += '/'

        url += path

        self.log.debug('request: %s %s' % (method, url))

        r = requests.request(method.upper(), url, headers=headers, params=params, data=body, **options)

        self.log.debug('request status: %s' % (r.status_code))

        r.raise_for_status()

        return r

    @method.return_type('text/plain')
    @method.arg('body', type='string')
    @method.arg('path', type='string', default='')
    @method.arg('method', type=Enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']), default='GET')
    def make_request(self, method, path='', body=None):
        r = self._make_request(method, path, body=body)
        return r.content
