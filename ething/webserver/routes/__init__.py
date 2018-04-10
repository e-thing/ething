# coding: utf-8

from . import static
from . import file
from . import table
from . import app
from . import device
from . import rule
from . import utils
from . import event
from . import auth
from . import notify
from . import settings
from . import resource



def install_routes(**kwargs):
    
    static.install(**kwargs)
    file.install(**kwargs)
    table.install(**kwargs)
    app.install(**kwargs)
    device.install(**kwargs)
    rule.install(**kwargs)
    utils.install(**kwargs)
    event.install(**kwargs)
    auth.install(**kwargs)
    notify.install(**kwargs)
    settings.install(**kwargs)
    resource.install(**kwargs)
