# coding: utf-8
from .. import *
import collections


value_descriptor = Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'env', 'prev'))
value_str_descriptor = Descriptor(('msg', 'flow', 'glob', 'string', 'env', 'prev'))

filter_type = OneOf([
    ('==', value_descriptor),
    ('!=', value_descriptor),
    ('<' , value_descriptor),
    ('<=', value_descriptor),
    ('>' , value_descriptor),
    ('>=', value_descriptor),
    ('between', Dict(mapping=OrderedDict([
        ('min', value_descriptor),
        ('max', value_descriptor)
    ])), 'is between'),
    ('contains', value_str_descriptor),
    ('regex', value_str_descriptor, 'matches regex'),
    ('true', None, 'is true'),
    ('false', None, 'is false'),
    ('none', None, 'is none'),
    ('not_none', None, 'is not none'),
    ('type', Enum(['string','number','boolean','array','object','none']), 'is of type'),
    ('empty', None, 'is empty'),
    ('not_empty', None, 'is not empty'),
    ('go_above', Descriptor(('msg', 'flow', 'glob', 'number', 'env')), 'go above'),
    ('go_under', Descriptor(('msg', 'flow', 'glob', 'number', 'env')), 'go under'),
    ('rising_edge', None, 'rising edge'),
    ('falling_edge', None, 'falling edge'),
    ('expression', ObjectPathExp()),
])

@meta(icon='mdi-filter', category="condition")
@attr('last', mode=PRIVATE, default=None) # holds the last value
@attr('filter', type=filter_type, default={'type':'==', 'value':{'type':'string', 'value':''}})
@attr('data', type=Descriptor(('flow', 'glob', 'msg', 'expression')), default={'type':'msg','value':'payload'}, description='The data to filter.')
class Switch(Node):
    """
    Route messages based on their property values or sequence position
    """
    INPUTS = ['default']
    OUTPUTS = ['default', 'fail']

    def main(self, **inputs):
        old_val = self.last
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': self.flow,
            'prev_val': old_val
        }

        filter_type = self.filter.type
        val = self.data.get(**_context)
        res = None

        try:
            if filter_type == '==':
                filter_value = self.filter.value.get(**_context)
                res = val == filter_value
            elif filter_type == '!=':
                filter_value = self.filter.value.get(**_context)
                res = val != filter_value
            elif filter_type == '<':
                filter_value = self.filter.value.get(**_context)
                res = val < filter_value
            elif filter_type == '<=':
                filter_value = self.filter.value.get(**_context)
                res = val <= filter_value
            elif filter_type == '>':
                filter_value = self.filter.value.get(**_context)
                res = val > filter_value
            elif filter_type == '>=':
                filter_value = self.filter.value.get(**_context)
                res = val >= filter_value
            elif filter_type == 'between':
                min_val = self.filter.value['min'].get(**_context)
                max_val = self.filter.value['max'].get(**_context)
                res = val >= min_val and val <= max_val
            elif filter_type == 'contains':
                filter_value = self.filter.value.get(**_context)
                res = filter_value in val
            elif filter_type == 'regex':
                filter_value = self.filter.value.get(**_context)
                res = bool(re.search(filter_value, val))
            elif filter_type == 'true':
                res = val is True
            elif filter_type == 'false':
                res = val is False
            elif filter_type == 'none':
                res = val is None
            elif filter_type == 'not_none':
                res = val is not None
            elif filter_type == 'type':
                t = self.filter.value
                if t=='string':
                    res = isinstance(val, string_types)
                elif t=='number':
                    res = isinstance(val, number_types)
                elif t=='boolean':
                    res = isinstance(val, bool)
                elif t=='array':
                    res = isinstance(val, collections.Sequence)
                elif t=='object':
                    res = isinstance(val, collections.Mapping)
                elif t=='none':
                    res = val is None
            elif filter_type == 'empty':
                res = len(val) == 0
            elif filter_type == 'not_empty':
                res = len(val) != 0
            elif filter_type == 'go_above':
                filter_value = self.filter.value.get(**_context)
                res = old_val is not None and old_val < filter_value and val >= filter_value
            elif filter_type == 'go_under':
                filter_value = self.filter.value.get(**_context)
                res = old_val is not None and old_val > filter_value and val <= filter_value
            elif filter_type == 'rising_edge':
                res = old_val is not None and old_val == False and val == True
            elif filter_type == 'falling_edge':
                res = old_val is not None and old_val == True and val == False
            elif filter_type == 'expression':
                filter_value = self.filter.value
                res = bool(evaluate(filter_value, val))
        except:
            res = None

        # save the last value
        self.last = val

        self.emit(_msg, port='default' if res else 'fail')


