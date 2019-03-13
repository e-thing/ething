import EThingUI from 'ething-ui'
import EThing from 'ething-js'

function guidGenerator() {
    var S4 = function() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    };
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}


var sshSocket = EThingUI.io(EThing.config.serverUrl + '/ssh', {
  autoConnect: false
});

sshSocket.on('connect', () => {
  console.log('[socketio:SSH] connected')
});

sshSocket.on('disconnect', () => {
  console.log('[socketio:SSH] disconnected')
});

sshSocket.on('data', (data) => {
  //console.log('[socketio:SSH] data:', data)

  var shell = interactiveShellManager.get(data.id);

  if (shell) {
      shell._set_incoming_data(data.data)
  }

});

sshSocket.on('opened', (data) => {
  console.log('[socketio:SSH] opened ,', data)

  var shell = interactiveShellManager.get(data.id);

  if (shell) {
      shell._set_opened(data.id, data.buffer)
  }

});

sshSocket.on('closed', (data) => {
  console.log('[socketio:SSH] closed ,', data)

  var shell = interactiveShellManager.get(data.id);

  if (shell) {
      shell._set_closed()
  }

});

var _socket_refs = [];
const SOCKET_RELEASE_DELAY = 10000;
var _socket_close_timer = null;

function lock_socket (id) {
  if (_socket_refs.indexOf(id)!==-1) return;

  _socket_refs.push(id);

  if (_socket_refs.length==1) {
    if (_socket_close_timer!==null) {
      clearTimeout(_socket_close_timer)
      _socket_close_timer = null;
    } else {
      sshSocket.open()
    }
  }

}

function release_socket (id) {
  if (_socket_refs.length>0) {
    var i = _socket_refs.indexOf(id)
    if (i===-1) return;
    _socket_refs.splice(i, 1)
    if (_socket_refs.length==0) {
      _socket_close_timer = setTimeout(() => {
        _socket_close_timer = null
        sshSocket.close()
      }, SOCKET_RELEASE_DELAY)
    }
  }
}

var interactiveShellManager = {
    _shells: {},

    get (id) {
        return this._shells[id]
    },

    add (shell) {
        this._shells[shell.id] = shell
    },

    remove (shell) {
      delete this._shells[shell.id]
    }
}

function InteractiveShell (device, id) {

    this.id = id || guidGenerator()
    this.state = 'closed'

    interactiveShellManager.add(this)

    var _setState = (state) => {
        if (state != this.state) {
            this.state = state
            if (this.onstatechanged) {
                this.onstatechanged.call(this, this.state)
            }
        }
    }

    var _onopen = null;
    var _onclose = null;

    this.open = (onopen) => {
        _setState('opening');

        lock_socket(this)

        _onopen = onopen;

        sshSocket.emit('open', {
            device_id: device.id(),
            id: this.id
        })
    }

    this.close = (onclose) => {
        _setState('closing');

        _onclose = onclose;

        sshSocket.emit('close', {
            id: this.id
        })

        release_socket(this)
    }

    this.send = (data) => {
        sshSocket.emit('send', {
            id: this.id,
            data
        })
    }

    this.destroy = () => {

      if (this.state !== 'closed') {
        sshSocket.emit('detach', {
            id: this.id
        })
      }

      interactiveShellManager.remove(this)
      release_socket(this)
    }

    this._set_opened = (id, buffer) => {
        _setState('opened')

        if (_onopen) {
            _onopen.call(this)
            _onopen = null
        }
        if (this.onopen) {
            this.onopen.call(this)
        }

        if (buffer) {
          this._set_incoming_data(buffer)
        }
    }

    this._set_closed = () => {
        _setState('closed')

        if (_onclose) {
            _onclose.call(this)
            _onclose = null
        }
        if (this.onclose) {
            this.onclose.call(this)
        }
    }

    this._set_incoming_data = (data) => {
        if (this.ondata) {
            this.ondata.call(this, data)
        }
    }

}

export {
  InteractiveShell
}
