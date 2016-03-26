#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = gold_standard.py
__author__ = MichaelLockwood
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Mapping Input Glosses to Standard Outputs
__date__ = September2015
__credits__ = None
__collaborators__ = None

This module assists the user with building GoldStandard IGT values for use in
map_gloss.py for baseline and evaluation purposes.
"""

import inspect
import re
import types

class CLSO:
    """Data format created by Michael Lockwood that stores files of
    classes and objects (hence the name CLS - class and O - ojbect).

    Note the following code option was tried in previous versions but
    was replaced:

    import ast
    ast.literal_eval() # Convert str to dict, tuple, list
    """

    objects = {}
    evaluation = ''

    def __init__(self, file, option='r'):
        self._file = open(str(file)+'.clso', option)
        CLSO.objects[file] = self

    def type_check(value):
        type_matches = []
        for method in dir(types):
            try:
                match = isinstance(value, eval('types.'+str(method)))
                if match:
                    type_matches.append(method)
            except:
                pass
        return type_matches

    def eval_list(L):
        S = '['
        L = L[1:-1]
        items = re.split(',', L)
        for item in items:
            item = re.sub(' ', '', item)
            if not item:
                continue
            if re.search('\'.*\'', item) or re.search('\".*\"', item):
                item = item[1:-1]
            if re.search('\[.*\]', item):
                S += CLSO.eval_list(L) + ','
            elif re.search('\'', item):
                item = re.sub('\'', '\\\'', item)
                S += '\'' + item + '\', '
            else:
                S += '\'' + item + '\', '
        if S[-2:] == ', ':
            S = S[:-2]
        S += ']'
        return S

    def str_list(L):
        return '\"' + CLSO.eval_list(L) + '\"'

    def load(self):
        clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        cls = ''
        values = {}
        for line in self._file:
            line = line.rstrip()
            # If blank, continue
            if not line:
                continue
            # If ID line set class to the value between the angle brackets
            if re.search('<[\w]*>', line):
                cls = line[1:-1]
            # If class variable process immediately
            elif line[0] == '$':
                exec(line[1:])
            # If value delimiter process the object and reset the value DS
            elif line == '@':
                for member in clsmembers:
                    if cls == member[0]:
                        # Add __init__ arguments
                        init_values = inspect.getargspec(eval(cls+'.__init__'))
                        init_code = cls + '('
                        for value in init_values.args[1:]:
                            if value in values:
                                if re.search('\[.*\]', values[value]):
                                    init_code += (CLSO.str_list(values[value])
                                                  + ', ')
                                elif re.search('\'', values[value]):
                                    init_code += '\"' + values[value] + '\", '
                                else:
                                    init_code += '\'' + values[value] + '\', '
                                del values[value]
                            elif ('_'+value) in values:
                                if re.search('\[.*\]', values['_'+value]):
                                    init_code += (CLSO.str_list(
                                                  values['_'+value]) + ', ')
                                elif re.search('\'', values['_'+value]):
                                    init_code += ('\"' + values['_'+value] +
                                                  '\", ')
                                else:
                                    init_code += ('\'' + values['_'+value] +
                                                  '\', ')
                                del values['_'+value]
                            else:
                                raise ValueError('Missing argument in CLSO ' +
                                                 'object from ' + str(cls) +
                                                 ': ' + str(value))
                        init_code += ')'
                        obj = eval(init_code)
                        # Add all other values
                        for value in values:
                            # If not a Built-In Function or Method
                            try:
                                exec('CLSO.evaluation='+str(values[value]))
                                match = CLSO.type_check(CLSO.evaluation)
                                # If a Built-In Function or Method
                                if (match or values[value] == 'help' or
                                    values[value] == 'obj'):
                                    # STRING OPTION
                                    exec('obj.'+str(value) + '=\''+
                                        str(values[value] + '\''))
                                # If not a Built-In Function or Method
                                else:
                                    # VAR OPTION
                                    exec('obj.'+str(value)+'=' +
                                         str(values[value]))
                            except:
                                try:
                                    # STRING OPTION
                                    exec('obj.'+str(value) + '=\''+
                                         str(values[value] + '\''))
                                    
                                except:
                                    # TUPLE OPTION
                                    exec('obj.'+str(value) + '=\"'+
                                         str(values[value] + '\"'))
                values = {}
            # If close line process the object and reset the cls DS
            elif re.search('</[\w]*\>', line):
                cls = ''
            # If it is a value, process as value
            else:
                line = line.split('=')
                values[line[0]] = line[1]
        return True

    def _dump_helper(self, obj, cls_variables):
        methods = {}
        temp = inspect.getmembers(obj, inspect.ismethod)
        for method in temp:
            methods[method[0]] = True
        for value in dir(obj):
            if not re.search('__[\w]*__', value):
                if value not in methods and value not in cls_variables:
                    self._file.write(value + '=' + str(eval('obj.' + value))
                                     + '\n')
        self._file.write('@\n')
        return True

    def dump(self, obj):
        cls = str(obj.__class__)[17:-2]
        if cls[0] == '.':
            cls = cls[1:]
        cls_variables = []
        for value in dir(eval(cls)):
            if not re.search('__[\w]*__', value):
                cls_variables.append(value)
        self._file.write('<' + cls + '>\n')
        self._dump_helper(obj, cls_variables)
        self._file.write('</' + cls + '>\n\n')
        return True

    def bulk_dump(self, cls):
        self._file.write('<' + cls + '>\n')
        cls_variables = []
        for value in dir(eval(cls)):
            if not re.search('__[\w]*__', value):
                cls_variables.append(value)
        cls_functions = {}
        for func in inspect.getmembers(eval(cls), inspect.isfunction):
            cls_functions[func[0]] = True
        for var in cls_variables:
            if var != 'objects' and var not in cls_functions:
                self._file.write('$' + cls + '.' + str(var) + '=' + str(
                                 eval(cls +'.' + str(var))) + '\n')
        for obj in eval(str(cls) + '.objects'):
            if isinstance(obj, tuple):
                self._dump_helper(eval(str(cls) + '.objects[' + str(obj) +
                                       ']'), cls_variables)
            elif isinstance(obj, str):
                self._dump_helper(eval(str(cls) + '.objects[\'' + str(obj) +
                                       '\']'), cls_variables)
            else:
                raise TypeError('Object must be string or tuple.')
        self._file.write('</' + cls + '>\n\n')
        self._file.close()

    def close(self):
        self._file.close()

"""
Import packages and scripts---------------------------------------------
"""
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
from src.utils import functions

"""
GoldStandard class------------------------------------------------------
"""
class GS:
    
    objects = {} #(dataset, iso, gloss)
    languages = {}
    glosses = {}
    lexicon = {}
    values = {}
    nstd_types = ['standard', 'misspelled', 'confused', 'incomplete',
                  'combined', 'user-identified', 'unrecovered',
                  'part-of-speech', 'word']

    def __init__(self, dataset, iso, gloss):
        self._dataset = dataset
        self._iso = iso
        self._gloss = gloss
        self._observed = 1
        self._standard = ''
        self._error_type = ''
        GS.objects[(dataset, iso, gloss)] = self

    def load():
        """Load the GoldStandard CLSO file.
        """
        try:
            reader = CLSO('gold_standard', option='r')
            reader.load()
            return True
        except:
            print('Error loading gold_standard.clso')
            GS.objects = {}
            return False

    def export():
        """Export the GoldStandard CLSO file.
        """
        writer = CLSO('gold_standard', option='w')
        writer.bulk_dump('GS')
        return True

    def set_lexicon():
        for obj in GS.objects:
            if GS.objects[obj]._error_type == 'word':
                GS.lexicon[GS.objects[obj]._gloss] = True

    def seek_input():
        """Seek user input on gold standard values.
        """
        print('For each gloss please first enter:\n' +
                  '\t0) If it is standard\n' +
                  '\t1) If it is misspelled\n' +
                  '\t2) If it is confused with another gloss\n' +
                  '\t3) If it is a concept that needs to be glossed\n' +
                  '\t4) If it is a combination that should be divided\n' +
                  '\t5) If it is identified only by the user\n' +
                  '\t6) If it is an unrecoverable data entry error\n' +
                  '\t8) If it is a part-of-speech tag and not a word\n' +
                  '\t9) If it is a word and not a gloss\n')
        collection_name = ''
        iso = ''
        for gloss in sorted(GS.objects.keys()):
            if GS.objects[gloss]._standard:
                continue
            # Preconditioned Acceptance
            valid = True
            # If a standard gloss
            if gloss[2] in GS.glosses:
                GS.set_standard(gloss, 'standard', gloss[2])
            # If a known word
            elif gloss[2] in GS.lexicon:
                GS.set_standard(gloss, 'word', 'word')
            # If a known incomplete value
            elif gloss[2] in GS.values:
                GS.set_standard(gloss, 'incomplete', GS.values[gloss[2]])
            # Otherwise seek standard
            else:
                valid = False
                if collection_name != gloss[0]:
                    print('Dataset: ' + str(gloss[0]))
                    collection_name = gloss[0]
                if iso != gloss[1]:
                    print('Language: ' + str(gloss[1]))
                    iso = gloss[1]
            # Seek standard
            while not valid:
                error = input('\t' + gloss[2] + ': ')
                valid = True
                if str(error) == '0':
                    GS.set_standard(gloss, 'standard', gloss[2])
                elif str(error) == '1':
                    GS.set_standard(gloss, 'misspelled',
                        GS.seek_standard(gloss[2]))
                elif str(error) == '2':
                    GS.set_standard(gloss, 'confused',
                        GS.seek_standard(gloss[2]))
                elif str(error) == '3':
                    GS.set_standard(gloss, 'incomplete',
                        GS.seek_standard(gloss[2], repeat=True))
                elif str(error) == '4':
                    GS.set_standard(gloss, 'combined',
                        GS.seek_standard(gloss[2], repeat=True))
                elif str(error) == '5':
                    GS.set_standard(gloss, 'user-identified',
                                    'user-identified')
                elif str(error) == '6':
                    GS.set_standard(gloss, 'unrecovered', 'unrecovered')
                elif str(error) == '8':
                    GS.set_standard(gloss, 'part-of-speech', 'part-of-speech')
                elif str(error) == '9':
                    GS.set_standard(gloss, 'word', 'word')
                    GS.lexicon[gloss[2]] = True
                else:
                    print('\t\tYou have entered an unrecognized value, try' +
                          ' again.')
                    valid = False
                print()
        return True

    def set_standard(gloss, error_type, standard):
        GS.objects[gloss]._error_type = error_type
        if error_type == 'incomplete' or error_type == 'combined':
            GS.objects[gloss]._standard = error_type
            GS.objects[gloss]._gold_values = standard
        else:
            GS.objects[gloss]._standard = standard
        return True

    def seek_standard(gloss, repeat=False):
        """Ask the user to enter the standard value for the gloss.
        """
        if repeat == True:
            s_list = []
            standard = ''
            while str(standard) != '0':
                standard = input('\tWhat is one of the glosses for ' +
                                 str(gloss) + ' (use 0 if no more values): ')
                if str(standard) != '0' and standard != '':
                    s_list.append(standard.lower())
            standard = s_list
        else:
            standard = input('\tWhat is the correct value for ' + str(gloss) +
                             ': ')
        return standard

    def _run_statistics():
        """Report errors to the langauges DS for reporting.
        """
        GS.languages = {'<all>': {'<all>' : {}}}
        for gloss in GS.objects:
            if gloss[0] not in GS.languages:
                GS.languages[gloss[0]]  = {'Aggregate': {}}
            if gloss[1] not in GS.languages[gloss[0]]:
                GS.languages[gloss[0]][gloss[1]] = {}
            code = GS.objects[gloss]._error_type
            GS.languages[gloss[0]][gloss[1]][code] = (
                GS.languages[gloss[0]][gloss[1]].get(code, 0) + 1)
            GS.languages[gloss[0]]['Aggregate'][code] = (
                GS.languages[gloss[0]]['Aggregate'].get(code, 0) + 1)
            GS.languages['<all>']['<all>'][code] = GS.languages['<all>'][
                '<all>'].get(code, 0) + 1
        return True

    def _write_statistic(writer, dataset, error_name):
        return ('writer.write(\'\t{0:12} {1:4} & {2:.4f}\\n\'.format(\'' +
                str(error_name).title() + '\' + \':\' , GS.languages[\'' +
                str(dataset) + '\'][iso][\'' + str(error_name) + '\'], err[\''
                + str(error_name) + '\']))')

    def report():
        """Report all of the GS statistics to file.
        """
        GS._run_statistics()
        for dataset in GS.languages:
            if dataset != '<all>':
                writer = open('gold_standard/gold_standard_' + str(dataset),
                              'w')
                iso_map = {}
                for iso in GS.languages[dataset]:
                    iso_map[iso] = True
                del iso_map['Aggregate']
                iso_list = ['Aggregate'] + sorted(iso_map.keys())
            else:
                writer = open('gold_standard/gold_standard_total', 'w')
                iso_list = ['<all>']

            writer.write('Gold Standard Statistics for: ' + str(dataset) +
                         '\n\n')
            for iso in iso_list:
                total = 0.0
                for error in GS.languages[dataset][iso]:
                    total += GS.languages[dataset][iso][error]
                err = {}
                for error in GS.languages[dataset][iso]:
                    err[error] = GS.languages[dataset][iso][error] / total
                writer.write(str(iso) + ' Statistics:\n')
                for nstd in GS.nstd_types:
                    if nstd in GS.languages[dataset][iso]:
                        exec(GS._write_statistic(writer, dataset, nstd))
                writer.write('\n')
            writer.close()
        return True

    def delete_gold_standard(dataset, iso, gloss):
        """Delete a gold standard value.

        Keyword arguments:
          dataset -- the name of the dataset
          iso -- the iso value of the language
          gloss -- the value of the gold standard gloss
        """
        del GS.objects[(dataset, iso, gloss)]
        return True
        
    def add_observation(self):
        """Add an entry to the observation set for the dataset,
        iso_code, and gloss.
        """
        # Increment occurrence count for the gloss
        self._observed += 1
        return True

    def unigram_baseline(train, test):
        model = {}
        test_obj = []
        test_acc = {'pos': 0, 'neg': 0}
        for obj in GS.objects:
            if obj[0] in train:
                if GS.objects[obj]._gloss not in model:
                    model[GS.objects[obj]._gloss] = {}
                model[GS.objects[obj]._gloss][GS.objects[obj]._standard] = (
                    model[GS.objects[obj]._gloss].get(
                    GS.objects[obj]._standard, 0) + GS.objects[obj]._observed)
            elif obj[0] in test:
                test_obj.append(GS.objects[obj])
        for obj in test_obj:
            # Known glosses
            if obj._gloss in model:
                if functions.max_inD(model[obj._gloss])[0] == obj._standard:
                    test_acc['pos'] = test_acc.get('pos', 0) + 1
                else:
                    test_acc['neg'] = test_acc.get('neg', 0) + 1
            # Unknown glosses
            # Gloss in standard set
            elif obj._gloss in GS.glosses:
                if obj._gloss == obj._standard:
                    test_acc['pos'] = test_acc.get('pos', 0) + 1
                else:
                    test_acc['neg'] = test_acc.get('neg', 0) + 1
            # Otherwise assume it is a word
            else:
                if obj._standard == 'word':
                    test_acc['pos'] = test_acc.get('pos', 0) + 1
                else:
                    test_acc['neg'] = test_acc.get('neg', 0) + 1
        acc = functions.probD_conversion(test_acc)
        return acc

GS.load_standard_glosses()
GS.set_lexicon()
GS.load_standard_values()

if __name__ == '__main__':
    GS.load()
    print(GS.unigram_baseline({'dev1': True, 'dev2': True}, {'test': True}))
    # GS.report()

