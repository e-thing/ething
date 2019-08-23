# coding: utf-8
import logging
import inspect


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#The background is set with 40 plus the number of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': YELLOW,
    'INFO': BLUE,
    'DEBUG': WHITE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

class ColoredFormatter(logging.Formatter):

    def formatMessage(self, record):
        s = super(ColoredFormatter, self).formatMessage(record)
        return COLOR_SEQ % (30 + COLORS[record.levelname]) + s + RESET_SEQ



class NamedLoggerAdapter(logging.LoggerAdapter):

    def __init__(self, obj, name):
        super(NamedLoggerAdapter, self).__init__(logging.getLogger(inspect.getmodule(obj).__name__), {
            'name': name,
        })

    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra['name'], msg), kwargs
