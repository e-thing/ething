

from ething.Device import Device, method, attr, isString, isObject, isInteger, isNone
import paramiko
from ething.utils import pingable




@pingable()
@attr('host', validator = isString(allow_empty = False), description="The ip address or hostname of the device to connect to.")
@attr('port', validator = isInteger(min=0, max=65535), default = 22, description="The port number of the device to connect to. The default port number is 22.")
@attr('auth', validator = isObject(user=isString(allow_empty=False), password=isString(allow_empty=False)) | isNone(), default=None, description="An object describing the credentials to use.")
class SSH(Device):
    """
    SSH Device resource representation
    """
    
    
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
            #    response += line+' '
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
    
    
    
    
    




