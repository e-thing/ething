
from ething.meta import method, iface

class IR (iface):
    
    
    @method.arg('id', type='int', minimum=0, maximum=255)
    def record(self, id):
        """
        record an IR code
        """
        self.set_value('V_IR_RECORD', id, store = False)
    
    @method.arg('id', type='int', minimum=0, maximum=255)
    def send(self, id):
        """
        send an IR code
        """
        self.set_value('V_IR_SEND', id, store = False)
    
    @method.return_type('int')
    def last_rec(self):
        """
        return the last IR code received
        """
        return self.get_value('V_IR_RECEIVE')
    
    
    