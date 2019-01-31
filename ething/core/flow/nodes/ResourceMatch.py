# coding: utf-8
from .. import *
from ...query import Expression


@meta(icon='mdi-filter')
class ResourceFilter(ResourceNode):
    """ filter signals that was emitted by a specific resource """

    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, **inputs):
        msg = inputs['default']
        test_pass = False
        try:
            test_pass = (msg.get('resource') == self.resource)
        finally:
            self.emit(msg, port='default' if test_pass else 'fail')



@meta(icon='mdi-filter')
@attr('expression', type=Expression(), description="The expression the resource must match")
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
                r = self.ething.get(self.resource)
            else:
                r = msg.get('resource')
                if isinstance(r, string_types):
                    r = self.ething.get(r)

            if r:
                test_pass = r.match(self.expression)
        finally:
            self.emit(msg, port='default' if test_pass else 'fail')
