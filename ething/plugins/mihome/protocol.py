# coding: utf-8
from ething.core.TransportProcess import Protocol
from ething.core.utils.date import utcnow
from .helpers import *
from .MihomeDevice import mihome_device_classes
import time
import datetime



class MihomeProtocol(Protocol):
    RESPONSE_TIMEOUT = 10  # seconds

    def __init__(self, core):
        super(MihomeProtocol, self).__init__()
        self.core = core

        # response management
        self._responseListeners = []

    def connection_made(self):
        super(MihomeProtocol, self).connection_made()
        self._responseListeners = []

        self.core.scheduler.set_interval(1, self.check_timeout, condition=lambda _: len(self._responseListeners)>0)

        self.search()


    def data_received(self, from_tupple):
        data, addr = from_tupple

        self.log.debug("Mihome: receive data from %s : %s", str(addr), data)

        data = data.decode("utf-8")
        ip = addr[0]

        response = json.loads(data)

        if isinstance(response, dict):
            
            sid = response.get('sid')
            cmd = response.get('cmd')
            model = response.get('model')
            device = None

            #
            # 1 - retrieve the device from the sid
            #
            if sid:
                device = self.core.find_one(lambda r: r.typeof('resources/MihomeBase') and r.sid == sid)

                if not device and model is not None:
                    # try to create a new device from the incoming data !
                    # we only need sid and model.

                    attributes = {
                        'sid': sid,
                        'model': model,
                        'short_id': response.get('short_id', 0),
                        'name': model
                    }

                    if model == 'gateway':
                        # concerning a gateway
                        attributes.update({'ip': ip})
                        device = self.core.create('resources/MihomeGateway', attributes)

                    else:
                        # concerning a device

                        gateway = self.core.find_one(lambda r: r.typeof('resources/MihomeGateway') and r.ip == ip)

                        if gateway:

                            attributes.update({
                                'createdBy': gateway.id,
                            })

                            for cls in mihome_device_classes:
                                try:
                                    if cls.isvalid(gateway, model):
                                        device = self.core.create(cls, attributes)
                                        break
                                except:
                                    self.log.exception('mihome cls create exception')
                            else:
                                self.log.warning('unable to create the device: no associated class found for model: %s' % model)

                        else:
                            self.log.warning(
                                "Mihome: gateway not found with ip=%s" % (ip,))

                    if not device:
                        self.log.error(
                            "Mihome: unable to create the device model: %s , sid:%s" % (model, sid))


                #
                # 2 - parse the packet
                #
                if device:
                    with device:
                        device.refresh_connect_state(True)
                        device._processData(response)

                if '_ack' in cmd:

                    # response ?

                    i = 0
                    while i < len(self._responseListeners):
                        responseListener = self._responseListeners[i]

                        if responseListener.command.get('sid') == sid and responseListener.ack == cmd:

                            # remove this item
                            self._responseListeners.pop(i)
                            i -= 1

                            responseListener.resolve(response, args = (device, ))

                        i += 1

    def send(self, command, ip = None, port = None, done = None, ack = True, err = None):
        ip = ip or MULTICAST_ADDRESS
        port = port or MULTICAST_PORT

        if ack is True:
            ack = command.get('cmd', '') + '_ack'

        result = Result(ack, command=command, done=done, err=err)

        if self.transport.is_open:

            self.log.debug("command send %s", str(command))

            try:
                self.transport.write(json.dumps(command).encode("utf-8"), (ip, port))
            except Exception as e:
                self.log.exception('send error')
                result.reject('send error: %s' % str(e))
            else:
                if ack:
                    self._responseListeners.append(result)
                else:
                    result.resolve()
        else:
            result.reject('not connected')

        return result

    def connection_lost(self, exc):

        self.core.scheduler.unbind(self.check_timeout)

        for responseListener in self._responseListeners:
            responseListener.reject('disconnected')
        self._responseListeners = []

        super(MihomeProtocol, self).connection_lost(exc)

    def check_timeout(self):
        # check for timeout !
        now = time.time()

        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener.send_ts > self.RESPONSE_TIMEOUT:
                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                self.log.debug("command timeout for : %s", str(responseListener.command.get('cmd')))

                responseListener.reject('response timeout')

            i += 1

    def search(self):
        self.log.debug('search...')
        self.send({"cmd":"whois"}, port = SERVER_PORT, ack = False)



