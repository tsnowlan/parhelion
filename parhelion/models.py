import re

class XML_Element(object):
    tag = None
    children = set() # names of other XML_Element.tag values
    attribs = set()  # names of

    def __init__(self, **kwargs):
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])

    @property
    def has_children(self):
        return bool(self.children)

    @property
    def has_attribs(self):
        return bool(self.attribs)

    def __repr__(self):
        return "<XML_Element tag={} children={} attribs={}>".format(
            self.tag,
            ','.join(sorted(self.children)),
            ','.join(sorted(self.attribs))
        )


class XML_Attribute(object):
    name = None
    _dt = None
    min_value = None
    max_value = None
    re_pattern = None

    def __init__(self, name, **kwargs):
        self.name = name
        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
            else:
                raise ValueError("Invalid kwarg '{}'".format(k))

    def set_data_type(self, data_type):
        self._dt = re.sub(r"<class '(.+?)'>", "\\1", str(data_type))

    def get_data_type(self):
        return self._dt

    def __repr__(self):
        return "<XML_Attribute name={} _dt={} min_value={} max_value={}>".format(
            self.name,
            self._dt,
            self.min_value,
            self.max_value
        )

    data_type = property(get_data_type, set_data_type)


class XML_Model(object):
    @classmethod
    def load(cls, filename):
        raise NotImplemented()

    def __init__(self, name, root_element, **kwargs):
        self.observations = {
            "elements": {},
            "relationships": {},
            "attribs": {}
        }
        self.elements = {}
        self.attribs = {}

        self.root_element = root_element
        self.name = name

    def write(self, filename=None):
        raise NotImplemented()

    def get_element(self, elt):
        try:
            return self.elements[elt]
        except KeyError:
            self.elements[elt] = XML_Element(tag=elt)
            return self.elements[elt]

    def get_attribute(self, attrib):
        try:
            return self.attribs[attrib]
        except KeyError:
            self.attribs[attrib] = XML_Attribute(name=attrib)
            return self.attribs[attrib]