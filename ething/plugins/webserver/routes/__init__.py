# coding: utf-8

from . import static
from . import file
from . import table
from . import device
from . import flow
from . import utils
from . import event
from . import auth
from . import notify
from . import settings
from . import resource
from . import plugin
from . import apikey


def install_routes(**kwargs):

    static.install(**kwargs)
    file.install(**kwargs)
    table.install(**kwargs)
    device.install(**kwargs)
    flow.install(**kwargs)
    utils.install(**kwargs)
    event.install(**kwargs)
    auth.install(**kwargs)
    notify.install(**kwargs)
    settings.install(**kwargs)
    resource.install(**kwargs)
    plugin.install(**kwargs)
    apikey.install(**kwargs)
