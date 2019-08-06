# coding: utf-8
from future.utils import string_types

import smtplib
import logging
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

from ething.core.Table import Table
from ething.core.File import File


class SmtpMail(object):

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port or 465
        self.user = user
        self.password = password

    def send(self, subject=None, message=None, attachments=None, to=None):

        if not self.host or not self.port or not self.user or not self.password:
            raise Exception('no configuration set')

        if isinstance(to, string_types):
            to = [to]

        if not to or len(to) == 0:
            raise Exception('no recipient set')

        msg = MIMEMultipart()

        msg['From'] = self.user
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject or 'notification'

        body = message if message else ''

        msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for attachment in attachments:

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

        if self.port == 465:
            # tls
            server = smtplib.SMTP_SSL(self.host, self.port)
            server.ehlo()
        else:
            server = smtplib.SMTP(self.host, self.port)
            server.ehlo()
            server.starttls()

        server.login(self.user, self.password)
        text = msg.as_string()
        server.sendmail(self.user, to, text)
        server.quit()

        return True
