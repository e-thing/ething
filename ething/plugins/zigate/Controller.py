# coding: utf-8
from future.utils import string_types

from .helpers import model_info, hex2str
from .Message import Message
import time


class Controller(object):

    AUTOCONNECT_PERIOD = 15  # seconds
    RESPONSE_TIMEOUT = 10  # seconds

    reset_attr = ['port']

    def __init__(self, gateway, transport):

        self._gateway = gateway
        self._ething = gateway.ething
        self._isOpened = False

        self._log = gateway.ething.log

        self._lastState = False
        self._lastAutoconnectLoop = 0
        self._preventFailConnectLog = 0

        # response management
        self._responseListeners = []

        self._initialized = False

        self._cache = {}

        # refresh the gateway each time the gateway properties changes
        self.ething.signalManager.bind(
            'ResourceUpdated', self.onResourceUpdated)

        self.ething.scheduler.tick(self.update)

        self._transport = transport(self)

    def __del__(self):
        self.destroy()

    @property
    def gateway(self):
        return self._gateway

    @property
    def ething(self):
        return self._ething

    @property
    def log(self):
        return self._log

    @property
    def isOpened(self):
        return self._isOpened

    @property
    def transport(self):
        return self._transport

    def onResourceUpdated(self, signal):
        if signal['resource'] == self.gateway.id and signal['rModifiedDate'] > self.gateway.modifiedDate:
            self.gateway.refresh()

            for attr in signal['attributes']:
                if attr in Controller.reset_attr:
                    self.restart()
                    break

    def restart(self):
        if self.isOpened:
            self.close()
            self.open()

    def destroy(self):
        self.close()
        self.ething.signalManager.unbind(
            'ResourceUpdated', self.onResourceUpdated)

    def open(self):

        self._initialized = False

        try:
            self.transport.open()
        except Exception as e:
            self.log.error(e)
            return False

        self._lastAutoconnectLoop = 0
        self.gateway.setConnectState(True)
        self._isOpened = True
        return True

    def close(self):

        self.transport.close()

        self._initialized = False

        self._isOpened = False
        self.gateway.setConnectState(False)

        for responseListener in self._responseListeners:
            responseListener['callback']('disconnected', None)
        self._responseListeners = []

        return True

    def createDevice(self, addr, model):
        device = None

        self.log.info("Zigate: create device addr: %s, model: %s" %
                      (addr, model))

        info = model_info(model)

        if info:

            attr = self.fetch(addr, ['model', 'manufacturer'])

            attr['name'] = info.name
            attr['address'] = info.addr
            attr['createdBy'] = self.gateway.id

            try:
                device = self.ething.create(info.cls.__name__, attr)
            except:
                self.log.exception(
                    "Zigate: unable to create the device %s" % model)

        else:
            self.log.warning(
                "Zigate: unable to create the device, unknown model = %s" % model)

        return device

    def init(self):

        self.log.info("Zigate: starting init ...")

        def get_version_cb(error, response):
            if not error:
                # ZiGate - set channel 11
                self.send(Message("0021", "00000800"), set_channel_cb)
            else:
                self.log.error("Zigate: init failed (get version)")

        def set_channel_cb(error, response):
            if not error:
                # ZiGate - Set Type COORDINATOR
                self.send(Message("0023", "00"), set_type_cb)
            else:
                self.log.error("Zigate: init failed (set channel)")

        def set_type_cb(error, response):
            if not error:
                # ZiGate - start network
                self.send(Message("0024", ""), start_network_cb, '8024')
            else:
                self.log.error("Zigate: init failed (set type)")

        def start_network_cb(error, response):
            if not error:
                self._initialized = True
                self.log.info("Zigate: init succeed")
            else:
                self.log.error("Zigate: init failed (start network)")

        # get version
        self.send(Message("0010"), get_version_cb, True)

    def store(self, addr, attr):
        # bind data to a device for later purpose
        # kind of a cache

        if addr not in self._cache:
            self._cache[addr] = {
                'ts': 0,
                'data': {}
            }

        self._cache[addr]['ts'] = time.time()
        self._cache[addr]['data'].update(attr)

    def fetch(self, addr, attr):
        data = {}

        if addr in self._cache:
            data = self._cache[addr].get('data', {})

        return [data.get(k) for k in attr]

    def processMessage(self, packet):

        self.log.debug("Zigate: packet received : %s" %
                       packet.toHumanReadable())

        type = packet.type
        sqn = packet['sqn']

        # handle response callback
        if type == "8000":  # status

            status = packet['status']
            success = (status == '00')

            i = 0
            while i < len(self._responseListeners):
                responseListener = self._responseListeners[i]

                if responseListener['sqn'] is False:

                    responseListener['sqn'] = sqn
                    responseListener['status'] = status

                    if (not responseListener['waitResponse']) or (not success):

                        statusStr = None

                        if status == '00':
                            statusStr = 'Success'
                        elif status == '01':
                            statusStr = 'Incorrect Parameters'
                        elif status == '02':
                            statusStr = 'Unhandled Command'
                        elif status == '03':
                            statusStr = 'Command Failed'
                        elif status == '04':
                            statusStr = 'Busy'
                        elif status == '05':
                            statusStr = 'Stack Already Started'
                        else:
                            statusStr = "ZigBee Error Code %s" % status

                        # remove this item
                        self._responseListeners.pop(i)
                        i -= 1

                        if callable(responseListener['callback']):
                            responseListener['callback'](
                                False if success else statusStr, None)

                    break

                i += 1

        else:

            i = 0
            while i < len(self._responseListeners):
                responseListener = self._responseListeners[i]

                if responseListener['sqn'] == sqn or responseListener['responseId'] == type:

                    # remove this item
                    self._responseListeners.pop(i)
                    i -= 1

                    if callable(responseListener['callback']):
                        responseListener['callback'](False, packet)

                    break

                i += 1

        device = None
        addr = packet['srcAddr']

        if addr:

            device = self.gateway.getDevice(addr)

            if not device:
                self.log.warning(
                    "Zigate: receive a message from an unknown device, addr: %s" % addr)

        if type == "8010":  # Version

            self.gateway.appVersion = packet['appVersion']
            self.gateway.sdkVersion = packet['sdkVersion']

        elif type == "004d":  # device announce

            """
            6F 2F = Short address ( adresse utilise dans le reseau)
            00 15 8D 00 01 29 15 C6 = Adresse MAC IEEE
            80 = Mac capability
            """

            self.store(addr, {
                'address': addr
            })

            # send request 0x0043 . Simple Descriptor request
            # in order to get some information about this device !

        elif type == "8102":  # Report Individual Attribute report

            if packet['clusterId'] == "0000":  # General: basic

                attrId = packet['attrId']

                if attrId == "0005":  # model identifier
                    model = hex2str(packet['data'])

                    self.store(addr, {'model': model})

                    self.log.info("Zigate: ZigateRead - model : %s" % model)

                    if not device:
                        device = self.createDevice(addr, model)

                elif attrId == "0004":  # manufacturer name
                    manufacturer = hex2str(packet['data'])

                    self.store(addr, {'manufacturer': manufacturer})

                    self.log.info(
                        "Zigate: ZigateRead - manufacturer : %s" % manufacturer)

                elif attrId == "0007":  # power source
                    powerSource = int(packet['data'][0:2], 16)
                    powerSource = powerSource & 0x7F
                    powerSourceStr = ''

                    if powerSource == 0x01:
                        powerSourceStr = 'Mains (single phase)'
                    elif powerSource == 0x02:
                        powerSourceStr = 'Mains (3 phase)'
                    elif powerSource == 0x03:
                        powerSourceStr = 'Battery'
                    elif powerSource == 0x04:
                        powerSourceStr = 'DC source'
                    elif powerSource == 0x05:
                        powerSourceStr = 'Emergency mains constantly powered'
                    elif powerSource == 0x06:
                        powerSourceStr = 'Emergency mains and transfer switch'

                    if powerSourceStr:
                        self.store(addr, {'powerSource': powerSourceStr})

                    self.log.info(
                        "Zigate: ZigateRead - powerSource : %d (%s)" % (powerSource, powerSourceStr))

                """
                else if( $packet->clusterId=="0006" ){  // General: On/Off xiaomi

                //SetSwitch(MsgSrcAddr,MsgSrcEp,MsgClusterData,16)
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Switch",MsgClusterData)
                
            
            } else if( $packet->clusterId=="0402" ){  // Measurement: Temperature xiaomi
                $value = hexdec(substr($MsgClusterData, -8, 4));
                $value = $value / 100;
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Temperature",round(int(MsgValue,16)/100,1))
                
                self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception temperature : " . $value );
                        
            } else if( $packet->clusterId=="0403" ){  // Measurement: Pression atmospherique xiaomi   ////// a corriger/modifier http://zigate.fr/xiaomi-capteur-temperature-humidite-et-pression-atmospherique-clusters/
                if( str(Data[28:32])=="0028"){
                    //MsgValue=Data[len(Data)-6:len(Data)-4] ////bug !!!!!!!!!!!!!!!!
                    $value = hexdec(substr($MsgClusterData, -6, 2));
                    //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgValue,8))
                    
                    self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception atm : " . $value );
                }    
                if( str(Data[26:32])=="000029"){
                    //MsgValue=Data[len(Data)-8:len(Data)-4]
                    $value = hexdec(substr($MsgClusterData, -8, 4));
                    $value = $value / 100;
                    //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgValue,16),1))
                    
                    self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception atm : " . $value);
                }    
                if( str(Data[26:32])=="100029"){
                    //MsgValue=Data[len(Data)-8:len(Data)-4]
                    $value = hexdec(substr($MsgClusterData, -8, 4));
                    $value = $value / 10;
                    //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Barometer",round(int(MsgValue,16)/10,1))
                    
                    self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception atm : " . $value);
                }
            } else if( $packet->clusterId=="0405" ){  // Measurement: Humidity xiaomi
                //MsgValue=Data[len(Data)-8:len(Data)-4]
                $value = hexdec(substr($MsgClusterData, -8, 4));
                $value = $value / 100;
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Humidity",round(int(MsgValue,16)/100,1))
                
                self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception hum : " . $value );
        
            } else if( $packet->clusterId=="0406" ){  // (Measurement: Occupancy Sensing) xiaomi
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Switch",MsgClusterData)
                
                self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception Occupancy Sensor : " . $MsgClusterData );

            } else if( $packet->clusterId=="0400" ){  // (Measurement: LUX) xiaomi
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Lux",str(int(MsgClusterData,16) ))
                
                self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception LUX Sensor : " . $MsgClusterData );
                
                
            } else if( $packet->clusterId=="0012" ){  // Magic Cube Xiaomi
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Switch",MsgClusterData)
                
                self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception Xiaomi Magic Cube Value : " . $MsgClusterData );
                
            } else if( $packet->clusterId=="000c" ){  // Magic Cube Xiaomi rotation
                //MajDomoDevice(MsgSrcAddr,MsgSrcEp,"Vert Rot",MsgClusterData)
                
                self.log.debug("Zigate: ZigateRead - MsgType 8102 - reception Xiaomi Magic Cube Value Vert Rot : " . $MsgClusterData );
                
                
                        """

        if device:
            with device:
                device.onMessage(packet)
                device.setConnectState(True)

    def update(self):
        # do some stuff regularly
        now = time.time()

        # check for a deconnection
        if self.isOpened != self._lastState:
            if not self.isOpened:
                self.log.info("Zigate: disconnected")
            else:
                self.init()
        self._lastState = self.isOpened

        # autoconnect
        if not self.isOpened and (now - self._lastAutoconnectLoop) > Controller.AUTOCONNECT_PERIOD:
            try:
                self._lastAutoconnectLoop = now
                self.open()
                self._preventFailConnectLog = 0
            except Exception as e:
                self.gateway.setConnectState(False)

                if self._preventFailConnectLog % 20 == 0:
                    self.log.exception("Zigate: unable to connect")
                self._preventFailConnectLog += 1

        # check for timeout !
        i = 0
        while i < len(self._responseListeners):
            responseListener = self._responseListeners[i]

            if now - responseListener['ts'] > Controller.RESPONSE_TIMEOUT:

                # remove this item
                self._responseListeners.pop(i)
                i -= 1

                responseListener['callback']('response timeout', None)

            i += 1

    def send(self, message, callback=None, waitResponse=None):

        self.log.debug("Zigate: send %s" % message.toHumanReadable())

        self.transport.write(message.build())

        responseId = None

        if waitResponse:
            if isinstance(waitResponse, string_types):
                responseId = waitResponse.rjust(4, "0").upper()
            else:
                responseId = format("04X", (int(message.type, 16) | 0x8000))

        self._responseListeners.append({
            'callback': callback,
            'ts': time.time(),
            'message': message,
            'status': False,
            'sqn': False,
            'responseId': responseId,
            'waitResponse': bool(waitResponse)
        })
