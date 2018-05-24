# coding: utf-8

from ething.meta import method, iface


class Distance (iface):

    @method.return_type('float')
    def getDistance(self):
        """
        return the distance.
        """
        return self.get_value('V_DISTANCE')

    @method.meta(optional='V_UNIT_PREFIX')
    @method.return_type('float')
    def getDistanceUnit(self):
        """
        return the distance unit.
        """
        return self.get_value('V_UNIT_PREFIX')
