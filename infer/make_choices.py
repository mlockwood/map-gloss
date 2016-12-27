#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from infer.constants import RADIO


__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


def make_choices(categories, file):
    """
    Intake a set of choices organized by categories and produce a
    choices file that is compatible with the AGGREGATION project.

    Args:
        categories: dictionary of category keys to glosses
        file: output file for the choices file

    Returns: None

    """
    choices_text = ''

    # Build section(s) of the choices file
    choices_text += set_tense_aspect_mood(categories)

    # Export choices
    writer = open(file, 'w')
    writer.write(choices_text)
    writer.close()


def set_tense_aspect_mood(categories):
    """
    Set the tense-aspect-mood section of the choices file.

    Args:
        categories: dictionary of category keys to glosses

    Returns: text of test, aspect, and mood choices

    """
    tam_choices = 'section=tense-aspect-mood\ntense-definition=choose\n'

    # Build tense, aspect, and mood from categories
    tam = ['tenses', 'aspects', 'moods']
    for category in tam:
        if category not in categories:
            continue

        # Create rules for TAM categories
        rule = 1
        for gloss in categories[category]:
            if gloss in RADIO:
                tam_choices += add_radio_choice(RADIO[gloss])
            else:
                tam_choices += add_choice(category[:-1], rule, gloss, category[:-1])
                rule += 1
    return tam_choices


def add_radio_choice(choice):
    """
    Default string representation for radio button choices.

    Args:
        choice: value of the choice

    Returns: text of radio choice

    """
    return '{}=on\n'.format(choice.lower())


def add_radio_choice_subtype(rule, choice, supertype):
    """
    Default string representation for radio choice subtypes.

    Args:
        rule: the current rule number
        choice: choice itself
        supertype: category above the choice

    Returns: text of radio choice subtype

    """
    return ' {}-subtype{}_name={}\n'.format(supertype.lower(), rule, choice)


def add_choice(category, rule, choice, supertype):
    """
    Default string representation for choices.

    Args:
        category: category of choice
        rule: the current rule number
        choice: choice itself
        supertype: category above the choice

    Returns: text of choice

    """
    return ' {0}{1}_name={2}\n  {0}{1}_supertype1_name={3}\n'.format(category, rule, choice, supertype)
