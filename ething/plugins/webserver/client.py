# coding: utf-8
from ething.core.flow import *
from ething.core.dbentity import *
from ething.core.utils.date import TzDate, utcnow
from flask import request


table_name = 'clients'


@attr('modifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY)
@attr('browser', mode=READ_ONLY, default=None)
@attr('platform', mode=READ_ONLY, default=None)
@attr('ip', mode=READ_ONLY, default=None)
@attr('online', mode=READ_ONLY, default=False)
@attr('name', type=String(allow_empty=False), default="anonymous")
@attr('id', mode=READ_ONLY)
class Client(DbEntity):

    def __init__(self, data, create=True, context=None):
        if 'app' not in context:
            raise Exception('missing "app" in context')

        app = context.get('app')

        if 'ething' not in context:
            context['ething'] = app.core # necessary for TzDate.toJson(...)

        super(Client, self).__init__(data, create, context)

        object.__setattr__(self, '_Client__app', app)
        object.__setattr__(self, '_Client__sio', set())

    def __str__(self):
        return '<Client id=%s name=%s ip=%s>' % (self.id, self.name, self.ip)

    def __repr__(self):
        return str(self)

    @property
    def sockets(self):
        return list(self.__sio)

    def attach_socket(self, sid):
        if sid not in self.__sio:
            self.__sio.add(sid)
            if len(self.__sio) == 1:
                self.__app.log.debug('client online %s' % self)
                self.online = True

    def detach_socket(self, sid):
        if sid in self.__sio:
            self.__sio.remove(sid)
            if len(self.__sio) == 0:
                self.online = False
                self.__app.log.debug('client offline %s' % self)

    def update_from_request(self):
        """must be executed in a flask context"""
        with self:
            self.attach_socket(request.sid)
            user_agent = request.user_agent
            self.online = True
            self.ip = request.remote_addr
            self.platform = user_agent.platform
            self.browser = '%s %s' % (user_agent.browser, user_agent.version)

    def notify(self, message):
        data = {
            'msg': message
        }

        for sid in self.__sio:
            self.__app.socketio.emit('notification', data, room=sid, namespace='/notifications')

    @property
    def db(self):
        return self.__app.core.db

    def _insert(self):
        self.db.insert_table_row(table_name, self.serialize())
        self.__app.clients.append(self)

    def _before_save(self):
        self.modifiedDate = utcnow()  # update the modification time

    def _save(self, dirty_attrs):
        self.db.update_table_row(table_name, self.id, self.serialize(), False)

    def _remove(self):
        self.db.remove_table_row(table_name, self.id, False)
        try:
            self.__app.clients.remove(self)
        except ValueError:
            pass


def install (app):

    app.get_client = lambda cid: get_client(app, cid)

    def _notify_client(*args, **kwargs):
        return notify_client(app, *args, **kwargs)

    app.notify_client = _notify_client

    app.clients = []
    db = app.core.db
    if not db.table_exists(table_name):
        db.create_table(table_name)
    for doc in db.get_table_rows(table_name):
        try:
            app.clients.append(Client.unserialize(doc, context={'app': app}))
        except:
            pass

    @app.socketio.on('disconnect')
    def client_disc():
        sid = request.sid
        for cl in app.clients:
            cl.detach_socket(sid)

    @app.socketio.on('init', namespace='/notifications')
    def client_init_handler(data):
        cid = data['cid']
        cl = get_client(app, cid)
        if not cl:
            cl = create_client(app, cid)
            app.clients.append(cl)

        cl.update_from_request()


def get_client(app, cid):
    for cl in app.clients:
        if cl.id == cid:
            return cl


def create_client(app, cid):
    return Client.create({'id': cid}, context={'app': app})


def notify_client(app, message, cid=None):

    if cid is None:
        data = {
            'msg': message
        }
        app.socketio.emit('notification', data, namespace='/notifications')
        return

    cl = get_client(app, cid)
    if cl is not None:
        cl.notify(message)


@meta(icon='mdi-bell', category='notification')
@attr('message', type=Descriptor(('text', 'msg', 'flow', 'glob', 'env')), description='The message of the notification')
class NotifyClient(Node):
    INPUTS = ['default']

    def main(self, **inputs):
        msg = inputs.get('default')
        self.ething.get_plugin('webserver').app.notify_client(self.message)
