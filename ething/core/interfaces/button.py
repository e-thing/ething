# coding: utf-8

from ..Interface import Interface
from ..reg import *
from ..rule.event import ResourceSignal, ResourceEvent, ResourceFilter


class ButtonClicked(ResourceSignal):
    def __init__(self, resource, type='single'):
        super(ButtonClicked, self).__init__(resource)
        self.type = type


@attr('resource', type=ResourceFilter(must_throw=ButtonClicked))
class ButtonClickedEvent(ResourceEvent):
    signal = ButtonClicked




@throw(ButtonClicked)
class Button(Interface):
    pass

