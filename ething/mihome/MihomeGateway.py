# coding: utf-8
from future.utils import string_types



from ething.Device import Device, method, attr, isString, isInteger, isNone, PRIVATE
from ething.interfaces import RGBWLight
from .helpers import IV
import pyaes
import binascii
import math
import json


def just16(str):
    return str.ljust(int(math.ceil(len(str)/16.))*16)


musicMap = ["Police siren", "Police siren 2", "Accident tone", "Missle countdown", "Ghost", "Sniper", "War", "Air Strike", "Barking dogs", "Doorbell ring tone", "Knock on door", "Hilarious", "Alarm clock", "MiMix", "Enthusiastic", "GuitarClassic", "IceWorldPiano", "LeisureTime", "Childhood", "MorningStreamlet", "MusicBox", "Orange", "Thinker"]


@attr('sid', validator = isString(allow_empty = False), description = "The uniq sid of the gateway")
@attr('ip', validator = isString(allow_empty = False), description="The IP address of the gateway")
@attr('password', validator = isString(allow_empty = True), default = "", description="The password of the gateway")
@attr('token', mode = PRIVATE, default = '')
class MihomeGateway(Device, RGBWLight):
    
    
    def getGatewayKey (self):
        aes = pyaes.AESModeOfOperationCBC(just16(self.password).encode('utf8'), iv = IV)
        ciphertext = aes.encrypt(just16(self._token))
        return binascii.hexlify(ciphertext).decode('utf8')
    
    
    def processData (self, response):
        
        if 'token' in response :
            self._token = response['token']
        
        
        data = json.loads(response['data'])
        
        attr = {}
        
        if data:
            
            if 'rgb' in data:
                rgb = data['rgb'] & 0xffffff
                brightness = data['rgb'] >> 24
                
                attr['color'] = '#' + format(rgb, '06X')
                attr['brightness'] = brightness
            
            
            if 'illumination' in data:
                attr['illumination'] = int(data['illumination']) - 300 # lm
            
        
        if attr :
            self.store(None, attr)
        
    
    
    def sendCommand (self, cmd):
        return self.ething.rpc.request('device.mihome.send', self.id, cmd)
    
    
    def getLevel(self):
        return self.data.get('brightness', 0)
    
    def setLevel(self, level):
        hrgb = int(self.data.get('color', '#FFFFFF')[1:], 16)
        
        hrgb = hrgb | (level << 24)
        
        self.sendCommand({
            "cmd" : "write",
            "model" : "gateway",
            "sid" : self.sid,
            "short_id" : 0,
            "data" : {
                "rgb" : hrgb
            }
        })
    
    def getColor(self):
        return self.data.get('color', '#000000')
    
    def setColor(self, color):
        
        hrgb = int(color.replace('#','').replace('0x', ''), 16) if isinstance(color, string_types) else color
        
        hrgb = hrgb | (self.data.get('brightness', 100) << 24)
        
        self.sendCommand({
            "cmd" : "write",
            "model" : "gateway",
            "sid" : self.sid,
            "short_id" : 0,
            "data" : {
                "rgb" : hrgb
            }
        })
    
    @method.arg('music', enum = musicMap)
    @method.arg('volume', minimum = 0, maximum = 100)
    def playMusic(self, music = "Police siren", volume = 50):
        """
        start some music
        """
        
        if isinstance(music, string_types):
            music = str(music)
            if music in musicMap:
                music = musicMap.index(music)
            else:
                raise Exception('music unknown: %s' % music)
        
        self.sendCommand({
            "cmd" : "write",
            "model" : "gateway",
            "sid" : self.sid,
            "short_id" : 0,
            "data" : {
                "mid" : music,
                "vol": volume
            }
        })
    
    @method
    def stopMusic(self):
        """
        stop the music
        """
        
        self.sendCommand({
            "cmd" : "write",
            "model" : "gateway",
            "sid" : self.sid,
            "short_id" : 0,
            "data" : {
                "mid" : 10000
            }
        })


