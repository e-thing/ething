# coding: utf-8

from ething.plugin import *
from .smtp import SmtpMail
from ething.flow import Node, Descriptor
from ething.reg import *


@attr('password', type=String(password=True), default='')
@attr('user', type=String(), default='')
@attr('port', type=Number(min=1, max=65535), default=587)
@attr('host', type=String(allow_empty=False), default="smtp.gmail.com")
class Mail(Plugin):
    pass


@meta(icon='mdi-email', category="notification")
@attr('message', type=Descriptor(('text', 'template', 'msg', 'flow', 'glob', 'env')), description="The message of the notification")
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

        mail_plugin = self.core.get_plugin('mail')
        mailer = SmtpMail(host=mail_plugin.host, port=mail_plugin.port, user=mail_plugin.user, password=mail_plugin.password)
        mailer.send(subject=subject, message=message, to=to)
        self.log.debug('email "%s" send to %s', subject, to)

