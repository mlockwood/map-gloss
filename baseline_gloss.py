#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = baseline_gloss.py
__author__ = MichaelLockwood
__projectclass__ = LING575
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Infer Tense, Aspect, and Mood
__date__ = August2015
__credits__ = None
__collaborators__ = None

This module loads enriched XIGT data and connects with map_gloss to allow the
user to build a baseline of the errors present in the available IGT data.
"""

import map_gloss
import os
import sys
import xigt.ref

from xigt.codecs import xigtxml


def load_data(collection, name):
    # Set path to the root of the AGGREGATION folder
    agg_path = os.path.abspath(os.path.join(os.path.abspath(os.path.join(
               os.getcwd(), os.pardir)), os.pardir))
    # Initialize and prepare objects for map_gloss.py
    data = []
    for dataset in collection:
        if datasets[dataset][-1] == '/':
            xigt_path = (agg_path + datasets[dataset] +
                         'testsuite-enriched.xml')
        else:
            xigt_path = (agg_path + '/' + datasets[dataset] +
                               '/testsuite-enriched.xml')
        data.append((name, dataset, xigt_path))
    # Process XIGT files with map_gloss.py
    map_gloss.Baseline.main(data, name)
    return True
        
"""
User Interface Functions------------------------------------------------
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

load_data(dev1, 'dev1')

load_data(dev2, 'dev2')

#load_data(test, 'test')
