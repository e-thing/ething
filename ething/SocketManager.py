# coding: utf-8
import time
import select
import socket


class SocketManager(object):

    READ = 1
    WRITE = 2

    def __init__(self, core):
        self.core = core
        self.log = core.log

        self.read_map = {}
        self.write_map = {}

    def register(self, socket, mode, callback, args=()):
        if mode == SocketManager.READ:
            self.registerReadSocket(socket, callback, args)
        elif mode == SocketManager.WRITE:
            self.registerWriteSocket(socket, callback, args)

    def registerReadSocket(self, socket, callback, args=()):
        if callable(callback):
            self.read_map[socket] = (callback, False, args)

    def registerReadSocketOnce(self, socket, callback, args=()):
        if callable(callback):
            self.read_map[socket] = (callback, True, args)

    def unregisterReadSocket(self, socket):
        if socket in self.read_map:
            del self.read_map[socket]

    def registerWriteSocket(self, socket, callback, args=()):
        if callable(callback):
            self.write_map[socket] = (callback, False, args)

    def registerWriteSocketOnce(self, socket, callback, args=()):
        if callable(callback):
            self.write_map[socket] = (callback, True, args)

    def unregisterWriteSocket(self, socket):
        if socket in self.write_map:
            del self.write_map[socket]

    def loop(self, timeout=1):

        while 1:

            t0 = time.time()

            read = list(self.read_map)
            write = list(self.write_map)
            excepts = []

            #self.log.debug("select %d %d" % (len(read), len(write)))

            readable, writable, exceptional = select.select(
                read, write, excepts, timeout)

            if len(readable) > 0:
                # incomming data
                for s in readable:
                    it = self.read_map[s]
                    #self.log.debug("data available for reading")

                    try:
                        it[0](*(it[2]))
                    except:
                        self.log.exception(
                            'SocketManager read callback exception in %s' % it[0])

                    if it[1]:
                        self.unregisterReadSocket(s)

            if len(writable) > 0:
                # incomming data
                for s in writable:
                    it = self.write_map[s]
                    #self.log.debug("data available for writing")

                    try:
                        it[0](*(it[2]))
                    except:
                        self.log.exception(
                            'SocketManager write callback exception')

                    if it[1]:
                        self.unregisterWriteSocket(s)

            spent = time.time() - t0
            if spent >= timeout:
                break

            timeout -= spent

    def loop_forever(self):

        while 1:
            self.loop(1)
