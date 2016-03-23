#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = evaluation.py
__author__ = MichaelLockwood
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Mapping Input Glosses to Standard Outputs
__date__ = October2015
__credits__ = None
__collaborators__ = None

This module performs the evaluation procedures for map_gloss and the inference
scripts which utilize map_gloss.
"""

"""
Import packages and scripts---------------------------------------------
"""
import math
import re
import os
import sys

class PathSetter:

    def set_pythonpath(directory='', subdirectory=''):
        if directory:
            directory = PathSetter.find_path(directory)
            if subdirectory:
                if directory[-1] != '/' and subdirectory[0] != '/':
                    directory += '/'
                directory += subdirectory
        else:
            directory = os.getcwd()
        sys.path.append(directory)
        return True

    def find_path(directory):
        match = re.search('/' + str(directory), os.getcwd())
        if not match:
            raise IOError(str(directory) + 'is not in current working ' +
                          'directory')
        return os.getcwd()[:match.span()[0]] + '/' + directory

# Add aggregation and map_gloss to PYTHONPATH
PathSetter.set_pythonpath('aggregation')
PathSetter.set_pythonpath('map_gloss')
# Import scripts
import confusion_matrix
import functions

"""
MapGloss evaluation-----------------------------------------------------
"""
class MapGloss:

    objects = {}
    datasets = {}
    languages = {}
    error_types = {'incomplete': True, 'combined': True,
                   'user-identified': True, 'unrecovered': True,
                   'part-of-speech': True, 'word' : True}

    def __init__(self, dataset, iso, gloss, classification, standard, final):
        self._dataset = dataset
        self._iso = iso
        self._gloss = gloss
        self._classification = classification
        self._standard = standard
        self._final = final
        MapGloss.objects[(dataset, iso, gloss)] = self
        if dataset not in MapGloss.datasets:
            MapGloss.datasets[dataset] = {}
        MapGloss.datasets[dataset][(iso, gloss)] = self
        if iso not in MapGloss.languages:
            MapGloss.languages[iso] = {}
        MapGloss.languages[iso][(dataset, gloss)] = self

    # Main evaluation wrapper function
    def evaluate_all():
        for dataset in MapGloss.datasets:
            MapGloss.evaluate(MapGloss.datasets[dataset], dataset)
        for iso in MapGloss.languages:
            MapGloss.evaluate(MapGloss.languages[iso], iso)
        return True
    
    # Main evaluation function
    def evaluate(objects, collection):
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/map_gloss'):
            os.mkdir(os.getcwd() + '/evaluation/map_gloss')
        writer = open('evaluation/map_gloss/' + str(collection) +
                      '_results.eval', 'w')
        correct = 0
        i_vectors = []
        c_vectors = []
        acc = {'standard': {}, 'non-standard': {}}
        for obj in objects:
            uv_obj = objects[obj]
            # Determine final classification output
            if uv_obj._final not in MapGloss.error_types:
                if str(uv_obj._final) == str(uv_obj._standard):
                    final = 'standard'
                else:
                    final = 'non-standard'
            else:
                final = uv_obj._final
            # Populate accuracy DS
            if uv_obj._classification not in acc:
                acc[uv_obj._classification] = {}
            acc[uv_obj._classification][final] = acc[uv_obj._classification
                                                     ].get(final, 0) + 1
            # Set direct evaluation values
            if str(uv_obj._final) == str(uv_obj._standard):
                correct += 1
                c_vectors.append([uv_obj._standard, uv_obj._gloss,
                                  uv_obj._final])
            else:
                i_vectors.append([uv_obj._standard, uv_obj._gloss,
                                  uv_obj._final])
        # Write results to file
        writer.write('Accuracy: ' +
                     str(correct/float(len(MapGloss.objects))) + '\n')
        writer.write('Total: ' + str(len(MapGloss.objects)) +
                     '; Correct: ' + str(correct) + '\n\n')
        writer.write('Incorrect pairs\n')
        for gloss in i_vectors:
            writer.write(('Standard: {0:20s}\tObserved: {1:20s}\tIncorrect: ' +
                         '{2:20s}\n').format(str(gloss[0]), str(gloss[1]),
                                             str(gloss[2])))
        writer.write('\nCorrect pairs\n')
        for gloss in c_vectors:
            writer.write(('Standard: {0:20s}\tObserved: {1:20s}\tCorrect: ' +
                         '{2:20s}\n').format(str(gloss[0]), str(gloss[1]),
                                             str(gloss[2])))
        # Write accuracy
        file = 'evaluation/map_gloss/' + str(collection)
        functions.accuracy(acc, file)
        return True
