# coding: utf-8

from future.utils import listvalues
import socket
import struct
import re


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

    except socket.error:
        pass
    finally:
        if s:
            s.close()

    return listvalues(bulbs)
