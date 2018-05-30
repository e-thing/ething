# coding: utf-8

from . import Signal, Event
from ething.base import attr, Validator, isNone, abstract
from ething.ShortId import ShortId
from ething.ResourceQueryParser import ResourceQueryParser
from future.utils import string_types


class ResourceSignal(Signal):

    def __init__(self, resource):
        super(ResourceSignal, self).__init__()
        self.resource = resource.id
        self.rName = resource.name
        self.rType = resource.type
        self.rModifiedDate = resource.modifiedDate
    
    def __str__(self):
        return "%s [%s]" % (type(self).__name__, self.resource)

    def __repr__(self):
        return "%s [%s]" % (type(self).__name__, self.resource)
    

class isResourceFilter(Validator):

    def __init__(self, onlyTypes=None):
        self.onlyTypes = onlyTypes

    def _checkId(self, id, ething):
        # resource id
        resource = ething.get(id)
        if resource is None:
            raise ValueError("the resource with id '%s' does not exist." % id)
        if self.onlyTypes:
            # check the type
            for type in self.onlyTypes:
                if resource.isTypeof(type):
                    break
            else:
                raise ValueError("the resource %s must be one of the following types : %s" % (
                    str(resource), ', '.join(self.onlyTypes)))

    def validate(self, value, object):

        resourceFilter = value
        ething = object.ething

        if isinstance(resourceFilter, string_types):
            # can either be an id or an expression

            if ShortId.validate(resourceFilter):
                # resource id
                self._checkId(resourceFilter, ething)
            else:
                # expression
                ok, message = ResourceQueryParser.check(resourceFilter)
                if not ok:
                    raise ValueError('invalid expression: %s' % message)

        elif isinstance(resourceFilter, list):
            if len(resourceFilter) == 0:
                raise ValueError("not a valid array of resource's id.")

            # must be an array of ids
            for id in resourceFilter:
                if ShortId.validate(id):
                    self._checkId(id, ething)
                else:
                    raise ValueError("not a valid array of resource's id.")

        else:
            raise ValueError("invalid")

        return value

    def schema(self):
        return {
            "type": "array",
            "items": {
                "type": "string"
            },
            "onlyTypes": self.onlyTypes
        }


@abstract
@attr('resource', validator=isResourceFilter() | isNone(), default=None, description="filter the resource emitting the signal")
class ResourceEvent(Event):

    signal = ResourceSignal

    def _filter(self, signal):
        # the event accepts only signal emitted from a resource

        resourceIdFromSignal = signal.resource

        resourceFilter = self.resource

        if resourceFilter is None:  # no filtering
            return True
        # can either be an id or an expression
        elif isinstance(resourceFilter, string_types):

            if ShortId.validate(resourceFilter):
                return resourceFilter == resourceIdFromSignal
            else:  # query string
                # check if the resource from the signal match the expression
                return bool(self.ething.findOne({
                    '$and': {
                        {'_id': resourceIdFromSignal},
                        self.ething.resourceQueryParser.parse(resourceFilter)
                    }
                }))

        elif isinstance(resourceFilter, list):  # array of resource ids
            return resourceIdFromSignal in resourceFilter

        return False
