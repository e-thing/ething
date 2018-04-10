# coding: utf-8

from ething.meta import method
from ething.interfaces import Switch


class Lock (Switch):
    
    
    def setState(self, state):
        self.set_value( 'V_STATUS', state )
    
    
    