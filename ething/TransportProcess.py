# coding: utf-8

from .processes import Process
import threading
import serial
import socket
import struct
import time
import logging
from queue import Queue, Empty
import os


LOGGER = logging.getLogger(__name__)


win = True if os.name == 'nt' else False


class Transport(object):

    def __init__(self):
        self._opened = threading.Event()
    
    def open(self):
        self._opened.set()

    def read(self):
        raise NotImplementedError()

    def write(self, data):
        pass

    def close(self):
        self._opened.clear()

    @property
    def is_open(self):
        return self._opened.is_set()

    def wait_open(self, timeout=None):
        return self._opened.wait(timeout)

class SerialTransport(Transport):

    def __init__(self, port, baudrate):
        super(SerialTransport, self).__init__()
        self._lock = threading.Lock()
        self.serial = None
        self.port = port
        self.baudrate = baudrate

    def open(self):
        try:
            self.serial = serial.serial_for_url(self.port, baudrate=self.baudrate, timeout=1)
        except serial.SerialException as e:
            LOGGER.error(e)
            return
        super(SerialTransport, self).open()
        LOGGER.info("(serial) connected to port=%s baudrate=%d" % (self.port, self.baudrate))

    def read(self):
        if self.serial is not None:
            if self.serial.is_open:
                if win and self.serial.in_waiting==0:
                    # on windows the serial.read() is blocking gevent
                    t0 = time.time()
                    timeout = self.serial.timeout
                    read = False
                    while time.time() - t0 < timeout:
                        if self.serial.in_waiting>0:
                            read = True
                            break
                        time.sleep(0.1)
                    if not read:
                        return

                return self.serial.read(self.serial.in_waiting or 1)
            else:
                self.close()

    def write(self, data):
        if self.serial is not None:
            with self._lock:
                # LOGGER.debug("(serial) write to port=%s baudrate=%d data=%s" % (self.port, self.baudrate, data))
                self.serial.write(data)
        else:
            raise Exception('Not connected')

    def close(self):
        if self.serial is not None:
            with self._lock:
                super(SerialTransport, self).close()
                self.serial.close()
                self.serial = None
                LOGGER.info("(serial) closed from port=%s baudrate=%d" % (self.port, self.baudrate))

class NetTransport(Transport):

    def __init__(self, host, port):
        super(NetTransport, self).__init__()
        self._lock = threading.Lock()
        self.sock = None
        self.host = host
        self.port = port

    def open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(1)
        super(NetTransport, self).open()
        LOGGER.info("(net) connected to host=%s port=%d" % (self.host, self.port))

    def read(self):
        if self.sock is not None:
            try:
                data = self.sock.recv(1024)  # return as bytes
                # LOGGER.debug("(net) read from host=%s port=%d data=%s" % (self.host, self.port, data))
            except socket.timeout:
                pass
            else:
                if data:
                    return data
                else:
                    # socket closed !
                    self.close()

    def write(self, data):
        if self.sock is not None:
            with self._lock:
                # LOGGER.debug("(net) write to host=%s port=%d data=%s" % (self.host, self.port, data))
                self.sock.send(data)
        else:
            raise Exception('Not connected')

    def close(self):
        if self.sock is not None:
            with self._lock:
                super(NetTransport, self).close()
                self.sock.close()
                self.sock = None
                LOGGER.info("(net) closed from host=%s port=%d" % (self.host, self.port))


class UdpTransport(Transport):

    def __init__(self, host, port):
        super(UdpTransport, self).__init__()
        self._lock = threading.Lock()
        self.sock = None
        self.host = host
        self.port = port

    def open(self):
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

        self.sock.bind(("0.0.0.0", self.port))

        mreq = struct.pack("=4sl", socket.inet_aton(
            self.host), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)
        # allow multiple processes to bind to the same address
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # join multicast group and bind to port
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(2)

        super(UdpTransport, self).open()

        LOGGER.info("(udp): connection opened, host: %s , port: %d" % (
            str(self.host), self.port))


    def read(self):
        if self.sock is not None:
            try:
                data, addr = self.sock.recvfrom(4096)  # return as bytes
            except socket.timeout:
                pass
            else:
                if data:
                    return data, addr
                else:
                    # socket closed !
                    self.close()

    def write(self, data, to):
        if self.sock is not None:
            with self._lock:
                self.sock.sendto(data, to)
        else:
            raise Exception('Not connected')

    def close(self):
        if self.sock is not None:
            with self._lock:
                super(UdpTransport, self).close()
                self.sock.close()
                self.sock = None
                LOGGER.info("(udp) closed from host=%s port=%d" % (self.host, self.port))


class Protocol(object):

    def init(self, transport):
        self.transport = transport
    
    def connection_made(self):
        pass

    def data_received(self, data):
        """Called with snippets received from the serial port"""
    
    def loop(self):
        pass

    def connection_lost(self, exc):
        #if isinstance(exc, Exception):
        #    LOGGER.error("Exception in transport process: %s" % str(exc))
        pass


class Packetizer(Protocol):
    """
    Read binary packets from serial port. Packets are expected to be terminated
    with a TERMINATOR byte (null byte by default).
    The class also keeps track of the transport.
    """

    def __init__(self, terminator = b'\0'):
        super(Packetizer, self).__init__()
        self.buffer = bytearray()
        self.terminator = terminator

    def data_received(self, data):
        """Buffer received data, find TERMINATOR, call handle_packet"""
        self.buffer.extend(data)
        while self.terminator in self.buffer:
            packet, self.buffer = self.buffer.split(self.terminator, 1)
            self.handle_packet(packet)

    def handle_packet(self, packet):
        raise NotImplementedError()


class LineReader(Packetizer):
    """
    Read and write (Unicode) lines.
    The encoding is applied.
    """

    def __init__(self, terminator = b'\r\n', encoding = 'utf-8', unicode_handling = 'replace'):
        super(LineReader, self).__init__(terminator)
        self.encoding = encoding
        self.unicode_handling = unicode_handling

    def handle_packet(self, packet):
        self.handle_line(packet.decode(self.encoding, self.unicode_handling))

    def handle_line(self, line):
        """Process one line - to be overridden by subclassing"""
        raise NotImplementedError()

    def write_line(self, text, encode = True):
        """
        Write text to the transport. ``text`` is a Unicode string and the encoding
        is applied before sending ans also the newline is append.
        """
        if encode:
            text = text.encode(self.encoding, self.unicode_handling)
        # + is not the best choice but bytes does not support % or .format in py3 and we want a single write call
        self.transport.write(text + self.terminator)


class TransportProcess(Process):

    def __init__(self, transport, protocol, reconnect = True, reconnect_delay = 15, open_state_changed_handler = None, logger = LOGGER, **kwargs):
        super(TransportProcess, self).__init__(**kwargs)
        self.transport = transport
        self.protocol = protocol
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        self._is_open = False
        self._open_state_changed_handler = open_state_changed_handler
        self._logger = logger

    @property
    def is_open(self):
        return self._is_open

    @property
    def logger(self):
        return self._logger

    def on_open_state_changed(self):
        # the state is given by self.is_open
        if self._open_state_changed_handler is not None:
            self._open_state_changed_handler(self.is_open)

    def run(self):

        self.protocol.init(self.transport)
        
        while self.is_running:
        
            error = None
            
            try:
                self.transport.open()
            except Exception as e:
                self.logger.exception('exception in transport.open()')
                error = e

            try:
                self.protocol.connection_made()
            except Exception as e:
                self.logger.exception('exception in protocol.connection_made()')
                error = e

            while not error and self.is_running and self.transport.is_open:

                if not self._is_open:
                    self._is_open = True
                    self.on_open_state_changed()

                try:
                    # used mainly for regular check such as timeout...
                    self.protocol.loop()
                except Exception as e:
                    self.logger.exception('exception in protocol.loop()')
                    error = e

                try:
                    # read all that is there or wait for one byte (blocking)
                    data = self.transport.read()
                except Exception as e:
                    # probably some I/O problem such as disconnected USB serial
                    # adapters -> exit
                    self.logger.exception('exception in transport.read()')
                    error = e
                else:
                    if data:
                        # make a separated try-except for called used code
                        try:
                            self.protocol.data_received(data)
                        except Exception as e:
                            self.logger.exception('exception in protocol.data_received()')
                            error = e

            self._is_open = False
            self.on_open_state_changed()

            if self.transport.is_open:
                try:
                    self.transport.close()
                except Exception as e:
                    self.logger.exception('exception in transport.close()')

            try:
                self.protocol.connection_lost(error)
            except Exception as e:
                self.logger.exception('exception in protocol.connection_lost()')

            
            if not self.reconnect:
                break
            
            if self.reconnect_delay > 0:
                t_end = time.time() + self.reconnect_delay
                while self.is_running and time.time() < t_end:
                    time.sleep(1.)
                self.logger.debug('reconnecting...')


class QueueProtocol(Protocol):
    def __init__(self, queue):
        super(QueueProtocol, self).__init__()
        self._q = queue

    def data_received(self, data):
        self._q.put(data)


class ThreadedTransport(Transport):

    def __init__(self, transport, timeout=1):
        super(ThreadedTransport, self).__init__()
        self._transport = transport
        self._q = Queue()
        self._thread = None
        self._timeout = timeout

    def open(self):
        if self._thread:
            raise Exception('already opened')
        self._thread = TransportProcess(transport=self._transport, protocol=QueueProtocol(self._q))
        self._thread.start()
        # wait for the Process to be opened
        if self._transport.wait_open(5):
            super(ThreadedTransport, self).open()

    def read(self):
        try:
            data = self._q.get(timeout=self._timeout)
        except Empty:
            return None

        return data

    def write(self, *args, **kwargs):
        return self._transport.write(*args, **kwargs)

    def close(self):
        if self._thread:
            super(ThreadedTransport, self).close()
            self._thread.stop()
            self._thread = None


class AsyncResult (object):

    def __init__(self, command = None, done = None, err = None):
        self.__command = command
        self.__on_done = done
        self.__on_err = err
        self.__event = threading.Event()
        self.__data = None
        self.__error = None
        self.__send_ts = time.time()

    @property
    def command(self):
        return self.__command

    @property
    def data(self):
        return self.__data

    @property
    def error(self):
        return self.__error

    @property
    def send_ts(self):
        return self.__send_ts

    def resolve(self, data = None, args = (), kwargs = {}):
        if not self.__event.is_set():
            self.__data = data
            if self.__on_done:
                self.__on_done(self, *args, **kwargs)
            self.__event.set()

    def reject(self, error, args = (), kwargs = {}):
        if not self.__event.is_set():
            self.__error = error

            if self.__on_err:
                self.__on_err(self, *args, **kwargs)

            self.__event.set()

    def wait(self, timeout = None):
        self.__event.wait(timeout)