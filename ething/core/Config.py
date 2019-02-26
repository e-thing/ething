# coding: utf-8
from pytz import common_timezones
from .reg import *


@attr('timezone', type=Enum(common_timezones), default='UTC', description="Set the application timezone.")
class Config(Entity):

    def __init__(self, core):
        # get the config from the core db
        config = core.db.store.get('config', None)

        super(Config, self).__init__(config, {
            'core': core
        }, data_src='db')

    def __transaction_end__(self):
        if is_dirty(self):
            updated_keys = [a.name for a in list_dirty_attr(self)]

            self.core.db.store['config'] = serialize(self)
            clean(self)

            self.core.log.info('config updated: %s' % updated_keys)

    def __str__(self):
        return '<config>'

    def __repr__(self):
        return str(self)
