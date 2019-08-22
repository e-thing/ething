# coding: utf-8
from .db import *
from .utils.date import TzDate, utcnow
from .Signal import Signal
import datetime


__all__ = ['SUCCESS', 'INFO',
           'WARNING', 'ERROR', 'MODES', 'NotificationSent', 'Notification',
           'list_persistent_notifications', 'remove_persistent_notification', 'notify']


SUCCESS = "success"
INFO = 'info'
WARNING = 'warning'
ERROR = 'error'


MODES = (ERROR, WARNING, INFO, SUCCESS)


@meta(icon='mdi-bell')
class NotificationSent(Signal):
    """
    is emitted each time a notification has been sent
    """
    def __init__(self, notification):
        super(NotificationSent, self).__init__(**notification.__json__()) # must be a dictionary


@attr('timeout', type=Integer(), default=3600, mode=READ_ONLY) # 0 means for ever, unit: seconds
@attr('date', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY)
@attr('queue', type=Nullable(String(allow_empty=False)), mode=READ_ONLY, default=None) # if 2 notifications have the same queue id, only the last one will be kept
@attr('source', type=Nullable(DBLink('resources/Resource')), mode=READ_ONLY, default=None) # the originator of this message
@attr('title', type=Nullable(String(allow_empty=False)), default=None)
@attr('mode', type=String(allow_empty=False), mode=READ_ONLY, default=INFO)
@attr('message', type=String(allow_empty=False), mode=READ_ONLY)
@uid()
@db(table='notifications')
class Notification(Entity):

    def __str__(self):
        msg = self.message
        return '<Notification id=%s msg=%s>' % (self.id, msg[:32] + (msg[32:] and '...') )

    def __repr__(self):
        return str(self)


def list_persistent_notifications(core):
    _clean(core)
    notifications = core.db.os.find(Notification)
    return notifications


def remove_persistent_notification(core, id):
    notification = core.db.os.get(Notification, id)
    if notification:
        remove(notification)
    else:
        raise Exception('Notification not found id=%s' % id)


def _clean(core):
    # remove obsolete notifications
    queue_list = list()
    for notification in core.db.os.find(Notification, sort='-date'):

        # queue
        queue = notification.queue
        if queue is not None:
            if queue in queue_list:
                remove(notification)
                break
            queue_list.append(queue)

        # out-dated
        timeout = notification.timeout
        if timeout > 0 and utcnow() - notification.date > datetime.timedelta(seconds=timeout):
            remove(notification)
            break

        # source does not exists anymore
        try:
            notification.source
        except ValueError:
            remove(notification)
            break


def notify(core, message, mode=INFO, persistant=False, **kwargs):

    # sanitize mode
    mode = mode or INFO
    mode = mode.lower()
    if mode == 'warn':
        mode = 'warning'
    if mode not in MODES:
        mode = INFO

    kwargs['message'] = message
    kwargs['mode'] = mode

    if not persistant:
        kwargs.setdefault('timeout', 10)

    notification = create(Notification, kwargs, context = {
        'core': core
    })

    if persistant:
        core.db.os.save(notification)
        _clean(core)

    core.emit(NotificationSent(notification))

    return notification

