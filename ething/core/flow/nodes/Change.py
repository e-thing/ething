# coding: utf-8
from .. import *


rule_item = OneOf([
    ('set', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob'))),
        ('to', Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env')))
    ]))),
    ('change', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob'))),
        ('search', Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'env'))),
        ('replace', Descriptor(('msg', 'flow', 'glob', 'string', 'number', 'boolean', 'timestamp', 'env')))
    ]))),
    ('delete', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob')))
    ]))),
    ('move', Dict(mapping=OrderedDict([
        ('value', Descriptor(('msg', 'flow', 'glob'))),
        ('to', Descriptor(('msg', 'flow', 'glob')))
    ])))
])

@meta(icon='mdi-pencil', category="function")
@attr('rules', type=Array(rule_item), default=[{
    'type': 'set',
    'value': {
        'value': {'type':'msg', 'value':'payload'},
        'to': {'type':'string', 'value':''}
    }
}])
class Change(Node):
    """
    Set, change, delete or move properties of a message, flow context or global context.

    The node can specify multiple rules that will be applied in the order they are defined.
    """

    INPUTS = ['default']
    OUTPUTS = ['default']

    def main(self, **inputs):
        _msg = inputs['default']
        _context = {
            'msg': _msg,
            'flow': self.flow
        }

        for rule in self.rules:
            rule_type = rule.type
            rule_data = rule.value

            if rule_type == 'set':
                val = rule_data['to'].get(**_context)
                rule_data['value'].set(val, **_context)
            elif rule_type == 'change':
                val = rule_data['to'].get(**_context)
                pattern = rule_data['search'].get(**_context)
                repl = rule_data['replace'].get(**_context)
                new_val = re.search(pattern, repl, val)
                rule_data['value'].set(new_val, **_context)
            elif rule_type == 'delete':
                rule_data['value'].delete(**_context)
            elif rule_type == 'move':
                val = rule_data['value'].get(**_context)
                rule_data['to'].set(val, **_context)
                rule_data['value'].delete(**_context)

        self.emit(_msg)
