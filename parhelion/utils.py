import collections
import io
import json


class ParhelionJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, collections.Iterable):
                return sorted(list(obj))
            else:
                return obj.__dict__
        except AttributeError:
            return super(__class__, self).default(obj)

def abbrev(long_string, max_length=8, tail='...'):
    if len(long_string) > max_length:
        long_string = long_string[0:max_length] + tail
    return long_string
