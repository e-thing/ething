# coding: utf-8
from ething.core.Device import *
import paramiko
from ething.plugins.ping import pingable
from ething.core.plugin import Plugin
from ething.core.Process import Process
import socket
import uuid
import time


SHELL_CLIENT_ACTIVITY_TIMEOUT = 60


class SSHPlugin(Plugin):

    JS_INDEX = './js/index.js'

    def setup(self):
        # install specific http routes
        self._webserver_install()

    def _webserver_install(self):

        # install specific http routes
        webserver_plugin = self.core.get_plugin('webserver')
        if not webserver_plugin:
            return

        app = webserver_plugin.app
        auth = app.auth
        socketio = app.socketio

        from flask import request, copy_current_request_context
        from flask_socketio import emit

        self.interactive_shell_manager = Interactive_Shell_Manager()

        @app.route('/api/ssh/shells')
        @auth.required()
        def list_interactive_shell():
            return app.jsonify(self.interactive_shell_manager)

        @app.route('/api/ssh/shells/<id>')
        @auth.required()
        def interactive_shell(id):
            shell = self.interactive_shell_manager.get(id)
            if not shell:
                raise Exception('shell not found')
            return app.jsonify(shell)

        @socketio.on('connect', namespace='/ssh')
        def client_connect():
            self.log.debug('Client connected %s' % request.sid)

        @socketio.on('disconnect', namespace='/ssh')
        def client_disconnect():
            self.log.debug('Client disconnected %s' % request.sid)
            self.interactive_shell_manager.leave(request.sid)

        @socketio.on('open', namespace='/ssh')
        def open_interactive_shell(data):

            device_id = data.get('device_id')
            shell_id = data.get('id')
            client_id = request.sid

            device = app.getResource(device_id, ['SSH'])

            # does the shell already exist !
            resume = True
            shell = self.interactive_shell_manager.get(shell_id)
            if not shell:
                shell = Interactive_Shell(device, id=shell_id)
                resume = False

            self.log.debug('ssh open, client %s , shell %s , resume=%s' % (client_id, shell, resume))

            @copy_current_request_context
            def on_data(data):
                # socketio.emit('data', data, namespace="/ssh", room=interactive_shell_instance.id)
                emit('data', {
                    'id': shell.id,
                    'data': data
                }, namespace='/ssh')

            @copy_current_request_context
            def on_close():
                # socketio.close_room(interactive_shell_instance.id, namespace="/ssh")
                self.interactive_shell_manager.remove(shell)
                emit('closed', {
                    'id': shell.id
                }, namespace='/ssh')

            shell.on_data = on_data
            shell.on_close = on_close

            if not resume:
                shell.open()
                self.interactive_shell_manager.add(shell)

            self.interactive_shell_manager.join(client_id, shell)

            emit('opened', {
                'id': shell.id,
                'buffer': shell.buffer
            }, namespace='/ssh')

        @socketio.on('close', namespace='/ssh')
        def close_interactive_shell(data):
            self.log.debug('ssh close, client %s' % (request.sid))

            shell_id = data.get('id')
            shell = self.interactive_shell_manager.get(shell_id)
            if shell:
                shell.close()

        @socketio.on('detach', namespace='/ssh')
        def detach_interactive_shell(data):
            self.log.debug('ssh detach, client %s' % (request.sid))

            shell_id = data.get('id')
            shell = self.interactive_shell_manager.get(shell_id)
            if shell:
                self.interactive_shell_manager.leave(request.sid, shell)

        @socketio.on('send', namespace='/ssh')
        def send_interactive_shell(data):
            shell_id = data.get('id')
            shell = self.interactive_shell_manager.get(shell_id)
            if shell:
                shell.send(data.get('data'))

        self.core.scheduler.setInterval(10, self.interactive_shell_manager.clean, name="ssh.clean_session", condition=lambda _: not self.interactive_shell_manager.is_empty)


class Interactive_Shell_Manager(object):
    def __init__(self):
        self._shells = {}

    @property
    def is_empty(self):
        return not bool(self._shells)

    def add(self, shell):
        if shell.id not in self._shells:
            self._shells[shell.id] = {
                'shell': shell,
                'clients': set(),
                'ts_create': time.time(),
                'ts_client_activity': None
            }

    def remove(self, shell):
        if isinstance(shell, Interactive_Shell):
            shell = shell.id

        if shell in self._shells:
            del self._shells[shell]

    def get(self, id):
        if id in self._shells:
            return self._shells.get(id)['shell']

    def join(self, client_id, shell):
        if isinstance(shell, Interactive_Shell):
            shell = shell.id

        if shell in self._shells:
            self._shells[shell]['clients'].add(client_id)
            self._shells[shell]['ts_client_activity'] = time.time()

    def leave(self, client_id, shell=None):
        if isinstance(shell, Interactive_Shell):
            shell = shell.id

        if shell is None:
            # remove the client from all the interactive shells
            for k in self._shells:
                self.leave(client_id, k)
        else:
            if shell in self._shells:
                try:
                    self._shells[shell]['clients'].remove(client_id)
                    self._shells[shell]['ts_client_activity'] = time.time()
                except KeyError:
                    pass

    def clean(self):
        # close/remove non linked shell
        to_remove = set()
        for shell_id in list(self._shells.keys()):
            item = self._shells[shell_id]
            if len(item['clients'])==0:
                # ghost shell: no client attached to this shell
                ts_client_activity = item['ts_client_activity'] or item['ts_create']
                if time.time() - ts_client_activity > SHELL_CLIENT_ACTIVITY_TIMEOUT:
                    to_remove.add(shell_id)

        for shell_id in to_remove:
            shell = self.get(shell_id)
            self.remove(shell_id)
            shell.close()

    def clear(self):
        shells = [self._shells.get(k).get('shell') for k in self._shells]
        self._shells.clear()

        for shell in shells:
            shell.close()

    def toJson(self):
        return [self._shells[id]['shell'] for id in self._shells]


class Interactive_Shell(Process):

    BUFFER_SIZE = 2000

    def __init__(self, device, id=None, on_data=None, on_open=None, on_close=None):
        super(Interactive_Shell, self).__init__(name='ssh.interactive_shell', manager=device.core.process_manager, id=id)
        self.device = device
        self.session = None
        self.on_data = on_data
        self.on_open = on_open
        self.on_close = on_close
        self.buffer = b''

    def __str__(self):
        return '<SSH.Interactive_Shell device=%s id=%s>' % (self.device, self.id)

    @property
    def opened(self):
        return self.session and self.session.active and not self.session.closed

    def open(self):
        host = self.device.host
        port = self.device.port

        self.log.debug('opening %s:%s ...' % (host, port))

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(
            host, port, username=self.device.auth['user'], password=self.device.auth['password'])

        self.log.debug('opened %s:%s ...' % (host, port))

        transport = ssh.get_transport()
        self.session = transport.open_session()
        self.session.settimeout(1.)  # Set to non-blocking mode
        self.session.set_combine_stderr(True)
        self.session.get_pty()
        self.session.invoke_shell()

        if self.on_open:
            self.on_open()

        # start process
        self.start()

    def send(self, data):
        if self.session:
            self.log.debug('send data = %s' % str(data))
            return self.session.send(data)

    def close(self):
        self.stop()

    def _close_session(self):
        if self.session:
            self.log.debug('close')
            if self.on_close:
                self.on_close()
            # self.session.send('\x03') # send ^C
            self.session.close()
            self.session = None

    def loop(self):
        if not self.opened:
            return False # exit the loop

        try:
            data = self.session.recv(512)
        except socket.timeout:
            pass
        else:
            if len(data) == 0:
                # closed by server
                self.log.debug('closed by server')
                return False
            self.log.debug('rec data = %s' % str(data))

            self.buffer += data
            if len(self.buffer) > self.BUFFER_SIZE:
                self.buffer = self.buffer[:-self.BUFFER_SIZE]

            self.on_data(data)

    def toJson(self):
        data = super(Interactive_Shell, self).toJson()
        data.update({
            'id': self.id,
            'opened': self.opened,
            'device_id': self.device.id
        })
        return data

    ## process
    def main(self):
        while self.is_running:
            if self.loop() is False:
                break

    def end(self):
        self._close_session()


@pingable()
@attr('auth', type=Dict(mapping = OrderedDict([('user', String(allow_empty=False)), ('password', String(allow_empty=False))])), description="An object describing the credentials to use.")
@attr('port', type=Integer(min=0, max=65535), default=22, description="The port number of the device to connect to. The default port number is 22.")
@attr('host', type=Host(), description="The ip address or hostname of the device to connect to.")
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
