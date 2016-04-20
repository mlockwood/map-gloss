#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import packages and libraries
import re
import os

# Import variables
from src.gloss.constants import GRAMS, MODELS, PATH, EVAL


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'reference.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class Language(object):

    objects = {}

    def __init__(self, model, dataset, iso):
        self.model = model
        self.dataset = dataset
        self.iso = iso
        self.reference = {}  # {input_gloss: final_gloss}
        self.final = {}  # {final_gloss: True}

        Language.objects[(model, dataset, iso)] = self

    @staticmethod
    def add_reference(model, dataset, iso, gloss, final):
        # Select language object
        if (model, dataset, iso) not in Language.objects:
            Language(model, dataset, iso)
        language = Language.objects[(model, dataset, iso)]

        # Add gloss to glosses with value of final
        language.reference[gloss] = final
        language.final[final] = True

        return True


def load_references():
    # Set the path for the reference files
    path = '{}/out/reference'.format(PATH)

    # Search through the path for matching .ref files
    for dirpath, dirnames, filenames in os.walk(path):

        # Avoid redundant processing by reviewing dataset and language files
        if 'dataset' in dirpath or 'language' in dirpath:
            continue

        # For model .ref files
        for filename in [f for f in filenames if re.search('.ref$', f)]:
            # Open the file
            reader = open('{}/{}'.format(dirpath, filename), 'r')

            # For each line in the reader add the reference to the appropriate Language object
            for line in reader:
                line = line.rstrip()
                line = re.split(',', line)
                Language.add_reference(*line)

    return True
