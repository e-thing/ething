# coding: utf-8

from .Process import Process
import threading
import serial
import socket
import struct

class Transport(object):

    def open(self, process):
        self.process = process
        self.protocol = process.protocol
        self.log = process.log

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

    def open(self, process):
        super(SerialTransport, self).open(process)
        self.serial = serial.serial_for_url(self.port, baudrate=self.baudrate, timeout=1)
        self.log.info("(serial) connected to port=%s baudrate=%d" % (self.port, self.baudrate))

    def read(self):
        if self.serial.is_open:
            return self.serial.read(self.serial.in_waiting or 1)
        else:
            self.process.stop()

    def write(self, data):
        with self._lock:
            self.serial.write(data)

    def close(self):
        with self._lock:
            self.serial.close()
            self.log.info("(serial) closed from port=%s baudrate=%d" % (self.port, self.baudrate))

class NetTransport(Transport):

    def __init__(self, host, port):
        super(NetTransport, self).__init__()
        self._lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def open(self, process):
        super(NetTransport, self).open(process)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(1)
        self.log.info("(net) connected to host=%s port=%d" % (self.host, self.port))

    def read(self):
        data = self.sock.recv(1024)  # return as bytes
        if data:
            return data
        else:
            # socket closed !
            self.process.stop()

    def write(self, data):
        with self._lock:
            self.sock.send(data)

    def close(self):
        with self._lock:
            self.sock.close()
            self.log.info("(net) closed from host=%s port=%d" % (self.host, self.port))


class UdpTransport(Transport):

    def __init__(self, host, port):
        super(UdpTransport, self).__init__()
        self._lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.host = host
        self.port = port

    def open(self, process):
        super(UdpTransport, self).open(process)

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
        with self._lock:
            self.sock.sendto(data)

    def close(self):
        with self._lock:
            self.sock.close()
            self.log.info("(udp) closed from host=%s port=%d" % (self.host, self.port))


class Protocol(object):

    def connection_made(self, process):
        self.process = process
        self.transport = process.transport
        self.log = process.log

    def data_received(self, data):
        """Called with snippets received from the serial port"""

    def connection_lost(self, exc):
        if isinstance(exc, Exception):
            raise exc

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

    def write_line(self, text):
        """
        Write text to the transport. ``text`` is a Unicode string and the encoding
        is applied before sending ans also the newline is append.
        """
        # + is not the best choice but bytes does not support % or .format in py3 and we want a single write call
        self.transport.write(text.encode(self.encoding, self.unicode_handling) + self.terminator)

class TransportProcess(Process):

    def __init__(self, name, transport, protocol, **kwargs):
        super(TransportProcess, self).__init__(name, **kwargs)
        self.transport = transport
        self.protocol = protocol
        self.is_open = False

    def main(self):

        error = None

        self.transport.open(self)

        self.is_open = True

        try:
            self.protocol.connection_made(self)
        except Exception as e:
            error = e

        while not error and not self.stopped():
            try:
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

        self.is_open = False

        self.transport.close()

        self.protocol.connection_lost(error)


