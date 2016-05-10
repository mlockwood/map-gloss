#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = eval_infer.py
__author__ = MichaelLockwood
__projectclass__ = LING575
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Evaluate Tense, Aspect, and Mood
__date__ = June2015
__credits__ = None
__collaborators__ = None

This module loads two sets of choices files; a gold standard set and an
auto-generated set. The evaluation procedure compares the gold standard
against the inference set and a baseline set.
"""
import os
import re
import sys


# Import scripts
from src.eval import confusion_matrix
from src.utils import choices_reader


# Import errors
import src.infer.errors as InferErrors

from src.eval.constants import INFER_BASELINE
from src.infer.constants import PATH, CTYPES, FTYPES


class Choices(object):

    objects = {}

    def __init__(self, file, model, dataset, iso, containers, ftype='gold'):
        self.file = file
        self.choices_file = choices_reader.ChoicesFile(file)
        self.model = model
        self.dataset = dataset
        self.iso = iso
        self.containers = containers

        if ftype in FTYPES:
            self.ftype = ftype
        else:
            raise InferErrors.InvalidFileTypeError(ftype)

        self.load_choices()

        Choices.objects[file] = self

    def load_choices(self):
        choices = {}
        tam = ['tenses', 'aspects', 'moods']
        for category in tam:
            for choice in eval('self.choices_file.{}()'.format(category)):
                if isinstance(choice, list):
                    choice = choice[0]
                choices[tuple([s.lower() for s in [self.dataset, self.iso, category, choice]])] = True

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
    types = {'language': True, 'dataset': True, 'model': True}

    def __init__(self, model, container, ctype='language'):
        """
        Containers are hierarchy values for glosses such as language,
        dataset, and collection.
        :param container: {language: model_dataset_iso,
                           dataset: model_dataset,
                           model: model}
        :param ctype: identify which container is used
        """
        self.model = model
        self.container = container

        if ctype in Container.types:
            self.ctype = ctype
        else:
            raise InferErrors.InvalidContainerTypeError(ctype)

        # Attribute data structures
        self.gold = {}
        self.baseline4 = {}
        self.baseline5 = {}
        self.final = {}

        # Confusion matrices and Compare objects
        self.baseline4_cm = {}
        self.baseline5_cm = {}
        self.final_cm = {}
        self.compare4 = {}
        self.compare5 = {}

        Container.objects[container] = self

    @staticmethod
    def get(args):
        if args[1] not in Container.objects:
            Container(*args)
        return Container.objects[args[1]]

    def set_confusion_matrices(self):
        # Create initial confusion matrices for the baseline and the final sets
        self.baseline4_cm = confusion_matrix.CM(self.gold, self.baseline4, self.container + '_BASELINE4')
        self.baseline5_cm = confusion_matrix.CM(self.gold, self.baseline5, self.container + '_BASELINE5')
        self.final_cm = confusion_matrix.CM(self.gold, self.final, self.container + '_FINAL')

        # Create a comparative confusion matrix of each baseline against the final
        self.compare4 = confusion_matrix.Compare(self.final_cm, self.baseline4_cm)
        self.compare5 = confusion_matrix.Compare(self.final_cm, self.baseline5_cm)

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
