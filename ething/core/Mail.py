# coding: utf-8
from future.utils import string_types

import smtplib
import logging
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase



class Mail(object):

    def __init__(self, core):

        self.core = core
        self.log = logging.getLogger('ething.mail')

        self.host = core.config('notification.smtp.host')
        self.port = core.config('notification.smtp.port')
        self.user = core.config('notification.smtp.user')
        self.password = core.config('notification.smtp.password')
        self.to = core.config('notification.emails')

        if isinstance(self.to, string_types):
            self.to = [self.to]

    def send(self, subject=None, message=None, attachments=None, to=None):
        from .Table import Table
        from .File import File

        if not self.host or not self.port or not self.user or not self.password:
            self.log.debug('warning: no configuration set')
            return False

        if isinstance(to, string_types):
            to = [to]

        if not to and self.to:
            to = self.to

        if not to or len(to) == 0:
            self.log.warning('no recipient set')
            return False

        try:
            msg = MIMEMultipart()

            msg['From'] = self.user
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject or 'notification'

            body = message if message else ''

            msg.attach(MIMEText(body, 'plain'))

            if attachments:
                for attachment in attachments:

                    if isinstance(attachment, string_types):  # id
                        attachment = self.core.get(attachment)

                    if isinstance(attachment, dict):
                        filename = attachment['name']
                        content = attachment['content']
                    elif isinstance(attachment, File):
                        filename = attachment.name
                        content = attachment.read()
                    elif isinstance(attachment, Table):
                        filename = attachment.name+'.csv'
                        content = attachment.toCSV()
                    else:
                        continue

                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(content)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    "attachment; filename= %s" % filename)

                    msg.attach(part)

            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            text = msg.as_string()
            self.log.debug('sending a email "%s" to %s' % (subject, ','.join(to)))
            server.sendmail(self.user, to, text)
            server.quit()
        except:
            self.log.exception('unable to send mail')
            return False

        return True
