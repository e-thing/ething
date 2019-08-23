# coding: utf-8

from .. import *
from requests import Request, Session


@meta(icon='http', label="HTTP request", category="function")
@attr('body', type=Descriptor(('text', 'template', 'msg', 'flow', 'glob', 'env')), default={'type':'text', 'value':''}, description="The body part.")
@attr('method', type=Enum(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']), default='GET', description="The HTTP method.")
@attr('url', type=Descriptor(('string', 'msg', 'flow', 'glob', 'env')), description="The HTTP URL.")
class HttpRequest(Node):
    """ Make a HTTP request """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': self.flow,
        }

        url = self.url.get(**_context)
        method = self.method
        body = self.body.get(**_context)

        s = Session()

        req = Request(method, url)

        if body:
            req.data = body

        prepped = req.prepare()

        resp = s.send(prepped)

        self.logger.debug("method=%s, url=%s, resp.status_code=%s", method, url, resp.status_code)

        resp.raise_for_status()

        self.emit({
            'payload': {
                'content': resp.content,
                'headers': resp.headers,
                'status_code': resp.status_code,
                'url': resp.url,
                'encoding': resp.encoding
            }
        })

