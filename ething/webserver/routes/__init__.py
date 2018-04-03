
import static
import file
import table
import app
import device
import rule
import utils
import event
import auth
import notify
import settings
import resource



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
