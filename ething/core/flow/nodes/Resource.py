# coding: utf-8
from .. import *


@meta(icon='mdi-filter', category="condition")
class ResourceFilter(ResourceNode):
    """ filter signals that was emitted by a specific resource """

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, **inputs):
        msg = inputs['default']
        test_pass = False
        try:
            test_pass = (self.resource == msg.get('resource'))
        finally:
            self.emit(msg, port='default' if test_pass else 'fail')



@meta(icon='mdi-filter', category="condition")
@attr('expression', type=String(allow_empty=False), description="The expression the resource must match")
@attr('resource', type=Nullable(ResourceType()), default=None, description="The resource that must match the given expression. If none, the resource is the one that emits the message.")
class ResourceMatch(ResourceNode):
    """ is true if a resource match an expression """

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, **inputs):
        msg = inputs['default']
        test_pass = False
        try:
            if self.resource is not None:
                r = self.resource
            else:
                r = msg.get('resource')
                if isinstance(r, string_types):
                    r = self.core.get(r)

            if r:
                test_pass = r.match(self.expression)
        finally:
            self.emit(msg, port='default' if test_pass else 'fail')
