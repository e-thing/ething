# coding: utf-8

from ething.meta import method, iface


class Water_Quality (iface):

    @method.meta(optional='V_TEMP')
    @method.return_type('float')
    def getTemperature(self):
        """
        return the temperature of the water
        """
        return self.get_value('V_TEMP')

    @method.meta(optional='V_PH')
    @method.return_type('float')
    def getPH(self):
        """
        return the PH of the water
        """
        return self.get_value('V_PH')

    @method.meta(optional='V_ORP')
    @method.return_type('float')
    def getORP(self):
        """
        return the redox potential in mV
        """
        return self.get_value('V_ORP')

    @method.meta(optional='V_EC')
    @method.return_type('float')
    def getElectricConductivity(self):
        """
        return the water electric conductivity uS/cm (microSiemens/cm)
        """
        return self.get_value('V_EC')
