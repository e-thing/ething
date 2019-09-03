# coding: utf-8
from .db import *
from .utils.date import utcnow
from .utils import generate_id
from .Signal import Signal
import datetime
import logging


__all__ = ['SUCCESS', 'INFO',
           'WARNING', 'ERROR', 'MODES', 'NotificationSent',
           'NotificationManager']


LOGGER = logging.getLogger(__name__)


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
    pass


class NotificationManager(object):

    def __init__(self, core, source=None):
        self._core = core
        self._source = source
        self._table = core.db['notifications']

    def _clean(self):
        now = utcnow()

        for doc_id in list(self._table):
            doc = self._table[doc_id]
            timeout = doc.get('timeout', 0)
            if timeout > 0 and now - doc['date'] > datetime.timedelta(seconds=timeout):
                del self._table[doc_id]

    def notify(self, message, mode=INFO, timeout=0, id=None, title=None, source=None):
        self._clean()

        if timeout < 0:
            raise ValueError('timeout is < 0')

        notification = None

        to_be_removed = len(message)==0

        if to_be_removed:

            if id is None:
                LOGGER.error('no id given')
                return

            if id in self._table:
                del self._table[id]
                self._core.emit(NotificationSent(message='', id=id))

        else:

            # send a notification

            if source is None:
                source = self._source

            attr = {
                'message': message,
                'mode': mode,
                'timeout': timeout,
                'title': title,
                'source': getattr(source, 'id', None) if source is not None else None,
                'date': utcnow(),
                'id': id or generate_id()
            }

            if id is not None:
                if id in self._table:
                    # update it
                    self._table.update(attr)
                    notification = self._table[id]

            if not notification:
                # create it !
                notification = self._table.insert(attr)

            self._core.emit(NotificationSent(**notification))

            return notification['id']

    def success(self, message, timeout=0, id=None, title=None, source=None):
        return self.notify(message, mode=SUCCESS, timeout=timeout, id=id, title=title, source=source)

    def error(self, message, timeout=0, id=None, title=None, source=None):
        return self.notify(message, mode=ERROR, timeout=timeout, id=id, title=title, source=source)

    def info(self, message, timeout=0, id=None, title=None, source=None):
        return self.notify(message, mode=INFO, timeout=timeout, id=id, title=title, source=source)

    def warning(self, message, timeout=0, id=None, title=None, source=None):
        return self.notify(message, mode=WARNING, timeout=timeout, id=id, title=title, source=source)

    warn = warning

    def remove(self, id):
        self.notify('', id=id)

    def find(self, filter=None):
        self._clean()
        return self._table.select(filter_fn=filter)

