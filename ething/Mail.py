
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from Table import Table
from File import File


class Mail(object):
	
	
	def __init__ (self, core):
		
		self.core = core
		self.log = core.log
		
		self.host = core.config('notification.smtp.host')
		self.port = core.config('notification.smtp.port')
		self.user = core.config('notification.smtp.user')
		self.password = core.config('notification.smtp.password')
		self.to = core.config('notification.emails')
		
		if isinstance(self.to,basestring):
			self.to = [self.to]
	
	def send (self, subject = 'notification',message = None, attachments = [], to = []):
		
		if not self.host or not self.port or not self.user or not self.password:
			return False
		
		if isinstance(to,basestring):
			to = [to]
		
		if not to and self.to:
			to = self.to
		
		if len(to) == 0:
			return False
		
		msg = MIMEMultipart()
		 
		msg['From'] = self.user
		msg['To'] = ', '.join(to)
		msg['Subject'] = subject
		
		body = message if message else ''
		
		msg.attach(MIMEText(body, 'plain'))
		
		for attachment in attachments:
			
			if isinstance(attachment, basestring): # id
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
			part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
			 
			msg.attach(part)
		
		
		server = smtplib.SMTP(self.host, self.port)
		server.starttls()
		server.login(self.user, self.password)
		text = msg.as_string()
		self.log.debug('sending a email "%s" to %s' % (subject, ','.join(to)))
		server.sendmail(self.user, to, text)
		server.quit()
		
		
		return True
	
	
	

if __name__ == '__main__':
	
	from ething.core import Core
	
	core = Core({
		'db':{
			'database': 'test'
		},
		'log': {
			'level': 'DEBUG'
		},
		"notification": {
			"emails": [
				"a.mezerette@gmail.com"
			],
			"smtp": {
				"host": "smtp.gmail.com",
				"port": 587,
				"user": "LOGIN@gmail.com",
				"password": "PASSWORD"
			}
		}
	})
	
	mail = Mail(core)
	
	print mail.send('toto')
	


