# coding: utf-8

from ething.meta import method, iface


class Water (iface):

    @method.meta(optional='V_FLOW')
    @method.return_type('float')
    def getFlow(self):
        """
        return the flow of water
        """
        return self.get_value('V_FLOW')

    @method.meta(optional='V_VOLUME')
    @method.return_type('float')
    def getVolume(self):
        """
        return the water volume
        """
        return self.get_value('V_VOLUME')
