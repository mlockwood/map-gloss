#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = eval_tam.py
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

class PathSetter:

    def set_pythonpath(directory='', subdirectory=''):
        if directory:
            directory = PathSetter.find_path(directory)
            if subdirectory:
                if directory[-1] != '/' and subdirectory[0] != '/':
                    directory += '/'
                directory += subdirectory
        else:
            directory = os.getcwd()
        sys.path.append(directory)
        return True

    def find_path(directory):
        match = re.search('/' + str(directory), os.getcwd())
        if not match:
            raise IOError(str(directory) + 'is not in current working ' +
                          'directory')
        return os.getcwd()[:match.span()[0]] + '/' + directory

# Add aggregation and map_gloss to PYTHONPATH
PathSetter.set_pythonpath('aggregation')
PathSetter.set_pythonpath('map_gloss')
# Import scripts
from src.evaluation import confusion_matrix
from src.utils import choices_reader


class Evaluation:

    gold = {}
    agg_path = PathSetter.find_path('aggregation')
    choices_path = os.getcwd() + '/tam_choices'
    baseline = {('tense', 'past'): True, ('tense', 'future'): True,
                ('tense', 'present'): True, ('aspect', 'perfective'): True,
                ('aspect', 'imperfective'): True}

    def load_standard_glosses():
        reader = open('standard_glosses', 'r')
        for row in reader:
            if row[0] == '#':
                continue
            line = row.rstrip('\n')
            line = line.lower()
            line = re.sub(' ', '', line)
            line = line.split(',')
            # Set standard glosses
            Evaluation.gold[line[0].lower()] = line[1].lower()
            Evaluation.gold[line[1].lower()] = line[1].lower()
        reader.close()
        return True

class Dataset:

    objects = {}

    def __init__(self, dataset):
        self._dataset = dataset
        self._iso_list = {}
        self._gold = {}
        self._infer = {}
        self._base1 = {}
        self._base2 = {}
        Dataset.objects[dataset] = self

    def set_base1(self):
        for iso in self._iso_list:
            for gloss in Evaluation.baseline:
                self._base1[(iso, gloss[0], gloss[1])] = True
        return True

    def process_cprf_files(self):
        self.set_base1()
        # Set confusion matrices
        self._infer_cm = confusion_matrix.CM(self._gold, self._infer,
                                             'infer_' + str(self._dataset))
        self._base1_cm = confusion_matrix.CM(self._gold, self._base1,
                                             'base1_' + str(self._dataset))
        self._base2_cm = confusion_matrix.CM(self._gold, self._base2,
                                             'base2_' + str(self._dataset))
        # Create CRPF files
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/tam_cprf'):
            os.mkdir(os.getcwd() + '/evaluation/tam_cprf')
        self._ib1 = confusion_matrix.Compare('infer_' + str(self._dataset),
                                             'base1_' + str(self._dataset))
        self._ib1.write_cprf_file('evaluation/tam_cprf/' + str(self._dataset) +
                                  '_baseline1')
        self._ib2 = confusion_matrix.Compare('infer_' + str(self._dataset),
                                             'base2_' + str(self._dataset))
        self._ib2.write_cprf_file('evaluation/tam_cprf/' + str(self._dataset) +
                                  '_baseline2')
        return True

class Language:

    objects = {}

    def __init__(self, dataset, iso, path):
        self._dataset = dataset
        self._iso = iso
        self._path = path
        self._gold_path = Language.set_gold_path(path)
        self._infer_path = Language.set_infer_path(iso)
        self._base_path = Language.set_base_path(iso)
        Language.objects[(dataset, iso)] = self
        self._gold = Choices(dataset, iso, 'gold', self._gold_path)
        self._infer = Choices(dataset, iso, 'infer', self._infer_path)
        self._base1 = Evaluation.baseline
        self._base2 = Choices(dataset, iso, 'base2', self._base_path)
        self.process_cprf_files()

    def clear_class_data():
        Language.objects = {}

    def set_gold_path(path):
        if path[-1] == '/':
            return (Evaluation.agg_path + path + 'choices.up')
        else:
            return (Evaluation.agg_path + '/' + path + 'choices.up')

    def set_infer_path(iso):
        return (Evaluation.choices_path + '/' + str(iso) + '.choices')

    def set_base_path(iso):
        return (Evaluation.choices_path + '/' + str(iso) + '_base.choices')

    def process_cprf_files(self):
        # Set confusion matrices
        self._infer_cm = confusion_matrix.CM(self._gold._categories,
                                             self._infer._categories,
                                             'infer_' + str(self._iso))
        self._base1_cm = confusion_matrix.CM(self._gold._categories,
                                             self._base1,
                                             'base1_' + str(self._iso))
        self._base2_cm = confusion_matrix.CM(self._gold._categories,
                                             self._base2._categories,
                                             'base2_' + str(self._iso))
        # Create CRPF files
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/tam_cprf'):
            os.mkdir(os.getcwd() + '/evaluation/tam_cprf')
        self._ib1 = confusion_matrix.Compare('infer_' + str(self._iso),
                                             'base1_' + str(self._iso))
        self._ib1.write_cprf_file('evaluation/tam_cprf/' + str(self._iso) +
                                  '_baseline1')
        self._ib2 = confusion_matrix.Compare('infer_' + str(self._iso),
                                             'base2_' + str(self._iso))
        self._ib2.write_cprf_file('evaluation/tam_cprf/' + str(self._iso) +
                                  '_baseline2')
        return True
                            
class Choices:

    objects = {}

    def __init__(self, dataset, iso, value, path):
        self._dataset = dataset
        if dataset in Dataset.objects:
            self._dataset_obj = Dataset.objects[dataset]
            self._dataset_obj._iso_list[iso] = True
        else:
            self._dataset_obj = Dataset(dataset)
            self._dataset_obj._iso_list[iso] = True
        self._iso = iso
        self._value = value
        self._path = path
        self._choices_file = ''
        self._categories = {}
        Choices.objects[(dataset, iso, value)] = self
        self.load_file()

    def load_file(self):
        self._choices_file = choices_reader.ChoicesFile(self._path)
        tam = ['tenses', 'aspects', 'moods']
        for cat in tam:
            for value in eval('self._choices_file.' + str(cat) + '()'):
                if isinstance(value, list):
                    value = value[0]
                if value.lower() in Evaluation.gold and self._value != 'base2':
                    value = Evaluation.gold[value.lower()]
                exec('self._categories[(\'' + str(cat)[:-1] + '\',\'' +
                     str(value) + '\')]=True')
        for gloss in self._categories:
            exec('self._dataset_obj._' + str(self._value) + '[(\'' +
                 str(self._iso) + '\',\'' + str(gloss[0]) + '\',\'' +
                 str(gloss[1]) + '\')]=True')
        return True

Evaluation.load_standard_glosses()
