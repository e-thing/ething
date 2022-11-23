# coding: utf-8

from . import core
from . import static
from . import file
from . import table
from . import flow
from . import utils
from . import event
from . import auth
from . import settings
from . import resource
from . import plugin
from . import apikey
from . import client
from . import notification


# todo: async
async def install_routes(**kwargs):
    core.install(**kwargs)
    static.install(**kwargs)
    file.install(**kwargs)
    table.install(**kwargs)
    flow.install(**kwargs)
    utils.install(**kwargs)
    event.install(**kwargs)
    auth.install(**kwargs)
    settings.install(**kwargs)
    resource.install(**kwargs)
    plugin.install(**kwargs)
    apikey.install(**kwargs)
    await client.install(**kwargs)
    notification.install(**kwargs)
