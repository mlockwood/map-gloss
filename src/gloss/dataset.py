#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import re

# Import scripts
from src.gloss import errors as GlossErrors


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'dataset.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def load_datasets(data_path, var_paths={}):
    # {dataset: {iso: xigt_path}}
    datasets = {}
    cur_dataset = ''
    reader = open(data_path + '/datasets', 'r')
    for row in reader:
        row = row.rstrip()

        # Handle special row types
        if not re.sub(' ', '', row):
            continue
        if row[0] == '#':
            continue
        elif row[0] == '@':
            cur_dataset = row[1:]

        # Handle languages
        else:
            line = re.sub(' ', '', row.rstrip().lower()).split(',') # if this works replace load standards 4 lines

            # If no dataset is found raise MissingDatasetError
            if not cur_dataset:
                raise GlossErrors.MissingDatasetError('Language with ISO {} at path {}'.format(line[0], line[1]) +
                                                         ' does not have an identified dataset.')

            # If dataset contains a variable path parse here
            match = re.search('\{\{\w*\}\}', line[1])
            if match:
                # If variable path identifier in var_paths
                var_path = re.sub('\{|\}', '', match.group())
                if var_path in var_paths:
                    line[1] = re.sub(match.group(), var_paths[var_path], line[1])

                # Else raise VariablePathError
                else:
                    raise GlossErrors.VariablePathError('{} was identified as a variable path'.format(var_path) +
                                                           ' but no path was provided in gloss/constants.py.')

            # Add the language to the datasets DS
            if cur_dataset not in datasets:
                datasets[cur_dataset] = {}
            datasets[cur_dataset][line[0]] = line[1]

    return datasets