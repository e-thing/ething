# coding: utf-8


from .MihomeBase import MihomeBase
from ething.core.reg import *
import json


@abstract
@attr('voltage', type=Number(), mode=READ_ONLY, default=0, description = 'the voltage of the battery if any')
class MihomeDevice(MihomeBase):
    """
    Mihome Device base class
    """

    def _get_gateway(self):
        return self.createdBy

    def processAttr(self, name, value):
        pass  # to be implemented

    def _processData(self, response):

        data = json.loads(response['data'])

        if isinstance(data, dict):

            for k in data:

                value = data[k]

                if k == 'voltage':
                    self._voltage = int(value)/1000.  # volt
                else:
                    self.processAttr(k, value)

