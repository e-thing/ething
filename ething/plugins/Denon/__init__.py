from ething.Device import Device
from ething.reg import *
from ething.utils.ping import pingable
from ething.interfaces import Relay
from ething.discovery import mdns
from ething.scheduler import set_interval
import requests
import xmltodict


def install(core, options):

    def discover_handler(alive, info):
        if alive:
            host = info.get('address')
            if not core.find_one(lambda r: r.typeof(Denon) and r.host == host):
                # not already created, so create it !
                core.create(Denon, {
                    'name': 'Marantz M-CR611',
                    'host': host
                })

    mdns.register_service('_http._tcp.local.', discover_handler, 'Marantz M-CR611')


@pingable()
@attr('host', type=Host(), description="The ip address or hostname of the device to connect to.")
class Denon(Relay):
    """
    Denon Device resource representation
    """

    def setState(self, state):
        self.sendCmd('PWON' if state else 'PWSTANDBY')
        self._update()

    @set_interval(30, name="denon.update")
    def _update(self):
        # fetch the status
        status = self.getStatus()
        if status:
            self.state = status.get('item', {}).get('Power', {}).get('value') == 'ON'
        else:
            self.state = False

    def _request(self, path):
        r = None
        online = True
        try:
            r = requests.get(
                "http://%s/%s" % (self.host, path))
        except requests.exceptions.ConnectionError:
            online = False

        self.refresh_connect_state(online)
        return r

    @method
    def setVolumeUp(self):
        """
        turn up the volume
        """
        self.sendCmd('MVUP')

    @method
    def setVolumeDown(self):
        """
        turn down the volume
        """
        self.sendCmd('MVDOWN')

    @method.arg('source', type=Enum(["CD", "TUNER", "IRADIO", "IPD", "BLUETOOTH"]))
    def setSource(self, source):
        """
        select the source
        """
        self.sendCmd('SI' + source)

    @method.return_type('object')
    def getCDStatus(self):
        """
        return the device CD status
        """
        return xmltodict.parse(self.sendPostCmd('GetCDStatus'))

    @method.arg('command', type=Enum(["STOP", "PLAY", "PAUSE", "PREV_TRACK", "NEXT_TRACK"]))
    def setCDControl(self, command):
        """
        control the CD player
        """
        map = {
            'STOP': '00',
            'PLAY': '01',
            'PAUSE': '02',
            'PREV_TRACK': '05',
            'NEXT_TRACK': '06',
        }
        self.sendPostCmd('SetCDControl', map.get(command, '00'))

    @method.return_type('image/jpg')
    def getNetCover(self):
        """
        get the radio cover
        """
        r = self._request("NetAudio/art.asp-jpg")

        if r is not None and r.ok:
            return r.content

    @method.return_type('object')
    def getStatus(self):
        """
        return the device status
        """
        r = self._request("goform/formMainZone_MainZoneXmlStatus.xml")

        if r is not None and r.ok:
            return xmltodict.parse(r.text)

    @method.return_type('object')
    def getNetAudioStatus(self):
        """
        return the device NET status
        """
        return xmltodict.parse(self.sendPostCmd('GetNetAudioStatus'))

    """
     working cmd for marantz M-CR611 :

     PWON
     PWSTANDBY

     MVUP
     MVDOWN
     MV00 // min = mute
     MV08  
     MV20 // loud
     ...

     MUON // mute
     MUOFF

     SICD // CD
     SITUNER // DAB
     SIIRADIO // internet radio
     SISERVER // music server
     SIUSB // front usb
     SIIPD // front usb start playback
     SIBLUETOOTH // bluetooth

     // control online music, usb/ipod bluetooth
     // cf Steuerungsprotokoll_IP_RS232C_AVR-X1200W_AVR-X2200W_AVR-X3200W_AVR-X4200W.pdf
     NS9A // play bluetooth
     NS9C // stop
     ...


    """

    @method.arg('cmd', type='string')
    def sendCmd(self, cmd):
        r = self._request("goform/formiPhoneAppDirect.xml?%s" % cmd)
        if r is not None:
            return r.ok
        else:
            return False

    """
    GetSourceStatus
    GetAllZonePowerStatus
    GetVolumeLevel
    GetMuteStatus
    GetZoneName
    GetNetAudioStatus
    GetSurroundModeStatus
    GetCDStatus

    SetCDControl value: 00 , 01 play, 05 prev, 06 next
    """

    def sendPostCmd(self, cmd, value=None):

        body = '<?xml version="1.0" encoding="utf-8" ?><tx><cmd id="1">%s</cmd>' % cmd

        if value is not None:
            body += '<value>%s</value>' % value

        body += '</tx>'

        online = True
        r = None
        try:
            r = requests.post("http://%s/goform/AppCommand.xml" %
                              self.host, data=body.encode('utf8'))
        except requests.exceptions.ConnectionError:
            online = False

        self.refresh_connect_state(online)

        if r is not None and r.ok:
            return r.text
