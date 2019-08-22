# coding: utf-8


from .MySensorsGateway import MySensorsGateway, MySensorsController
from ething.TransportProcess import Transport
from .Message import Message
from .helpers import *
import time, random, logging


LOGGER = logging.getLogger(__name__)


class FakeTransport(Transport):

    def __init__(self):
        super(FakeTransport, self).__init__()
        self.msg_sent = list()
        self.msg_rec = list()

    def open(self):
        self.msg_sent.clear()
        self.msg_rec.clear()

        LOGGER.info("(fake) connected")

        self.msg_rec.append(Message(GATEWAY_ADDRESS, INTERNAL_CHILD, INTERNAL, I_GATEWAY_READY))

        # light
        self.msg_rec.append(Message.parse('12;6;0;0;3;My Light'))

        #thermometer
        self.msg_rec.append(Message.parse('11;5;0;0;6;My thermometer'))
        self.t_11_5 = time.time()

    def read(self):

        t = time.time()

        if self.msg_sent:
            msg = Message.parse(self.msg_sent.pop(0))
            LOGGER.debug("(fake) msg=%s", msg)

            if msg.ack:
                ack_msg = msg.copy()
                ack_msg.payload = None
                self.msg_rec.append(ack_msg)

            if msg.messageType == INTERNAL:
                if msg.subType == I_VERSION:
                    i_msg = msg.copy()
                    i_msg.value = 'X.X'
                    self.msg_rec.append(i_msg)

        if t - self.t_11_5 > 5.0:
            self.msg_rec.append(Message.parse('11;5;1;0;0;%s' % round(random.random() * 50., 1)))
            self.t_11_5 = t

        if self.msg_rec:
            for m in self.msg_rec:
                LOGGER.debug("(fake) read=%s", m)
            rec = b''.join([m.raw()+b'\r\n' for m in self.msg_rec])
            self.msg_rec.clear()
            return rec

        time.sleep(0.5)

    def write(self, data):
        LOGGER.debug("(fake) write=%s", data)
        self.msg_sent.append(data)

    def close(self):
        LOGGER.info("(fake) closed")


class MySensorsFakeController(MySensorsController):
    def __init__(self, gateway):
        super(MySensorsFakeController, self).__init__(gateway, FakeTransport())


class MySensorsFakeGateway(MySensorsGateway):
    __controller__ = MySensorsFakeController
