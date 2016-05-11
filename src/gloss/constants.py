#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import re
import os


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'gloss/constants.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def find_path(directory, alt_base_directory=False):
    if not alt_base_directory:
        alt_base_directory = os.getcwd()
    match = re.search('/' + str(directory), alt_base_directory)
    if not match:
        raise IOError(str(directory) + ' is not in current working ' + 'directory')
    return os.getcwd()[:match.span()[0]] + '/' + directory


def load_standard_grams(data_path):
    grams = {}
    reader = open(data_path + '/standard_grams', 'r')
    for row in reader:
        if row[0] == '#':
            continue
        line = row.rstrip()
        line = line.lower()
        line = re.sub(' ', '', line)
        line = line.split(',')
        # Handle pseudo values
        L_pseudo = False
        G_pseudo = False
        if len(line) > 3:
            for value in line[3:]:
                if value == '!L' or value == '!l':
                    L_pseudo = True
                elif value == '!G' or value == '!g':
                    G_pseudo = True
        # Standard grams set of key = Leipzig or GOLD and value = [Leipzig, GOLD, categories, L-p, G-p]
        grams[line[0]] = line[0:3] + [L_pseudo, G_pseudo]
        grams[line[1]] = line[0:3] + [L_pseudo, G_pseudo]
    reader.close()
    return grams


def load_standard_values(data_path):
    values = {}
    reader = open(data_path + '/standard_values', 'r')
    for row in reader:
        if row[0] == '#':
            continue
        line = row.rstrip()
        line = line.lower()
        line = re.sub(' ', '', line)
        line = line.split(',')
        # Handle standard glosses
        grams = []
        if len(line) > 2:
            for value in line[2:]:
                grams.append(value)
        # Standard values set of key = value and value = [value, type, grams...]
        values[line[0]] = line
    reader.close()
    return values


PATH = find_path('map_gloss', os.path.realpath(__file__))
GRAMS = load_standard_grams(PATH + '/data')
VALUES = load_standard_values(PATH + '/data')
CTYPES = {'language': True, 'dataset': True, 'model': True}
EVAL = True