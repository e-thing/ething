from ..type import String


class Expression(String):
    def __init__(self, **attributes):
        super(Expression, self).__init__(**attributes)

    def validate(self, value, context = None):

        super(Expression, self).validate(value, context)

        ething = context.get('ething')

        if ething:
            ok, message = ething.resourceQueryParser.check(value)
            if not ok:
                raise ValueError('invalid expression: %s' % message)
