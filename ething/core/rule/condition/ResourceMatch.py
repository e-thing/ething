# coding: utf-8

from .Condition import Condition
from ...entity import *
from ...Resource import ResourceType
from ...query import Expression


@meta(icon='mdi-filter')
@attr('resource', type=Nullable(ResourceType()), default=None, description="The resource that must match the given expression. If none, the resource is the one that emits the signal.")
@attr('expression', type=Expression(), description="The expression the resource must match")
class ResourceMatch(Condition):
    """ is true if a resource match an expression """

    def test(self, signal, core):

        r = None

        if self.resource is not None:
            r = core.get(self.resource)
        else:
            if hasattr(signal, 'resource'):
                r = signal.resource

        if r:
            return r.match(self.expression)

