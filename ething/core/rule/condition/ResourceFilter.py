# coding: utf-8

from .Condition import Condition
from ...entity import *
from ...Resource import ResourceType
from ...query import Expression


@meta(icon='mdi-filter')
@attr('resource', type=ResourceType(), description="The resource that emitted the signal.")
class ResourceFilter(Condition):
    """ filter signals that was emitted by a specific resource """

    def test(self, signal, core):
        if hasattr(signal, 'resource'):
            return signal.resource == self.resource

