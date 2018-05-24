# coding: utf-8

from ething.meta import method, iface


class Cover (iface):

    @method
    def up(self):
        """
        move cover up
        """
        self.set_value('V_UP', None)

    @method
    def down(self):
        """
        move cover down
        """
        self.set_value('V_DOWN', None)

    @method
    def stop(self):
        """
        stop cover
        """
        self.set_value('V_STOP', None)

    @method.return_type('string')
    def getState(self):
        """
        return the state of the cover : up, down or stop
        """
        return self.data.get('state')

    @method.meta(optional='V_PERCENTAGE')
    @method.return_type('float')
    def getLevel(self):
        """
        return the cover percentage (in %)
        """
        return self.get_value('V_PERCENTAGE')

    @method.meta(optional='V_PERCENTAGE')
    @method.arg('level', type='float', minimum=0, maximum=100)
    def setLevel(self, level):
        """
        set the cover percentage (in %)
        """
        self.set_value('V_PERCENTAGE', level)
