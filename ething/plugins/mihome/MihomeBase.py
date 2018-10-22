# coding: utf-8

from ething.core.Device import Device
from ething.core.reg import *
from ething.core.Process import get_process
from .helpers import IV
import binascii
import pyaes
import math


def just16(str):
    return str.ljust(int(math.ceil(len(str)/16.))*16)


@abstract
@attr('model', type=String(allow_empty=False), mode = READ_ONLY, description="The name of the model of the device")
@attr('short_id', mode = READ_ONLY, default=0)
@attr('sid', type=String(allow_empty=False), mode = READ_ONLY, description="The uniq sid of the device")
class MihomeBase(Device):

    @property
    def controller(self):
        return get_process('mihome')

    def _get_gateway(self):
        raise NotImplementedError()

    def _read(self, **kwargs):
        result = self.controller.send(
            {'cmd': 'read', 'sid': self.sid},
            ip=self._get_gateway().ip,
            **kwargs
        )

        result.wait()

        if result.error:
            raise Exception(str(result.error))

        return result

    def _get_write_key(self, gateway):
        if not gateway.password:
            raise Exception('[mihome gateway] no password set')
        aes = pyaes.AESModeOfOperationCBC(
            just16(gateway.password).encode('utf8'), iv=IV)
        ciphertext = aes.encrypt(just16(gateway._token))
        return binascii.hexlify(ciphertext).decode('utf8')

    def _write(self, data, **kwargs):
        gateway = self._get_gateway()

        payload = {
            'cmd': 'write',
            'model': self.model,
            'sid': self.sid,
            'short_id': self.short_id,
            'data': {
                'key': self._get_write_key(gateway)
            }
        }

        payload['data'].update(data)

        result = self.controller.send(
            payload, ip=gateway.ip, **kwargs
        )

        result.wait()

        if result.error:
            raise Exception(str(result.error))

        return result

    def _processData(self, response):
        raise NotImplementedError()