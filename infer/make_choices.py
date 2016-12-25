#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from map_gloss.infer.constants import RADIO


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'infer/make_choices.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def make_choices(categories, file):
    choices_text = ''

    # Build section(s) of the choices file
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