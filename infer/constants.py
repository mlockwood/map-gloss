#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'infer/constants.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


INFER_BASELINE = {('tenses', 'past'): True,
                  ('tenses', 'future'): True,
                  ('tenses', 'present'): True,
                  ('aspects', 'perfective'): True,
                  ('aspects', 'imperfective'): True
                  }
RADIO = {'fut': 'future', 'future': 'future', 'past': 'past', 'pst': 'past', 'prs': 'present', 'present': 'present'}
