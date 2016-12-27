#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from map_gloss.infer.choices_reader import ChoicesFile
from map_gloss.infer.constants import INFER_BASELINE


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__email__ = 'lockwm@uw.edu'


def load_choices(dataset, iso, file):
    choices_file = ChoicesFile(file)
    choices = {}
    tam = ['tenses', 'aspects', 'moods']
    for category in tam:
        for choice in eval('choices_file.{}()'.format(category)):
            if isinstance(choice, list):
                choice = choice[0]
            choices[tuple([s.lower() for s in [dataset, iso, category, choice]])] = True
    return choices


def load_model_choices(datasets, languages):
    gold = {}
    for language in languages:
        gold.update(load_choices(language[0], language[1], datasets[language[0]]["iso_list"][language[1]]["choices"]))
    return gold


def load_baseline4(dataset, iso):
    choices = {}
    for (category, choice) in INFER_BASELINE:
        choices[(dataset, iso, category, choice)] = True
    return choices


def load_model_baseline4(languages):
    b4 = {}
    for language in languages:
        b4.update(load_baseline4(*language))
    return b4