# coding: utf-8

from .Resource import Resource, ResourceTypeArray
from .reg import *

@abstract
@attr('items', type=ResourceTypeArray(), default=[], description="The list of items within this group.")
@meta(category="Group")
class Group(Resource):

    def apply(self, method, *args, **kwargs):
        return [getattr(item, method)(*args, **kwargs) for item in self.items]



from .interfaces import Light, Relay, DimmableLight, RGBWLight


@attr('items', type=ResourceTypeArray(accepted_types=(Relay, )))
class RelayGroup(Group, Relay):

    def setState(self, state):
        super(RelayGroup, self).setState(state)
        self.apply('setState', state)


@attr('items', type=ResourceTypeArray(accepted_types=(Light, )))
class LightGroup (Group, Light):

    def setState(self, state):
        super(LightGroup, self).setState(state)
        self.apply('setState', state)


@attr('items', type=ResourceTypeArray(accepted_types=(DimmableLight, )))
class DimmableLightGroup (Group, DimmableLight):

    def setState(self, state):
        super(DimmableLightGroup, self).setState(state)
        self.apply('setState', state)

    def setLevel(self, level):
        super(DimmableLightGroup, self).setLevel(level)
        self.apply('setLevel', level)


@attr('items', type=ResourceTypeArray(accepted_types=(RGBWLight, )))
class RGBWLightGroup (Group, RGBWLight):

    def setState(self, state):
        super(RGBWLightGroup, self).setState(state)
        self.apply('setState', state)

    def setLevel(self, level):
        super(RGBWLightGroup, self).setLevel(level)
        self.apply('setLevel', level)

    def setColor(self, hue, saturation):
        super(RGBWLightGroup, self).setColor(hue, saturation)
        self.apply('setColor', hue, saturation)
