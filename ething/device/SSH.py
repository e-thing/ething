# coding: utf-8


from ething.Device import *
import paramiko
from ething.utils import pingable


@pingable()
@attr('auth', type=Dict(mapping = OrderedDict([('user', String(allow_empty=False)), ('password', String(allow_empty=False))])), description="An object describing the credentials to use.")
@attr('port', type=Integer(min=0, max=65535), default=22, description="The port number of the device to connect to. The default port number is 22.")
@attr('host', type=String(allow_empty=False), description="The ip address or hostname of the device to connect to.")
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
            client.connect(
                self.host, self.port, username=self.auth['user'], password=self.auth['password'])
            stdin, stdout, stderr = client.exec_command(command)

            response = stdout.read()
            # for line in stdout:
            #    response += line+' '
            client.close()
            return response
        else:
            raise ValueError('command must be a non empty string')
