# coding: utf-8

from .Process import Process
import threading
import serial
import socket
import struct
import time

class Transport(object):

    def init(self, process):
        self.process = process
        self.protocol = process.protocol
        self.log = process.log
    
    def open(self):
        pass

    def read(self):
        raise NotImplementedError()

    def write(self, data):
        pass

    def close(self):
        pass

class SerialTransport(Transport):

    def __init__(self, port, baudrate):
        super(SerialTransport, self).__init__()
        self._lock = threading.Lock()
        self.serial = None
        self.port = port
        self.baudrate = baudrate

    def open(self):
        super(SerialTransport, self).open()
        self.serial = serial.serial_for_url(self.port, baudrate=self.baudrate, timeout=1)
        self.log.info("(serial) connected to port=%s baudrate=%d" % (self.port, self.baudrate))

    def read(self):
        if self.serial is not None:
            if self.serial.is_open:
                return self.serial.read(self.serial.in_waiting or 1)
            else:
                self.process.stop()

    def write(self, data):
        if self.serial is not None:
            with self._lock:
                # self.log.debug("(serial) write to port=%s baudrate=%d data=%s" % (self.port, self.baudrate, data))
                self.serial.write(data)
        else:
            raise Exception('Not connected')

    def close(self):
        if self.serial is not None:
            with self._lock:
                self.serial.close()
                self.serial = None
                self.log.info("(serial) closed from port=%s baudrate=%d" % (self.port, self.baudrate))

class NetTransport(Transport):

    def __init__(self, host, port):
        super(NetTransport, self).__init__()
        self._lock = threading.Lock()
        self.sock = None
        self.host = host
        self.port = port

    def open(self):
        super(NetTransport, self).open()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(1)
        self.log.info("(net) connected to host=%s port=%d" % (self.host, self.port))

    def read(self):
        if self.sock is not None:
            try:
                data = self.sock.recv(1024)  # return as bytes
                # self.log.debug("(net) read from host=%s port=%d data=%s" % (self.host, self.port, data))
            except socket.timeout:
                pass
            else:
                if data:
                    return data
                else:
                    # socket closed !
                    self.process.stop()

    def write(self, data):
        if self.sock is not None:
            with self._lock:
                # self.log.debug("(net) write to host=%s port=%d data=%s" % (self.host, self.port, data))
                self.sock.send(data)
        else:
            raise Exception('Not connected')

    def close(self):
        if self.sock is not None:
            with self._lock:
                self.sock.close()
                self.sock = None
                self.log.info("(net) closed from host=%s port=%d" % (self.host, self.port))


class UdpTransport(Transport):

    def __init__(self, host, port):
        super(UdpTransport, self).__init__()
        self._lock = threading.Lock()
        self.sock = None
        self.host = host
        self.port = port

    def open(self):
        super(UdpTransport, self).open()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.sock.bind(("0.0.0.0", self.port))

        mreq = struct.pack("=4sl", socket.inet_aton(
            self.host), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self.sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_RCVBUF, 1024)
        # allow multiple processes to bind to the same address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # join multicast group and bind to port
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sock.settimeout(1)

        self.log.info("(udp): connection opened, host: %s , port: %d" % (
            str(self.host), self.port))


    def read(self):
        if self.sock is not None:
            try:
                data, addr = self.sock.recvfrom(1024)  # return as bytes
            except socket.timeout:
                pass
            else:
                if data:
                    return data, addr
                else:
                    # socket closed !
                    self.process.stop()

    def write(self, data, to):
        if self.sock is not None:
            with self._lock:
                self.sock.sendto(data, to)
        else:
            raise Exception('Not connected')

    def close(self):
        if self.sock is not None:
            with self._lock:
                self.sock.close()
                self.sock = None
                self.log.info("(udp) closed from host=%s port=%d" % (self.host, self.port))


class Protocol(object):
    
    def init(self, process):
        self.process = process
        self.transport = process.transport
        self.log = process.log
    
    def connection_made(self):
        pass

    def data_received(self, data):
        """Called with snippets received from the serial port"""
    
    def loop(self):
        pass

    def connection_lost(self, exc):
        if isinstance(exc, Exception):
            self.log.error("Exception in transport process: %s" % str(exc))

class Packetizer(Protocol):
    """
    Read binary packets from serial port. Packets are expected to be terminated
    with a TERMINATOR byte (null byte by default).
    The class also keeps track of the transport.
    """

    def __init__(self, terminator = b'\0'):
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

    def __init__(self, name, transport, protocol, reconnect = True, reconnect_delay = 15, **kwargs):
        super(TransportProcess, self).__init__(name, **kwargs)
        self.transport = transport
        self.protocol = protocol
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        self.is_open = False

    def main(self):
        
        self.protocol.init(self)
        self.transport.init(self)
        
        while not self.stopped():
        
            error = None
            
            try:
                self.transport.open()
                
                self.is_open = True
                
                self.protocol.connection_made()
            except Exception as e:
                error = e

            while not error and not self.stopped():
                try:
                    # used mainly for regular check such as timeout...
                    self.protocol.loop()
                    
                    # read all that is there or wait for one byte (blocking)
                    data = self.transport.read()
                except Exception as e:
                    # probably some I/O problem such as disconnected USB serial
                    # adapters -> exit
                    error = e
                else:
                    if data:
                        # make a separated try-except for called used code
                        try:
                            self.protocol.data_received(data)
                        except Exception as e:
                            error = e

            if self.is_open:
                self.transport.close()
            
            self.is_open = False

            self.protocol.connection_lost(error)
            
            if not self.reconnect:
                break
            
            if self.reconnect_delay > 0:
                t_end = time.time() + self.reconnect_delay
                while not self.stopped() and time.time() < t_end:
                    time.sleep(0.5)

