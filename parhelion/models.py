from __future__ import print_function, absolute_import

import io
import json
import re

from parhelion.utils import abbrev, ParhelionJSONEncoder


############################################################
#                          Globals                         #
############################################################

MODEL_SUFFIX = '.parmodel.json'


############################################################
#                          General                         #
############################################################


class GenericModel(object):
    name = None
    observations = None

    def write(self):
        raise NotImplemented()

    @classmethod
    def load(self):
        raise NotImplemented()

    @property
    def clean_name(self):
        if cleaned_name is not None:
            # escape any characters likely to cause issues
            cleaned_name = re.sub(r'([\[\]\{\}:\\\/])', "\\\1", cleaned_name)
            # spaces to underscores
            cleaned_name = cleaned_name.replace(' ', '_')
        return cleaned_name


############################################################
#                            XML                           #
############################################################


class XMLModel(GenericModel):
    elements = None
    attribs = None
    root_element = None

    def __init__(self, name, root_element, **kwargs):
        self.root_element = root_element
        self.name = name
        self.observations = {
            "elements": {},
            "relationships": {},
            "attribs": {}
        }
        self.elements = {}
        self.attribs = {}
        self.filename = None

        for k in kwargs.keys():
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
            else:
                raise ValueError("Invalid parameter for XMLModel: '{}'".format(k))

    @property
    def clean_name(self):
        cleaned_name = self.name
        if cleaned_name is not None:
            # remove leading URL prefix that gets added to some elements
            cleaned_name = re.sub(r'^\{http:\/\/.+?\}', '', cleaned_name)
            # spaces to underscores
            cleaned_name = cleaned_name.replace(' ', '_')
        return cleaned_name

    @classmethod
    def load(cls, filename):
        with open(filename, 'rt') as input_fh:
            input_obj = json.load(input_fh)
        input_obj['filename'] = filename
        return cls(input_obj['name'], input_obj['root_element'], **input_obj)

    def write(self, filename=None, include_observations=False):
        if filename is not None:
            fname = filename
        elif self.filename is not None:
            fname = self.filename
        else:
            fname = self.clean_name + MODEL_SUFFIX

        if not fname.endswith(MODEL_SUFFIX):
            fname += MODEL_SUFFIX
        self.filename = fname

        if include_observations:
            output_obj = vars(self)
        else:
            output_obj = {k: getattr(self, k) for k in vars(self) if k != "observations"}

        with io.open(fname, 'wt') as output_fh:
            json.dump(
                output_obj,
                output_fh,
                sort_keys=True,
                indent=4,
                cls=ParhelionJSONEncoder
            )

    def get_element(self, elt):
        try:
            return self.elements[elt]
        except KeyError:
            self.elements[elt] = XMLElement(tag=elt)
            return self.elements[elt]

    def get_attribute(self, attrib):
        try:
            return self.attribs[attrib]
        except KeyError:
            self.attribs[attrib] = XMLAttribute(name=attrib)
            return self.attribs[attrib]


class XMLElement(object):
    tag = None
    children = None
    attribs = None
    types = None
    required_val = True

    def __init__(self, **kwargs):
        self.children = set() # tags of child elements
        self.attribs = set()  # attribute keys observed in the element
        self.types = set()
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
        return "<XMLElement tag={} children={} attribs={}>".format(
            self.tag,
            abbrev(','.join(sorted(self.children)), 16),
            abbrev(','.join(sorted(self.attribs)), 16)
        )


class XMLAttribute(object):
    name = None
    _dt = None
    min = None
    max = None
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
        return "<XMLAttribute name={} data_type={} min={} max={}>".format(
            self.name,
            self.data_type,
            self.min,
            self.max
        )

    data_type = property(get_data_type, set_data_type)
