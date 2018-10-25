from ..type import String


class Expression(String):
    def __init__(self, **attributes):
        super(Expression, self).__init__(**attributes)

    def validate(self, value):
        from ..core import Core

        super(Expression, self).validate(value)

        ething = Core.get_instance()

        if ething:
            ok, message = ething.resourceQueryParser.check(value)
            if not ok:
                raise ValueError('invalid expression: %s' % message)
