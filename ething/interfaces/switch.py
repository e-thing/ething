# coding: utf-8

from ething.meta import interface, method, iface


@interface
class Switch(iface):
    
    
    @method.return_type('bool')
    def getState(self):
        """
        return the current state of the switch
        """
        return self.getData('state', False)
    
    
    @method.arg('state', type='bool')
    def setState(self, state):
        """
        set the current state of the switch
        """
        raise NotImplementedError()
    
    
    @method
    def on(self):
        """
        turn on the switch
        """
        self.setState(state = True)
    
    @method
    def off(self):
        """
        turn off the switch
        """
        self.setState(state = False)
    
    @method
    def toggle(self):
        """
        toggle the switch
        """
        self.setState(not self.getState())

