# coding: utf-8

from .Condition import Condition
from ...entity import *


number_types = integer_types + (float, )


def _cast_to_number(value):
    return float(value)


def _cast_to_string(value):
    return str(value)


def _cast_to_bool(value):
    if isinstance(value, string_types):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            try:
                return bool(float(value))
            except:
                return False
    return bool(value)


def _check_number(value):
    if not isinstance(value, number_types):
        raise ValueError('not a number : %s' % value)


@meta(icon='mdi-filter')
@attr('last', mode=PRIVATE, default=None) # holds the last value
@attr('filter', type=Dict(allow_extra=True, mapping={
    'type': Enum(('exists', '==', '>', '>=', '<', '<=', 'go above', 'go under', 'regex', 'rising edge', 'falling edge'))
}))
@attr('name', type=String(allow_empty=False), description='The name of the property (ie: temperature, humidity ...) to filter only the signal corresponding to this property.')
class DataFilter(Condition):
    """ filter signal data """

    def test(self, signal, core):

        name = self.name
        filter = self.filter
        filter_type = filter.get('type')
        value = filter.get('value')

        try:
            data = getattr(signal, name)
        except:
            return False

        if filter_type == 'exists':
            return True
        elif filter_type == '==':

            # make value the same type of data
            if isinstance(data, number_types):
                norm_value = _cast_to_number(value)
            elif isinstance(data, bool):
                norm_value = _cast_to_bool(value)
            else:
                norm_value = value

            return norm_value == data

        elif filter_type == '>':
            return _check_number(data) > _cast_to_number(value)
        elif filter_type == '>=':
            return _check_number(data) >= _cast_to_number(value)
        elif filter_type == '<':
            return _check_number(data) < _cast_to_number(value)
        elif filter_type == '<=':
            return _check_number(data) <= _cast_to_number(value)
        elif filter_type == 'regex':
            return re.search(self._cast_to_string(value), self._cast_to_string(data))
        elif filter_type == 'go above':
            _check_number(data)
            threshold = _cast_to_number(value)
            result = self.last is not None and self.last < threshold and data >= threshold
            # save the last value
            self.last = data
            return result
        elif filter_type == 'go under':
            _check_number(data)
            threshold = _cast_to_number(value)
            result = self.last is not None and self.last > threshold and data <= threshold
            # save the last value
            self.last = data
            return result
        elif filter_type == 'rising edge':
            data = _cast_to_bool(data)
            threshold = _cast_to_bool(value)
            result = self.last is not None and self.last is False and data is True
            # save the last value
            self.last = data
            return result
        elif filter_type == 'falling edge':
            data = _cast_to_bool(data)
            threshold = _cast_to_bool(value)
            result = self.last is not None and self.last is True and data is False
            # save the last value
            self.last = data
            return result
        else:
            raise Exception('invalid filter : %s' % filter_type)




