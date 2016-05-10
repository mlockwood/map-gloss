#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import re
import os

# Import scripts

from src.gloss import model
from src.infer import choices

# Import classes
from src.eval.eval_infer import Choices, Container

# Import variables
from src.gloss.constants import EVAL
from src.gloss.reference import Language, load_references
from src.infer.constants import PATH, CHOICES


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'model.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


# Steps
# 1 load reference
# 2 for each language set path, file, and send to choices (twice: once for baseline, once for final)
# 3 once all choices are built run eval


# Run model and collect references
# model.process_models()
load_references()


def make_choices():
    # For each language with a reference
    for language in Language.objects:
        language = Language.objects[language]

        # Resolve path first
        path = '{}/out/choices/{}'.format(PATH, language.model)
        if not os.path.isdir(path):
            os.makedirs(path)

        # Add base of file name to path
        path += '/{}_{}_{}'.format(language.model, language.dataset, language.iso)

        # Build choices files
        choices.make_choices(language.reference, '{}_baseline5.choices'.format(path))
        choices.make_choices(language.final, '{}.choices'.format(path))


def eval_choices():
    # For each language with a reference
    for obj in Language.objects:
        language = Language.objects[obj]

        # Establish containers for each model
        containers = [(language.model, 'model'),
                      ('{}_{}'.format(language.model, language.dataset), 'dataset'),
                      ('{}_{}_{}'.format(language.model, language.dataset, language.iso), 'language')]

        # Convert containers to objects
        containers = [Container.get((language.model, container[0], container[1])) for container in containers]

        # Load choices files for each loadable file
        # Resolve path first
        path = '{}/out/choices/{}'.format(PATH, language.model)
        if not os.path.isdir(path):
            os.makedirs(path)

        # Add base of file name to path
        path += '/{}_{}_{}'.format(language.model, language.dataset, language.iso)

        Choices(CHOICES[language.dataset][language.iso], language.model, language.dataset, language.iso, containers,
                ftype='gold')
        Choices.load_baseline4(language.dataset, language.iso, containers)
        Choices('{}_baseline5.choices'.format(path), language.model, language.dataset, language.iso, containers,
                ftype='baseline5')
        Choices('{}.choices'.format(path), language.model, language.dataset, language.iso, containers, ftype='final')

    # Write CPRF for the inference evaluation
    for obj in Container.objects:
        container = Container.objects[obj]
        container.set_confusion_matrices()


make_choices()
eval_choices()
