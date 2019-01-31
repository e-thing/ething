# coding: utf-8

from .. import *
from requests import Request, Session


@meta(icon='mdi-earth', label="HTTP request")
@attr('body', type=Text(), default='', description="The body part.")
@attr('method', type=Enum(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']), default='GET', description="The HTTP method.")
@attr('url', type=String(allow_empty=False), description="The HTTP URL.")
class HttpRequest(Node):
    """ Make a HTTP request """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):

        s = Session()

        req = Request(self.method, self.url)

        if self.method in ['POST', 'PUT', 'PATCH']:
            req.data = self.body

        prepped = req.prepare()

        resp = s.send(prepped)

        self.log.debug("method=%s, url=%s, resp.status_code=%s" % (self.method, self.url, resp.status_code))

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

