# coding: utf-8

from . import Signal, Event
from ...reg import *
from ...ShortId import ShortId
from future.utils import string_types
from ... import Core


__all__ = ["ResourceSignal", "ResourceFilter", "ResourceEvent"]


class ResourceSignal(Signal):

    def __init__(self, resource):
        super(ResourceSignal, self).__init__()
        self.resource = resource
    
    def __str__(self):
        return "<%s %s>" % (type(self).__name__, self.resource.id)

    def __repr__(self):
        return str(self)

#    def toJson(self):
#        j = super(ResourceSignal, self).toJson()
#        j['data']['resource'] = self.resource.id
#        return j

    def __getstate__(self):
        d = self.__dict__.copy()
        d['resource'] = self.resource.id
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.resource = Core.get_instance().get(d['resource'])

    

class ResourceFilter(Basetype):

    def __init__(self, onlyTypes=None, must_throw=None, **attributes):
        super(ResourceFilter, self).__init__(**attributes)
        self.onlyTypes = onlyTypes
        self.must_throw = must_throw

    def _checkId(self, id, ething = None):
        # resource id
        if not ething or not ething.is_db_loaded:
            return

        resource = ething.get(id) # raise an exception if the db is not already started

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
        if self.must_throw:

            signals_thrown_by_resource = [s.signal for s in list_registered_signals(resource)]

            signal = self.must_throw
            if isinstance(signal, string_types):
                signal = get_registered_class(signal)

            if signal not in signals_thrown_by_resource:
                raise ValueError("the resource %s does not throw the signal : %s" % (
                    str(resource),get_definition_pathname(signal)))

    def validate(self, value, context = None):

        resourceFilter = value
        ething = context.get('ething')

        if isinstance(resourceFilter, string_types):
            # can either be an id or an expression

            if ShortId.validate(resourceFilter):
                # resource id
                self._checkId(resourceFilter, ething)
            else:
                # expression
                if ething:
                    ok, message = ething.resourceQueryParser.check(resourceFilter)
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

    def toSchema(self, context = None):
        schema = super(ResourceFilter, self).toSchema(context)
        schema['type'] = "array"
        schema['items'] = {
            "type": "string"
        }
        schema['onlyTypes'] = self.onlyTypes
        return schema


@abstract
@attr('resource', type=ResourceFilter(), description="filter the resource emitting the signal")
class ResourceEvent(Event):

    signal = ResourceSignal

    def _filter(self, signal, core):
        # the event accepts only signal emitted from a resource

        resourceFromSignal = signal.resource

        resourceFilter = self.resource

        if resourceFilter is None:  # no filtering
            return True
        # can either be an id or an expression
        elif isinstance(resourceFilter, string_types):

            if ShortId.validate(resourceFilter):
                return resourceFilter == resourceFromSignal.id
            else:  # query string
                # check if the resource from the signal match the expression
                return resourceFromSignal.match(resourceFilter)

        elif isinstance(resourceFilter, list):  # array of resource ids
            return resourceFromSignal.id in resourceFilter

        return False
