

class InvalidQueryException(Exception):
    def __init__(self, message, stream = None):
        message = str(message)
        
        if stream is not None:
            message = "(near position %d) %s" % (stream.previousIndex(), message)
        
        # Call the base class constructor with the parameters it needs
        super(InvalidQueryException, self).__init__(message)
    