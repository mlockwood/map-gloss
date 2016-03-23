#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = infer_tam.py
__author__ = MichaelLockwood
__projectclass__ = LING575
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Infer Tense, Aspect, and Mood
__date__ = May2015
__credits__ = None
__collaborators__ = None

This module loads enriched XIGT data and automatically builds TAM choices
files. This additionally automatically loads eval_tam.py to evaluate the
precision, recall, and f-score of the automated choices file output against
the gold standard.
"""

"""
    user_preference -- allow the user to decide what output system
                             the tags should be; 0) Leipzig, 1) GOLD,
                             2) author
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
import eval_tam
import map_gloss

class Inference:

    glosses = {}
    equivalencies = {}
    agg_path = PathSetter.find_path('aggregation')
    choices_path = os.getcwd() + '/tam_choices'
    languages = {}

    def map_glosses(datasets):
        glosses = map_gloss.MapGloss.produce(datasets)
        Inference.load_standard_glosses()
        # Record dataset languages and their paths
        for dataset in datasets:
            for iso in dataset[0]:
                Inference.languages[(dataset[1], iso, dataset[0][iso])] = True
        # Create a TAM choices subdirectory for outputs
        if not os.path.exists(Inference.choices_path):
            os.makedirs(Inference.choices_path)
        # Build a choices file and a base choices file for each language
        for iso in glosses:
            # Main inference file
            file = Inference.choices_path + '/' + str(iso[1]) + '.choices'
            choices = Choices(iso[0], iso[1], file, glosses[iso])
            choices.set_choices()
            # Baseline file
            file = Inference.choices_path + '/' + str(iso[1]) + '_base.choices'
            choices = Choices(iso[0], iso[1], file, glosses[iso]['<obs>'])
            choices.set_choices()
        # Evaluate all files
        Inference.evaluate()
        return True

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
            gloss_categories = re.split('-', line[2])
            if not gloss_categories:
                print(str(line[0]) + '/' + str(line[1]) + ' does not have ' +
                      'any known categories.')
            Inference.glosses[line[0]] = gloss_categories
            Inference.glosses[line[1]] = gloss_categories
            Inference.equivalencies[line[0]] = line[1]
            Inference.equivalencies[line[1]] = line[0]
        reader.close()
        return True

    def evaluate():
        for iso in Inference.languages:
            eval_tam.Language(iso[0], iso[1], iso[2])
        for dataset in eval_tam.Dataset.objects:
            eval_tam.Dataset.objects[dataset].process_cprf_files()
        return True

class Choices:

    objects = {}
    radio = {'fut': 'future', 'future': 'future', 'past': 'past',
             'pst': 'past', 'prs': 'present', 'present': 'present'}

    def __init__(self, dataset, iso, file, glosses):
        self._dataset = dataset
        self._iso = iso
        self._file = file
        self._choices_text = ''
        self._glosses = glosses
        self._categories = {}
        Choices.objects[(dataset, iso)] = self

    def set_choices(self):
        self._choices_text = ('section=tense-aspect-mood\n' +
                              'tense-definition=choose\n')
        # Assign glosses to categories (MOM correction here)
        for gloss in self._glosses:
            if gloss == '<obs>':
                continue
            try:
                if Inference.glosses[gloss][0] not in self._categories:
                    self._categories[Inference.glosses[gloss][0]] = {}
                self._categories[Inference.glosses[gloss][0]][gloss] = True
            except:
                pass
        # Build tense, aspect, and mood from categories
        tam = ['tense', 'aspect', 'mood']
        for category in tam:
            if category not in self._categories:
                continue
            rule = 1
            for gloss in eval('self._categories[\'' + str(category) + '\']'):
                if gloss in Choices.radio:
                    self.write_radio_choices(Choices.radio[gloss])
                else:
                    self.write_choices(category, rule, gloss, category)
                    rule += 1
        self.export_choices()
        return True

    def export_choices(self):
        writer = open(self._file, 'w')
        writer.write(self._choices_text)
        writer.close()
        return True

    def write_radio_choices(self, value):
        self._choices_text += str(value).lower() + '=on\n'
        return True

    def write_radio_choices_subtype(self, rule, value, supertype):
        self._choices_text += (' ' + str(supertype).lower() + '-subtype' +
                               str(rule) + '_name=' + str(value) + '\n')
        return True

    def write_choices(self, category, rule, value, supertype):
        self._choices_text += (' ' + str(category) + str(rule) + '_name=' +
                               str(value) + '\n  ' + str(category) + str(rule)
                               + '_supertype1_name=' + str(category) + '\n')
        return True
        
"""
567 Dataset Collections-------------------------------------------------
"""
dev1 = {# Dev 1
        'jpn': '/data/567/dev1/jpn/',
        'jup': '/data/567/dev1/jup/',
        'pbt': '/data/567/dev1/pbt/',
        'rus': '/data/567/dev1/rus/',
        'sna': '/data/567/dev1/sna/'
        }
dev2 = {# Dev 2
        'bre': '/data/567/dev2/bre/',
        'fra': '/data/567/dev2/fra/',
        'lut': '/data/567/dev2/lut/',
        'ojg': '/data/567/dev2/ojg/',
        'sci': '/data/567/dev2/sci/',
        'tam': '/data/567/dev2/tam/'
        }
test = {# Test
        'ain': '/data/567/test/ain/',
        'hbs': '/data/567/test/hbs/',
        'hix': '/data/567/test/hix/',
        'inh': '/data/567/test/inh/',
        'jaa': '/data/567/test/jaa/',
        'kat': '/data/567/test/kat/',
        'tha': '/data/567/test/tha/',
        'vie': '/data/567/test/vie/',
        }

Inference.map_glosses([(dev1, 'dev1'), (dev2, 'dev2'), (test, 'test')])
