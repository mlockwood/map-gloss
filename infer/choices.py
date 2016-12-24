#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import re

# Import scripts
from src.gloss import errors as GlossErrors

# Import classes, functions, and variables
from map_gloss.gloss.standard import Gram
from map_gloss.infer.constants import RADIO


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'infer/choices.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def load_choices():
    """
    DEPRECATE THIS FUNCTION. IT IS REDUNDANT WITH THE DATASET LOADING
    REFRAME PROCESS SO THAT INFER IS AN OPTION DURING MODEL RUN
    """
    reader = open(data_path + '/choices', 'r')
    for row in reader:
        row = row.rstrip()

        # Handle special row types
        if not re.sub(' ', '', row):
            continue
        if row[0] == '#':
            continue
        elif row[0] == '@':
            cur_dataset = row[1:].lower()

        # Handle languages
        else:
            line = re.sub(' ', '', row.rstrip().lower()).split(',') # if this works replace load standards 4 lines

            # If no dataset is found raise MissingDatasetError
            if not cur_dataset:
                raise GlossErrors.MissingDatasetError('Language with ISO {} at path {} '.format(line[0], line[1]) +
                                                      'does not have an identified dataset.')

            # If dataset contains a variable path parse here
            match = re.search('\{\{\w*\}\}', line[1])
            if match:
                # If variable path identifier in var_paths
                var_path = re.sub('\{|\}', '', match.group())
                if var_path in var_paths:
                    line[1] = re.sub(match.group(), var_paths[var_path], line[1])

                # Else raise VariablePathError
                else:
                    raise GlossErrors.VariablePathError('{} was identified as a variable path '.format(var_path) +
                                                        'but no path was provided in gloss/constants.py.')

            # Add the language to the datasets DS
            if cur_dataset not in datasets:
                datasets[cur_dataset] = {}
            datasets[cur_dataset][line[0]] = line[1]

    return datasets


def make_choices(glosses, file):
    choices_text = ''
    categories = {}

    # Assign glosses to categories (MOM correction here)
    for gloss in glosses:
        try:
            if GRAMS[gloss][2] not in categories:
                categories[GRAMS[gloss][2]] = {}
            categories[GRAMS[gloss][2]][gloss] = True

        # There are some glosses that are not grams and should not be handled
        except:
            pass

    # Build section of the choices file
    choices_text += set_tense_aspect_mood(categories)

    # Export choices
    export_choices(file, choices_text)


def set_tense_aspect_mood(categories):
    tam_choices = 'section=tense-aspect-mood\ntense-definition=choose\n'

    # Build tense, aspect, and mood from categories
    tam = ['tense', 'aspect', 'mood']
    for category in tam:
        if category not in categories:
            continue

        # Create rules for TAM categories
        rule = 1
        for gloss in categories[category]:
            if gloss in RADIO:
                tam_choices += add_radio_choice(RADIO[gloss])
            else:
                tam_choices += add_choice(category, rule, gloss, category)
                rule += 1
    return tam_choices


def add_radio_choice(choice):
    return '{}=on\n'.format(choice.lower())


def add_radio_choice_subtype(rule, choice, supertype):
    return ' {}-subtype{}_name={}\n'.format(supertype.lower(), rule, choice)


def add_choice(category, rule, choice, supertype):
    return ' {0}{1}_name={2}\n  {0}{1}_supertype1_name={3}\n'.format(category, rule, choice, supertype)


def export_choices(file, choices_text):
    writer = open(file, 'w')
    writer.write(choices_text)
    writer.close()
    return True