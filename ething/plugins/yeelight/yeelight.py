# coding: utf-8

from future.utils import listvalues
import socket
import struct
import re
import colorsys
from ething.TransportProcess import AsyncResult
import math


MULTICAST_ADDRESS = '239.255.255.250'
MULTICAST_PORT = 1982
PORT = 55443


def scan():
    """
    scan Yeelight devices on the local network
    returns :
    array(1) {
      [0]=>
      array(13) {
        ["ip"]=>
        string(11) "192.168.1.2"
        ["Cache-Control"]=>
        string(12) "max-age=3600"
        ["Location"]=>
        string(28) "yeelight://192.168.1.2:55443"
        ["id"]=>
        int(56763690)
        ["model"]=>
        string(5) "color"
        ["fw_ver"]=>
        int(52)
        ["power"]=>
        string(3) "off"
        ["bright"]=>
        int(100)
        ["color_mode"]=>
        int(2)
        ["ct"]=>
        int(2420)
        ["rgb"]=>
        int(15512576)
        ["hue"]=>
        int(0)
        ["sat"]=>
        int(100)
      }
    }
    """

    bulbs = {}
    package = "M-SEARCH * HTTP/1.1\r\nST:wifi_bulb\r\nMAN:\"ssdp:discover\"\r\n"
    s = None

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO,
                         struct.pack('LL', 2, 0))
            s.setsockopt(socket.SOL_SOCKET, socket.IP_MULTICAST_TTL, 32)

            if s.sendto(package, (MULTICAST_ADDRESS, MULTICAST_PORT)):

                while True:
                    buf, remote_ip_port = s.recvfrom(2048)

                    if not buf:
                        break

                    if buf[:15] == "HTTP/1.1 200 OK":

                        bulb = {
                            'ip': remote_ip_port[0],
                            'port': remote_ip_port[1]
                        }

                        for line in buf.splitlines():

                            matches = re.search('^([^:]+):\s*(.+)\s*$', line)
                            if matches:

                                value = matches.group(2)

                                try:
                                    value = int(value)
                                except ValueError:
                                    pass

                                bulb[matches.group(1)] = value

                        bulbs[remote_ip_port[0]] = bulb

    except socket.error as e:
        pass
    finally:
        if s:
            s.close()

    return listvalues(bulbs)


def convert_K_to_RGB(colour_temperature):
    """
    Converts from K to RGB, algorithm courtesy of
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
    """
    # range check
    if colour_temperature < 1000:
        colour_temperature = 1000
    elif colour_temperature > 40000:
        colour_temperature = 40000

    tmp_internal = colour_temperature / 100.0

    # red
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        if tmp_red < 0:
            red = 0
        elif tmp_red > 255:
            red = 255
        else:
            red = tmp_red

    # green
    if tmp_internal <= 66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green

    # blue
    if tmp_internal >= 66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        if tmp_blue < 0:
            blue = 0
        elif tmp_blue > 255:
            blue = 255
        else:
            blue = tmp_blue

    return red, green, blue


COLOR_RGB = 1
COLOR_TEMP = 2
COLOR_HSV = 3

def parse_color(props):
    """

    :param props:
    :return: hue [0-360], saturation [0-100]
    """
    color_mode = int(props.get('color_mode', 1))

    if color_mode == COLOR_RGB:

        rgb = int(props.get('rgb', 0))

        r = (rgb >> 16) & 255
        g = (rgb >> 8) & 255
        b = rgb & 255

        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        return h * 360., s * 100.

    elif color_mode == COLOR_TEMP:
        ct = int(props.get('ct', 0)) # temperature in kelvin

        r, g, b = convert_K_to_RGB(ct)

        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

        return h * 360., s * 100.

    elif color_mode == COLOR_HSV:
        hue = int(props.get('hue', 0)) # 0 - 359
        sat = int(props.get('sat', 0)) # 0 - 100

        return hue, sat

    return 0., 0.


def parse_brightness(props):

    return int(props.get('bright', 0))


def parse_result_error(msg):

    if "error" in msg:
        error = msg['error']
        code = error.get('code', -1)
        message = error.get('message', '')
        return ( code, message )


class Result (AsyncResult):

    def resolve(self, msg, *args, **kwargs):
        err = parse_result_error(msg)

        if err:
            self.reject("error [%d] : %s" % err, *args, **kwargs)
        else:
            super(Result, self).resolve(msg.get('result', []), *args, **kwargs)