#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

from utils.classes import DataModelTemplate


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'gloss/reference.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class Reference(DataModelTemplate):  # formerly Language

    json_path = []
    objects = {}

    def set_object_attrs(self):
        Reference.objects[(self.model, self.dataset, self.iso)] = self

    @staticmethod
    def add_reference(model, dataset, iso, gloss, final):
        # Select Reference object
        if (model, dataset, iso) not in Reference.objects:
            Reference(**{"model": model, "dataset": dataset, "iso": iso, "lookup": {}, "final": {}})
        ref = Reference.objects[(model, dataset, iso)]

        # Add gloss to glosses with value of final
        ref.lookup[gloss] = final  # {input_gloss: final_gloss}
        ref.final[final] = True  # {final_gloss: True}

    @classmethod
    def load_references(cls, out_path):
        # Search through the path for matching .ref files
        for root, dirs, files in os.walk('{}/out/reference'.format(out_path)):
            for file in [x for x in files if re.search('.ref$', x)]:
                cls.json_path.append(os.path.join(root, file))
        # Use DataModelTemplate load for Reference
        cls.load()