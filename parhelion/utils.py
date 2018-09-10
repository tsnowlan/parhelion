import json

class ParhelionJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, set):
                return sorted(list(obj))
            else:
                return obj.__dict__
        except AttributeError:
            return super(__class__, self).default(obj)
