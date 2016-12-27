#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


INFER_BASELINE = {('tenses', 'past'): True,
                  ('tenses', 'future'): True,
                  ('tenses', 'present'): True,
                  ('aspects', 'perfective'): True,
                  ('aspects', 'imperfective'): True
                  }
RADIO = {'fut': 'future', 'future': 'future', 'past': 'past', 'pst': 'past', 'prs': 'present', 'present': 'present'}
