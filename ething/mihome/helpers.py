# coding: utf-8


import socket
import struct
import json

MULTICAST_ADDRESS = '224.0.0.50'
MULTICAST_PORT    = 9898
SERVER_PORT       = 4321
SOCKET_BUFSIZE    = 1024

IV = "\x17\x99\x6d\x09\x3d\x28\xdd\xb3\xba\x69\x5a\x2e\x6f\x58\x56\x2e"

from future.utils import listvalues

def scan ():
    
    gateways = {}
    
    message = '{"cmd":"whois"}'
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack('LL', 2, 0))
    
    try:
        sock.sendto(message, (MULTICAST_ADDRESS, SERVER_PORT))
        
        while True:
            data, addr = sock.recvfrom(SOCKET_BUFSIZE)
            
            if data:
                response = json.loads(data.decode("utf-8"))
                
                if response.get('cmd') == 'iam' and response.get('model') == 'gateway':
                    
                    gateways[addr[0]] = response
                    
            else:
                break
    except:
        pass
    finally:
        sock.close()
    
    return listvalues(gateways)
    
    

