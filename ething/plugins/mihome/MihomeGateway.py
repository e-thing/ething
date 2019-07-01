# coding: utf-8

from ething.core.reg import *
from ething.core.interfaces import RGBWLight, LightSensor
from .MihomeBase import MihomeBase
import json
import colorsys


musicMap = ["Police siren", "Police siren 2", "Accident tone", "Missle countdown", "Ghost", "Sniper", "War", "Air Strike", "Barking dogs", "Doorbell ring tone", "Knock on door",
            "Hilarious", "Alarm clock", "MiMix", "Enthusiastic", "GuitarClassic", "IceWorldPiano", "LeisureTime", "Childhood", "MorningStreamlet", "MusicBox", "Orange", "Thinker"]


@attr('ip', type=String(allow_empty=False), description="The IP address of the gateway")
@attr('password', type=String(allow_empty=True), default="", description="The password of the gateway")
@attr('token', mode=PRIVATE, default='')
class MihomeGateway(MihomeBase, RGBWLight, LightSensor):

    def _get_gateway(self):
        return self

    def _processData(self, response):
        
        if 'token' in response:
            self.token = response['token']

        if 'data' in response:
            data = json.loads(response['data'])

            if 'rgb' in data:
                rgb = data['rgb'] & 0xffffff
                brightness = data['rgb'] >> 24
                h = format(rgb, '06X')
                rgb = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
                hue, sat, _ = colorsys.rgb_to_hsv(*rgb)
                self.hue = hue * 360.
                self.saturation = sat * 100.
                self.level = int(brightness)

            if 'illumination' in data:
                self.light_level = int(data['illumination']) - 300  # lm

        if response.get('cmd') == 'iam':
            def read(result, gateway):
                list_sid = json.loads(result.data['data'])
                for sid in list_sid:
                    self.controller.send({"cmd": "read", "sid": sid}, ip=self.ip, ack = False)

            self.controller.send({"cmd": "get_id_list", 'sid': self.sid}, ip=self.ip, done = read)

    def setLevel(self, level):
        r, g, b = colorsys.hsv_to_rgb(self.hue / 360., self.saturation / 100., 1.)
        hrgb = int('%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255)), 16)
        hrgb = hrgb | (level << 24)

        self._write({
            "rgb": hrgb
        }, done = lambda _, device : super(MihomeGateway, self).setLevel(level))

    def setColor(self, hue, saturation):
        r, g, b = colorsys.hsv_to_rgb(hue/360., saturation/100., 1.)
        hrgb = int('%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255)), 16)
        hrgb = hrgb | (self.level << 24)

        self._write({
            "rgb": hrgb
        }, done=lambda _, device: super(MihomeGateway, self).setColor(hue, saturation))

    @method.arg('music', enum=musicMap)
    @method.arg('volume', minimum=0, maximum=100)
    def playMusic(self, music="Police siren", volume=50):
        """
        start some music
        """

        if isinstance(music, string_types):
            music = str(music)
            if music in musicMap:
                music = musicMap.index(music)
            else:
                raise Exception('music unknown: %s' % music)

        self._write({
            "mid": music,
            "vol": volume
        })

    @method
    def stopMusic(self):
        """
        stop the music
        """
        self._write({
            "mid": 10000
        })
