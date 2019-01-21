# coding: utf-8

from ething.core.plugin import Plugin
from collections import OrderedDict
from .smtp import SmtpMail
from ething.core.Flow import ActionNode
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
                'type': 'integer',
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



@meta(icon='mdi-email')
@attr('message', type=String(), description="The message of the notification")
@attr('subject', type=String(), description="The subject of the notification")
@attr('to', type=Email(), description="Recipient email address")
class SendEmail(ActionNode):
    """ Send an email """
    def run(self, msg, core):
        conf = core.get_plugin('Mail').config
        mailer = SmtpMail(host = conf.get('host'), port = conf.get('port'), user = conf.get('user'), password = conf.get('password'))
        mailer.send(subject = self.subject, message = self.message, to = self.to)
        self.log.debug('email "%s" send to %s' % (self.subject, self.to))

