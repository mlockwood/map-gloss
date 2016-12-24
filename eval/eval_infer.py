#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from map_gloss.utils.confusion_matrix import CM, Compare
from map_gloss.eval.choices_reader import *

# Import errors
from map_gloss.eval.constants import INFER_BASELINE
from map_gloss.infer.constants import FTYPES
from map_gloss.infer.errors import *


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'eval/infer.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class Choices(object):

    objects = {}

    def __init__(self, file, model, dataset, iso, ftype='gold'):
        self.file = file
        self.choices_file = ChoicesFile(file)
        self.model = model
        self.dataset = dataset
        self.iso = iso
        self.ftype = ftype if ftype in FTYPES else InvalidFileTypeError(ftype)
        self.load_choices()
        Choices.objects[file] = self

    def load_choices(self):
        choices = {}
        tam = ['tenses', 'aspects', 'moods']
        for category in tam:
            for choice in eval('self.choices_file.{}()'.format(category)):
                if isinstance(choice, list):
                    choice = choice[0]
                choices[tuple([s.lower() for s in [self.model, self.dataset, self.iso, category, choice]])] = True

        for container in self.containers:
            for choice in choices:
                exec('container.{}[choice]=True'.format(self.ftype))

        return True

    @staticmethod
    def load_baseline4(dataset, language, containers):
        choices = {}
        for (category, choice) in INFER_BASELINE:
            choices[(dataset, language, category, choice)] = True

        for container in containers:
            for choice in choices:
                container.baseline4[choice] = True

        return True


class Container(object):

    objects = {}

    def __init__(self, model, container):
        self.model = model
        self.gold = {}
        self.baseline4 = {}
        self.baseline5 = {}
        self.final = {}
        Container.objects[container] = self

    @staticmethod
    def get(args):
        if args[1] not in Container.objects:
            Container(*args)
        return Container.objects[args[1]]

    def set_confusion_matrices(self):
        # Create a comparative confusion matrix of each baseline against the final
        final_cm = CM(self.gold, self.final, self.container + '_FINAL')
        self.compare4 = Compare(final_cm, CM(self.gold, self.baseline4, self.container + '_BASELINE4'))
        self.compare5 = Compare(final_cm, CM(self.gold, self.baseline5, self.container + '_BASELINE5'))

        # Set the path for the comparative cprf files
        path = '{}/reports/choices/{}/{}'.format(PATH, self.model, self.ctype)
        if self.model == self.container:
            path = '{}/reports/choices/{}'.format(PATH, self.model)

        # Write the comparative cprf files
        if not os.path.isdir(path):
            os.makedirs(path)
        self.compare4.write_cprf_file('{}/{}_comparison4'.format(path, self.container))
        self.compare5.write_cprf_file('{}/{}_comparison5'.format(path, self.container))

        return True
