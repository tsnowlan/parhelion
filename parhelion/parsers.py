from __future__ import print_function

import io
import json
import logging
import sys
import xml.etree.ElementTree as ET

from parhelion.models import XML_Model, XML_Element, XML_Attribute

class DataParser(object):
    current_fh = None
    models = {}
    curr_model = None
    _files = []

    def get_files(self):
        return self._files

    def set_files(self, files):
        if not isinstance(files, list):
            files = [files]
        self._files = files

    files = property(get_files, set_files)

    def __init__(self, files=[], **kwargs):
        self.files = files

        for k in kwargs:
            if hasattr(self, k):
                setattr(self, k, kwargs[k])
            else:
                raise ValueError("Invalid kwarg '{}'".format(k))

    def load(self, files=[]):
        if files:
            self.files = files

        if len(self.files) == 0:
            raise ValueError("No files to load")

        for fn in self.files:
            with io.open(fn, 'rb') as self.current_fh:
                self.parse()

        return self

    def parse(self):
        raise NotImplemented()

    def dump(self):
        raise NotImplemented()

    def analyze(self):
        raise NotImplemented()


class XMLParser(DataParser):
    def parse(self):
        etree = ET.parse(self.current_fh)
        root = etree.getroot()

        if self.models.get(root.tag) is None:
            self.models[root.tag] = XML_Model(name=root.tag, root_element=root.tag)
        self.curr_model = self.models[root.tag]

        self.parse_element(root)

        import pdb; pdb.set_trace()
        return self

    def parse_element(self, elt):
        elt_model = self.curr_model.get_element(elt.tag)
        if elt.tag not in self.curr_model.observations['elements']:
            self.curr_model.observations['elements'][elt.tag] = []
        self.curr_model.observations['elements'][elt.tag].append({
            "children": [c.tag for c in elt.getchildren()],
            "attribs": elt.attrib,
            "value": elt.text.strip() if isinstance(elt.text, str) else elt.text
        })

        for k in elt.attrib:
            elt_model.attribs.add(k)
            attrib_model = self.curr_model.get_attribute(k)

            if attrib_model.data_type is None:
                attrib_model.data_type = type(elt.attrib[k])

            if k not in self.curr_model.observations['attribs']:
                self.curr_model.observations['attribs'][k] = [elt.attrib[k]]
            else:
                self.curr_model.observations['attribs'][k].append(elt.attrib[k])

        # recursively add child to model and parse child elements
        for subelt in elt.getchildren():
            elt_model.children.add(subelt.tag)
            self.parse_element(subelt)

    def dump(self, to_file=None, to_fh=None):
        if to_file:
            to_fh = io.open(to_file, 'w')
        elif to_fh is None:
            to_fh = sys.stdout

        print(json.dumps(self.models, indent=4, sort_keys=True), file=to_fh)


class JSONParser(DataParser):
    pass
