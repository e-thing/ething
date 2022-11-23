# coding: utf-8
from ething.db import *
from ething.utils.date import TzDate, utcnow
from flask import request
import logging


LOGGER = logging.getLogger(__name__)


@attr('modifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY)
@attr('browser', mode=READ_ONLY, default=None)
@attr('platform', mode=READ_ONLY, default=None)
@attr('ip', mode=READ_ONLY, default=None)
@attr('online', mode=READ_ONLY, default=False)
@attr('name', type=String(allow_empty=False), default="anonymous")
@attr('id', mode=READ_ONLY)
@db(table='clients')
class Client(Entity):

    def __init__(self, data, context=None):
        if 'app' not in context:
            raise Exception('missing "app" in context')

        super(Client, self).__init__(data, context)

        self.__sio = set()

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
                LOGGER.debug('client online %s', self)
                self.online = True

    def detach_socket(self, sid):
        if sid in self.__sio:
            self.__sio.remove(sid)
            if len(self.__sio) == 0:
                self.online = False
                LOGGER.debug('client offline %s', self)

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
            self.app.socketio.emit('notification', data, room=sid, namespace='/notifications')

    def remove(self):
        remove(self)
    
    def __db_save__(self, insert):
        self.modifiedDate = utcnow()  # update the modification time


# todo: make it async
async def install (app):

    app.get_client = lambda cid: get_client(app, cid)

    def _notify_client(*args, **kwargs):
        return notify_client(app, *args, **kwargs)

    app.notify_client = _notify_client

    # load clients database
    await app.core.db.os.load(Client)

    app.core.db.os[Client].update_context({
        'app': app
    })
    app.clients = app.core.db.os.find(Client)

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
    return app.core.db.os.create(Client, {'id': cid})


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

