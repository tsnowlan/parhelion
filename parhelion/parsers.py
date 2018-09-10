from __future__ import print_function

from collections import Counter
import datetime
import io
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET

from parhelion.models import XMLModel, XMLElement, XMLAttribute

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
            self.models[root.tag] = XMLModel(name=root.tag, root_element=root.tag)
        self.curr_model = self.models[root.tag]

        self.parse_element(root)

        return self

    def parse_element(self, elt):
        elt_model = self.curr_model.get_element(elt.tag)
        if elt.tag not in self.curr_model.observations['elements']:
            self.curr_model.observations['elements'][elt.tag] = []
        self.curr_model.observations['elements'][elt.tag].append({
            "children": [c.tag for c in elt.getchildren()],
            "attribs": elt.attrib.keys(),
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

    def analyze(self):
        for attrib in self.curr_model.attribs:
            attr_model = self.curr_model.attribs[attrib]
            for obs in self.curr_model.observations['attribs'][attrib]:
                if attr_model.data_type == 'str':
                    obs_val = len(obs)
                elif attr_model.data_type == 'int':
                    obs_val = int(obs)
                elif attr_model.data_type == 'float':
                    obs_val = float(obs)
                else:
                    logger.warn("Unknown data_type encoutered on attrib '{}': {}".format(attrib, attr_model.data_type))
                    break

                if attr_model.min is None or obs_val < attr_model.min:
                    attr_model.min = obs_val

                if attr_model.max is None or obs_val > attr_model.max:
                    attr_model.max = obs_val


        re_isfloat = re.compile('^-?\d*\.\d+$')
        re_isbool = re.compile('^true|false$', re.IGNORECASE)
        for elt in self.curr_model.elements:
            elt_model = self.curr_model.elements[elt]
            for obs in self.curr_model.observations['elements'][elt]:
                if obs['value'] is None or obs['value'] == "":
                    elt_model.required_val = False
                    elt_model.types.add('None')
                elif obs['value'].isnumeric():
                    elt_model.types.add('int')
                elif re.search(re_isfloat, obs['value']):
                    elt_model.types.add('float')
                elif re.search(re_isbool, obs['value']):
                    elt_model.types.add('bool')
                else:
                    elt_model.types.add('str')

        return self

    def dump(self):
        for model in self.models.values():
            print("Writing model file for {}".format(model.name))
            model.write()


class JSONParser(DataParser):
    pass
