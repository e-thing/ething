from future.utils import string_types, integer_types
import re
import collections


class Accessor(object):
    @classmethod
    def parse(cls, path):
        raise NotImplementedError()

    def __init__(self, obj):
        self.obj = obj

    def get(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def set(self, val):
        raise NotImplementedError()


class GlobField(Accessor):
    re_field = re.compile('\.\*')  # .*

    @classmethod
    def parse(cls, path):
        m = cls.re_field.match(path)
        if m:
            def build(obj):
                if isinstance(obj, collections.MutableMapping):
                    return [Field(obj, a, 'index') for a in obj]
                elif not isinstance(obj, Field.attr_lookup_black_list):
                    return [Field(obj, a, 'attr') for a in obj.__dict__]

            return m.group(0), build


class Field(Accessor):
    re_field = re.compile('\.[a-zA-Z0-9_]+')  # .field

    attr_lookup_black_list = string_types + integer_types + (float, bool)

    @classmethod
    def parse(cls, path):
        m = cls.re_field.match(path)
        if m:
            def build(obj):
                field = m.group(0)[1:]
                if isinstance(obj, collections.MutableMapping):
                    return cls(obj, field, 'index')
                elif not isinstance(obj, Field.attr_lookup_black_list):
                    return cls(obj, field, 'attr')
            return m.group(0), build

    def __init__(self, obj, field, mode='index'):
        super(Field, self).__init__(obj)
        self.field = field
        self.mode = mode

    def get(self):
        if self.mode == 'index':
            return self.obj[self.field]
        else:
            return getattr(self.obj, self.field)

    def delete(self):
        if self.mode == 'index':
            del self.obj[self.field]
        else:
            delattr(self.obj, self.field)

    def set(self, val):
        if self.mode == 'index':
            self.obj[self.field] = val
        else:
            setattr(self.obj, self.field, val)


class Index(Accessor):
    re_index = re.compile('\[(-?[0-9]+)\]')  # [-12]

    @classmethod
    def parse(cls, path):
        m = cls.re_index.match(path)
        if m:
            def build(obj):
                if isinstance(obj, collections.MutableSequence):
                    return cls(obj, int(m.group(1)))

            return m.group(0), build

    def __init__(self, obj, index):
        super(Index, self).__init__(obj)
        self.index = index

    def get(self):
        return self.obj[self.index]

    def delete(self):
        del self.obj[self.index]

    def set(self, val):
        self.obj[self.index] = val


def jsonpath(path, obj, action='get', args=None, kwargs=None):
    # format path
    if re.match('[a-zA-Z0-9_]', path):
        # accept starting with a field
        path = '$.' + path

    if path.startswith('$'):
        path = path[1:]

    context = {
        'accessors': [Field, Index, GlobField],
        'path': path,
        'ptr': obj,
        'ptrs': [obj],
        'action': action,
        'action_args': args or [],
        'action_kwargs': kwargs or {},
        'res': []
    }
    while True:

        for accessor_cls in context['accessors']:
            res = accessor_cls.parse(context['path'])
            if res:
                part, accessor_builder = res
                accessors = []
                for ptr in context['ptrs']:
                    try:
                        accessors_ = accessor_builder(ptr)
                    except Exception as e:
                        continue
                    if not accessors_:
                        continue
                    if isinstance(accessors_, Accessor):
                        accessors_ = [accessors_]
                    accessors = accessors + accessors_
                break
        else:
            raise Exception('invalid character "%s"' % context['path'][0])

        if not accessors:
            break

        next_path = context['path'][len(part):]

        if next_path == '':
            # end
            res = []
            for accessor in accessors:
                try:
                    res.append(getattr(accessor, context['action'])(*context['action_args'], **context['action_kwargs']))
                except:
                    pass
            context['res'] = res
            break
        else:
            # continue parsing the path
            context['path'] = next_path
            ptrs = []
            for accessor in accessors:
                try:
                    ptrs.append(accessor.get())
                except:
                    pass
            context['ptrs'] = ptrs

    return context['res']

