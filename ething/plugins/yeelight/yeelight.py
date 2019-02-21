# coding: utf-8

from future.utils import listvalues
import socket
import struct
import re
import colorsys
from ething.core.TransportProcess import AsyncResult


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


COLOR_RGB = 1
COLOR_TEMP = 2
COLOR_HSV = 3

def parse_color(props):

    color_mode = int(props.get('color_mode', 1))

    if color_mode == COLOR_RGB:

        rgb = int(props.get('rgb', 0))
        return '#' + hex(rgb)[2:].ljust(6, '0').upper()

    elif color_mode == COLOR_TEMP:
        # todo
        ct = int(props.get('ct', 0)) # temperature in kelvin


    elif color_mode == COLOR_HSV:
        hue = int(props.get('hue', 0)) # 0 - 359
        sat = int(props.get('sat', 0)) # 0 - 100

        r, g, b = colorsys.hsv_to_rgb(hue / 359., sat / 100., 1.)

        return '#%02X%02X%02X' % (int(r*255), int(g*255), int(b*255))

    return '#000000'

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