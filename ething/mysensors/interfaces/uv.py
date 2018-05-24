# coding: utf-8

from ething.meta import method, iface


class UV (iface):
    """
    see: https://www.mysensors.org/build/uv
    """

    @method.return_type('float')
    def getUVIndex(self):
        """
        return the UV index
        """
        return self.get_value('V_UV')
