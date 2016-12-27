#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from map_gloss.utils.IOutils import find_path


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'eval/constants.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


CLASSIFICATION_TYPES = ['standard', 'misspelled', 'confused', 'incomplete', 'combined', 'user-identified',
                        'unrecovered', 'part-of-speech', 'lexical entry']
GOLD_STANDARD_FILE = '{}/eval/data/gold_standard.json'.format(find_path('map_gloss'))
LABELS = {'0': ('standard', 0),
          '1': ('misspelled', 1),
          '2': ('confused', 1),
          '3': ('incomplete', 2),
          '4': ('combined', 2),
          '5': ('user-identified', 3),
          '6': ('unrecovered', 3),
          '8': ('part-of-speech', 3),
          '9': ('lexical entry', 3)}
LABEL_TEXT = [('0', 'standard'),
              ('1', 'misspelled'),
              ('2', 'confused with another gloss'),
              ('3', 'a lexical entry that should be glossed'),
              ('4', 'a combination that should be divided'),
              ('5', 'author-defined and specific to the language\'s IGT'),
              ('6', 'an unrecoverable gloss'),
              ('8', 'a part-of-speech tag or other non-gram value'),
              ('9', 'a lexical entry')]
LEXICON_FILE = '{}/eval/data/lexicon.json'.format(find_path('map_gloss'))