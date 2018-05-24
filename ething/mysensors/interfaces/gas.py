# coding: utf-8

from ething.meta import method, iface


class Gas (iface):

    @method.meta(optional='V_FLOW')
    @method.return_type('float')
    def getFlow(self):
        """
        return the flow of gas
        """
        return self.get_value('V_FLOW')

    @method.meta(optional='V_VOLUME')
    @method.return_type('float')
    def getVolume(self):
        """
        return the gas volume
        """
        return self.get_value('V_VOLUME')
