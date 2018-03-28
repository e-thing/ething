


"""
 @swagger-definition
 "SSH":{ 
   "type": "object",
   "description": "SSH Device resource representation",
	 "allOf": [
		{
		   "$ref":"#/definitions/Device"
		},
		{  
		   "type": "object",
		   "properties":{
			 "host": {
				  "type":"string",
				  "description":"The ip address or hostname of the device to connect to."
			   },
			 "port": {
				  "type":"number",
				  "description":"The port number of the device to connect to. The default port number is 22."
			   },
			 "auth": {
				"type":"object",
				  "properties":{  
					"user":{  
					   "type":"string",
					   "description":"the username to use for the authentication."
					},
					"password":{  
					   "type":"string",
					   "description":"the password to use for the authentication."
					}
				},
				  "description":"An object describing the credentials to use."
			   }
		   }
		}
   ]
 }
"""


from ething.Device import Device, method, attr, isString, isObject, isInteger, isNone
import paramiko
from ething.utils import pingable




@pingable
@attr('host', validator = isString(allow_empty = False))
@attr('port', validator = isInteger(min=0, max=65535), default = 22)
@attr('auth', validator = isNone() | isObject(user=isString(allow_empty=False), password=isString(allow_empty=False)), default=None)
class SSH(Device):
	
	
	
	@method.arg('command', type="string")
	@method.return_type('text/plain')
	def execute(self, command):
		"""
		execute a command.
		"""
		if command:
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.load_system_host_keys()
			client.connect(self.host, self.port, username=self.auth['user'], password=self.auth['password'])
			stdin, stdout, stderr = client.exec_command(command)
			
			
			response = stdout.read()
			#for line in stdout:
			#	response += line+' '
			client.close()
			return response
		else:
			raise ValueError('command must be a non empty string')



if __name__ == '__main__':
	
	from ething.core import Core
	
	ething = Core({
		'db':{
			'database': 'test'
		},
		'log':{
			'level': 'debug'
		}
	})
	
	dev = ething.findOne({
		"name": "sshdev"
	})
	
	if not dev:
		dev = ething.create("SSH", {
			"name": "sshdev",
			"host" : "localhost",
			"auth": {
				"user": "lebios",
				"password": "amb1987"
			}
		})
	
	print dev
	
	print dev.execute("ls")
	
	
	
	
	




