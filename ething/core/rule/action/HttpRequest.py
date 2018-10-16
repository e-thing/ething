# coding: utf-8

from .Action import Action
from ...entity import *
from requests import Request, Session


@attr('method', type=Enum(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']), default='GET', description="The HTTP method.")
@attr('url', type=String(allow_empty=False), description="The HTTP URL.")
@attr('body', type=String(), default='', description="The body part.")
class HttpRequest(Action):
    """ Make a HTTP request """
    def run(self, signal):
        s = Session()

        req = Request(self.method, self.url)

        if self.method in ['POST', 'PUT', 'PATCH']:
            req.data = self.body

        prepped = req.prepare()

        resp = s.send(prepped)

        self.log.debug("method=%s, url=%s, resp.status_code=%s" % (self.method, self.url, resp.status_code))

        resp.raise_for_status()


