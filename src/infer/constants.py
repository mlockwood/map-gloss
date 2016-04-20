__author__ = 'Michael Lockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


import os
import re
import src.gloss.errors as GlossErrors


def find_path(directory):
    match = re.search('/' + str(directory), os.getcwd())
    if not match:
        raise IOError(str(directory) + 'is not in current working ' + 'directory')
    return os.getcwd()[:match.span()[0]] + '/' + directory


def load_choices(data_path, var_paths= {}):
    # {dataset: {iso: choices_path}}
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


def load_model(data_path):
    models = []
    reader = open(data_path + '/models', 'r')
    for row in reader:
        models.append(re.split(',', row.rstrip()))  # [model_id, train collection, test collection, classifiers]
    return models


PATH = find_path('map_gloss')
AGG_PATH = find_path('aggregation')
DEV1_PATH = AGG_PATH + '/data/567/dev1'
DEV2_PATH = AGG_PATH + '/data/567/dev2'
TEST_PATH = AGG_PATH + '/data/567/test'

RADIO = {'fut': 'future', 'future': 'future', 'past': 'past', 'pst': 'past', 'prs': 'present', 'present': 'present'}
CHOICES = load_choices(PATH + '/data', {'agg': AGG_PATH, 'dev1': DEV1_PATH, 'dev2': DEV2_PATH, 'test': TEST_PATH})
CTYPES = {'language': True, 'dataset': True, 'model': True}
FTYPES = {'gold': True, 'baseline5': True, 'final': True}
