#!/usr/bin/env python

import socket
import threading
import logging



class Client(threading.Thread):
    def __init__(self, ip, port, clientsocket, onMessage = None, onConnect = None, onDisconnect = None):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        self.onMessage = onMessage if callable(onMessage) else None
        self.onConnect = onConnect if callable(onConnect) else None
        self.onDisconnect = onDisconnect if callable(onDisconnect) else None
        self.buff = ''

    def run(self):
        logging.debug("client connected %s %s" % (self.ip, self.port,))

        if self.onConnect is not None:
            self.onConnect(self.clientsocket)

        try:
            while True:
                data = self.clientsocket.recv(1024)
                if data:
                    #print ('Received {}'.format(data))
                    self.buff += data
                    while True:
                        try:
                            endLine = self.buff.index('\n')
                        except:
                            break
                        if endLine == -1:
                            break
                        line = self.buff[:endLine].strip('\r')
                        self.buff = self.buff[endLine+1:]
                        if self.onMessage is not None and len(line):
                            self.onMessage(self.clientsocket, line)
                else:
                    break
        except:
            pass
        finally:
            logging.debug("client disconnected")
            self.clientsocket.close()
            if self.onDisconnect is not None:
                self.onDisconnect(self.clientsocket)


class Server(threading.Thread):
    def __init__(self, host, port, onMessage = None, onConnect = None, onDisconnect = None):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.onMessage = onMessage if callable(onMessage) else None
        self.onConnect = onConnect if callable(onConnect) else None
        self.onDisconnect = onDisconnect if callable(onDisconnect) else None
        self.clients = []

    def run(self):

        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.tcpsock.bind((self.host, self.port))

        logging.info("Server listening on port %d" % self.port)

        while True:
            self.tcpsock.listen(10)
            (clientsocket, (ip, port)) = self.tcpsock.accept()
            self.clients.append(clientsocket)
            newthread = Client(ip, port, clientsocket, self.onMessage, self.onConnect, self.onClientDisconnect)
            newthread.start()

    def onClientDisconnect(self, client):
        if client in self.clients: self.clients.remove(client)
        #print("There are %d clients connected" % len(self.clients))
        if self.onDisconnect is not None:
            self.onDisconnect()

    def sendMessageToAllClients(self, message):
        for client in self.clients:
            client.sendall(message+"\r\n")

    def stop(self):
        return

if __name__ == '__main__':

    import time

    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005


    def onClientMessage(client, line):
        print ('message received: {}'.format(line))

        if line == "exit":
            client.close()

        return

    server = Server(TCP_IP, TCP_PORT, onClientMessage)
    server.start()

    while True:
        time.sleep(5)
        print("tic")
        server.sendMessageToAllClients("toc")

