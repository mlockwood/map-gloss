__author__ = 'Michael Lockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


import os
import re

import src.gloss.errors as MapGlossErrors

load_gold_standard = True
knn = False
maxent = False
nb = False
tbl = True
model_id = 0x1


def find_path(directory):
    match = re.search('/' + str(directory), os.getcwd())
    if not match:
        raise IOError(str(directory) + 'is not in current working ' + 'directory')
    return os.getcwd()[:match.span()[0]] + '/' + directory


def load_standard_grams(data_path):
    grams = {}
    reader = open(data_path + '/standard_glosses', 'r')
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


def load_datasets(data_path, var_paths= {}):
    # Train and test will be {dataset: {iso: xigt_path}}
    train = {}
    test = {}
    train_marker = False
    test_marker = False
    cur_dataset = ''
    reader = open(data_path + '/datasets', 'r')
    for row in reader:
        row = row.rstrip()

        # Handle special row types
        if not re.sub(' ', '', row):
            continue
        if row[0] == '#':
            continue
        elif row == '=TRAIN':
            train_marker = True
            test_marker = False
            cur_dataset = ''
        elif row == '=TEST':
            test_marker = True
            train_marker = False
            cur_dataset = ''
        elif row[0] == '@':
            cur_dataset = row[1:]

        # Handle languages
        else:
            line = re.sub(' ', '', row.rstrip().lower()).split(',') # if this works replace load standards 4 lines

            # If no dataset is found raise MissingDatasetError
            if not cur_dataset:
                raise MapGlossErrors.MissingDatasetError('Language with ISO {} at path {}'.format(line[0], line[1]) +
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
                    raise MapGlossErrors.VariablePathError('{} was identified as a variable path'.format(var_path) +
                                                           ' but no path was provided in gloss/constants.py.')

            # If train
            if train_marker:
                if cur_dataset not in train:
                    train[cur_dataset] = {}
                train[cur_dataset][line[0]] = line[1]

            # If test
            elif test_marker:
                if cur_dataset not in test:
                    test[cur_dataset] = {}
                test[cur_dataset][line[0]] = line[1]

            # If neither train or test exists raise TrainTestUnspecifiedError
            else:
                raise MapGlossErrors.TrainTestUnspecifiedError('Langauges were defined before train and test sets.')
    return train, test


agg_path = find_path('map_gloss') # CHANGE TO aggregation in production-------------------------------------------------
data_path = find_path('map_gloss') + '/data'

grams = load_standard_grams(data_path)
values = load_standard_values(data_path)
train, test = load_datasets(data_path, {'agg_path': agg_path})