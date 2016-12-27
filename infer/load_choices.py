#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from infer.choices_reader import ChoicesFile
from infer.constants import INFER_BASELINE


__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__email__ = 'lockwm@uw.edu'


def load_choices(dataset, iso, file):
    """
    Loads a choices file. Choices are then set as tuple keys by
    (dataset, iso, category, choice).
    Args:
        dataset: current dataset
        iso: current iso
        file: choices file path

    Returns: dictionary of choices

    """
    choices_file = ChoicesFile(file)
    choices = {}
    tam = ['tenses', 'aspects', 'moods']

    # Currently only processes TAM
    for category in tam:

        # Calls functions from choices file to extract choices by category
        for choice in eval('choices_file.{}()'.format(category)):
            if isinstance(choice, list):
                choice = choice[0]
            choices[tuple([s.lower() for s in [dataset, iso, category, choice]])] = True
    return choices


def load_model_choices(datasets, languages):
    """
    Use the datasets file (assuming it found all the needed choices
    files) to locate all choices files and then extract their choices
    for a combined model level set of all choices.

    Args:
        datasets: loaded datasets
        languages: list of languages for the model

    Returns: dictionary of all gold standard choices for the model

    """
    gold = {}
    for language in languages:
        gold.update(load_choices(language[0], language[1], datasets[language[0]]["iso_list"][language[1]]["choices"]))
    return gold


def load_baseline4(dataset, iso):
    """
    Create baseline4 choices for a dataset and iso.

    Args:
        dataset: current dataset
        iso: current iso

    Returns: dictionary of choices

    """
    choices = {}
    for (category, choice) in INFER_BASELINE:
        choices[(dataset, iso, category, choice)] = True
    return choices


def load_model_baseline4(languages):
    """
    Load baseline4 choices for every language in a model.

    Args:
        languages: list of languages for the model

    Returns: dictionary of all baseline4 choices for the model

    """
    b4 = {}
    for language in languages:
        b4.update(load_baseline4(*language))
    return b4
