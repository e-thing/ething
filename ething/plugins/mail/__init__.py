# coding: utf-8

from ething.core.plugin import Plugin
from collections import OrderedDict
from .smtp import SmtpMail
from ething.core.flow import Node, Descriptor
from ething.core.reg import *


class Mail(Plugin):

    CONFIG_DEFAULTS = {
        'host': 'smtp.gmail.com',
        'port' : 587,
        'user' : '',
        'password' : ''
    }

    CONFIG_SCHEMA = {
        "type": "object",
        "additionalProperties": False,
        "properties": OrderedDict([
            ("host", {
                "type": "string",
                "minLength": 1
            }),
            ("port", {
                "type": "integer",
                "title": "The Port Schema ",
                'minimum': 1,
                'maximum': 65535
            }),
            ("user", {
                "type": "string"
            }),
            ("password", {
                "type": "string",
                "format": "password"
            })
        ])
    }



@meta(icon='mdi-email', category="notification")
@attr('message', type=Descriptor(('text', 'msg', 'flow', 'glob', 'env')), description="The message of the notification")
@attr('subject', type=Descriptor(('string', 'msg', 'flow', 'glob', 'env')), description="The subject of the notification")
@attr('to', type=Descriptor(('string', 'msg', 'flow', 'glob', 'env')), description="Recipient email address")
class SendEmail(Node):
    """ Send an email """

    INPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': self.flow,
        }

        to = self.to.get(**_context)
        subject = self.subject.get(**_context)
        message = self.message.get(**_context)

        conf = self.core.get_plugin('Mail').config
        mailer = SmtpMail(host=conf.get('host'), port=conf.get('port'), user=conf.get('user'), password=conf.get('password'))
        mailer.send(subject=subject, message=message, to=to)
        self.log.debug('email "%s" send to %s' % (subject, to))

