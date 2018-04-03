
from ResourceAction import ResourceAction

class Email(ResourceAction):
    
    @staticmethod
    def validate (attributes, context):
        
        attributes.setdefault('subject', "Notification from e-Thing")
        attributes.setdefault('content', "")
        attributes.setdefault('to', [])
        
        other = {}
        
        for key in attributes:
            
            value = attributes[key]
                
            if key == 'subject':
                
                if not( isinstance(value, basestring) and len(value)>0 ):
                    raise Exception("must be a non empty string.")
                
            elif key == 'content':
                
                if not( isinstance(value, basestring) ):
                    raise Exception("must be a string.")
            
            elif key == 'to':
                
                if not( isinstance(value, basestring) and len(value)>0 ):
                    raise Exception("must be a non empty string.")
            
            else:
                other[key] = value
        
        return ResourceAction.validate(other, context)
    
    
    
    def call(self, signal):
        subject = self['subject']
        content = self['content']
        to = self['content']
        
        attachments = []
        
        for r in self.getResourcesFromSignal(signal):
            attachments.append(r.id)
        
        self.ething.notify(subject = subject, message = content, attachments = attachments, to = to)
    
    
    