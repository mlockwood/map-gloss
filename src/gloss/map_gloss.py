#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = map_gloss.py
__author__ = MichaelLockwood
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Mapping Input Glosses to Standard Outputs
__date__ = May2015
__credits__ = None
__collaborators__ = None

This module allows a user to map a set of input glosses from an interlinear
gloss text source to a condensed output that attempts to correct mistakes and
merge redundant glosses. The main glossing function calls the correct MapGloss
class functions for the user and manages that process. For more control a user
may consult the Map_Gloss_Tutorial.pdf which explains each function and how to
command greater control of the system.
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
import copy
import os
import string
import sys


# Import scripts
from src.eval import confusion_matrix, evaluation, gold_standard
from src.utils import functions, machine_learning

"""
MapGloss----------------------------------------------------------------
"""
class MapGloss:

    """The MapGloss class manages the process of mapping input glosses
    to intermediate and/or final compliant glosses. Objects are
    individual input glosses that must have a language iso value.
    """
    cross_valid = {}
    standard = {}
    
    """
    Main processing functions-------------------------------------------
    """
    def process(train, test):
        # Define collections
        collections = train + test
        # Load data for all datasets in the collections
        MapGloss.auto_load(collections)
        # Prepare training and test sets
        training_vectors = MapGloss.vectorize(train)
        testing_vectors = MapGloss.vectorize(test)
        # Train model
        model_obj = machine_learning.Model(training_vectors,
                                           run_kNN = MapGloss.knn,
                                           run_MaxEnt = MapGloss.maxent,
                                           run_NB = MapGloss.nb,
                                           run_TBL = MapGloss.tbl)
        model_obj.train()
        MapGloss.export_configuration(model_obj._ID)
        # Test models
        model_obj.test_models(training_vectors, 'train')
        model_obj.test_models(testing_vectors, 'test')
        # Set learning results from last test model
        MapGloss.set_model_results(model_obj._results)
        MapGloss.evaluate_map_gloss_results()
        # Write comparison p/r/f evaluation files
        MapGloss.process_cprf_files()
        MapGloss.export()
        return Language.get_language_glosses()

    def produce(test):
        # Set configuration variables
        MapGloss.load_configuration()
        # Load date for all datasets in the collection
        MapGloss.auto_load(test)
        # Prepare testing vectors
        testing_vectors = MapGloss.vectorize(test)
        # Load model
        machine_learning.Model.load()
        model_obj = machine_learning.Model.objects[
            sorted(machine_learning.Model.objects.keys())[-1]]
        if hasattr(MapGloss, 'model_ID'):
            if MapGloss.model_ID in machine_learning.Model.objects:
                model_obj = machine_learning.Model.objects[MapGloss.model_ID]
        # Run models
        model_obj.test_models(testing_vectors, 'test')
        # Collect results
        MapGloss.set_model_results(model_obj._results)
        return Language.get_language_glosses()

    def cross_validation(collections, label):
        # Set configuration variables
        MapGloss.load_configuration()
        # Load data for all datasets in the collections
        MapGloss.auto_load(collections)
        languages = {}
        for dataset in collections:
            for iso in dataset[0]:
                languages[(dataset[1], iso)] = True
        for iso in languages:
            train = copy.deepcopy(languages)
            del train[iso]
            test = {iso: True}
            # Prepare training and test sets
            training_vectors = MapGloss.vectorize(train, collect=True)
            testing_vectors = MapGloss.vectorize(test, collect=True)
            # Train model
            model_obj = machine_learning.Model(training_vectors,
                                               run_kNN = MapGloss.knn,
                                               run_MaxEnt = MapGloss.maxent,
                                               run_NB = MapGloss.nb,
                                               run_TBL = MapGloss.tbl)
            model_obj.train()
            # Test models
            model_obj.test_models(training_vectors, 'train')
            model_obj.test_models(testing_vectors, 'test')
            # Set learning results from last test model
            MapGloss.set_cross_valid(model_obj._results, iso, label)
        return True

    """
    Data Processing Functions-------------------------------------------
    """
    def auto_load(collections):
        MapGloss.load_standard_glosses()
        MapGloss.load_standard_values()
        collection = MapGloss.prepare_data(collections)
        MapGloss.add_data(collection)
        gold_standard.GS.load()
        MapGloss.gold_standard_to_vector()


            
    def load():
        """Load a CLSO file containing all DS.
        """
        gold_standard.GS.load()
        machine_learning.Model.load()
        return True

    def export():
        """Export CLSO files for map_gloss values that should be reloaded.
        """
        gold_standard.GS.export()
        return True

    @staticmethod
    def add_data(collection):
        """Function for the user to call to process a set(s) of glosses.
        Ensures that /src/xigt is in the PYTHONPATH.

        Keyword arguments:
          collection -- the list of xigt files organized into tuples as
                        following:
                        [(collection_name, iso_code, xigt_file), ... ]
        """


        # Process and convert data
        out_data = []
        for dataset in collection:
            for iso in collection[dataset]:
                # Open the current xigt file
                file = open(collection[dataset][iso])
                xc = xigtxml.load(file)
                file.close()
                punctex = re.compile('[%s]' % string.punctuation)
                # Train each IGT sentence
                for igt in xc:

                    # Capture the morphemes
                    morphemes = {}
                    for morpheme in igt.get('m'):
                        morphemes[morpheme.id] = morpheme.value()

                    # Determine which glosses share a morpheme
                    shared_morphemes = {}
                    for gloss in igt.get('g'):
                        try:
                            if morphemes[gloss.alignment] not in shared_morphemes:
                                shared_morphemes[morphemes[gloss.alignment]] = []
                            shared_morphemes[morphemes[gloss.alignment]] = (shared_morphemes.get(
                                morphemes[gloss.alignment], 0) + [re.sub(' ', '', str(gloss.value()).lower())])
                        except:
                            pass

                    # Capture the translated words
                    words = {}
                    for line in igt.get('t'):
                        line = str(line.value()).lower()
                        line = line.split()
                        for word in line:
                            words[word] = True

                    # Create a vector for each gloss instance
                    for gloss in igt.get('g'):
                        gloss = re.sub(punctex, '', str(gloss.value()))
                        if gloss:
                            word_match = False
                            if gloss.lower() in words:
                                word_match = True
                            try:
                                Vector(dataset, iso, gloss, shared_morphemes[morphemes[gloss.alignment]], word_match)
                            except:
                                Vector(dataset, iso, gloss, '', word_match)
            return True

    def gold_standard_to_vector():
        refresh = []
        # Process every vector
        for vector in Vector.objects:
            # If GoldStandard object does not exist, create GoldStandard object
            if ((vector[0], vector[1], vector[2]) not in
                gold_standard.GS.objects):
                refresh.append(vector)
                gold_standard.GS(vector[0], vector[1], vector[2])
            #If GoldStandard standard does not exist, add observation
            elif not gold_standard.GS.objects[(vector[0], vector[1], vector[2])
                                          ]._standard:
                gold_standard.GS.objects[(vector[0], vector[1], vector[2])
                                         ].add_observation()
            # If GoldStandard has a standard send to Vector
            else:
                Vector.objects[vector]._standard = str(
                    gold_standard.GS.objects[(vector[0], vector[1],
                                              vector[2])]._standard)
        # If there were values that needed a GoldStandard standard
        if refresh:
            # Seek input and then send to Vector
            gold_standard.GS.seek_input()
            for vector in refresh:
                Vector.objects[vector]._standard = gold_standard.GS.objects[(
                    vector[0], vector[1], vector[2])]._standard
        return True

    """
    Vector Processing Functions-----------------------------------------
    """
    def vectorize(datasets, collect=False):
        if collect == False:
            collection = {} # collection = {('dev1', iso): True}
            for dataset in datasets:
                for iso in dataset[0]:
                    collection[(dataset[1], iso)] = True
        else:
            collection = datasets
        # Select the vectors that match the (dataset, iso) of the collection
        vectors = []
        for vector in Vector.objects:
            if (vector[0], vector[1]) in collection:
                vectors.append(Vector.objects[vector])
        return vectors

    def set_cross_valid(results, iso, label):
        # iso must be (dataset, iso)
        UniqueVector.objects = {}
        for gloss in results:
            uv_obj = UniqueVector(gloss[0], gloss[1], gloss[2])
            uv_obj._results = copy.deepcopy(results[gloss])
            uv_obj.set_final()
            uv_obj.set_classification()
            uv_obj.set_standard()
        obj = Language.objects[iso]
        if iso not in MapGloss.cross_valid:
            MapGloss.cross_valid[iso] = {}
        baseline = confusion_matrix.CM(obj._std_glosses, obj._obs_glosses,
                                       iso[1] + '_baseline')
        MapGloss.cross_valid[iso]['<baseline>'] = baseline
        final = confusion_matrix.CM(obj._std_glosses, obj._final_glosses,
                                    iso[1] + '_' + str(label))
        MapGloss.cross_valid[iso]['<' + str(label) + '>'] = final
        return True

    def write_cross_validation():
        writer = open('evaluation/cross_validation.eval', 'w')
        for iso in sorted(MapGloss.cross_valid.keys()):
            line = str(iso[0]) + ' & ' + str(iso[1])
            for method in sorted(MapGloss.cross_valid[iso].keys()):
                line += ' & {0:.4f} & {1:.4f} & {2:.4f}'.format(
                    MapGloss.cross_valid[iso][method]._precision,
                    MapGloss.cross_valid[iso][method]._recall,
                    MapGloss.cross_valid[iso][method]._fscore)
            line += '\\\\\n'
            writer.write(line)
        writer.close()
        return True
    
    def set_model_results(results):
        for gloss in results:
            uv_obj = UniqueVector(gloss[0], gloss[1], gloss[2])
            uv_obj._results = copy.deepcopy(results[gloss])
            uv_obj.set_final()
        return True

    def evaluate_map_gloss_results():
        # Send UniqueVector objects to the evaluation for MapGloss
        for obj in UniqueVector.objects:
            uv_obj = UniqueVector.objects[obj]
            uv_obj.set_classification()
            uv_obj.set_standard()
            evaluation.MapGloss(uv_obj._dataset, uv_obj._iso, uv_obj._gloss,
                                uv_obj._classification, uv_obj._standard,
                                uv_obj._final)
        evaluation.MapGloss.evaluate_all()
        return True

    def process_cprf_files():
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/cprf'):
            os.mkdir(os.getcwd() + '/evaluation/cprf')
        if not os.path.exists(os.getcwd() + '/evaluation/hprf'):
            os.mkdir(os.getcwd() + '/evaluation/hprf')
        # Dataset level cprf files
        for dataset in Language.std_glosses:
            confusion_matrix.CM(Language.std_glosses[dataset],
                                Language.obs_glosses[dataset], dataset + '_baseline')
            confusion_matrix.CM(Language.std_glosses[dataset],
                                Language.final_glosses[dataset], dataset + '_final')
            c_obj = confusion_matrix.Compare(dataset + '_final',
                                             dataset + '_baseline')
            c_obj.write_cprf_file('evaluation/cprf/'+str(dataset))
        # ISO level cprf files
        for iso in Language.objects:
            obj = Language.objects[iso]
            baseline = confusion_matrix.CM(obj._std_glosses, obj._obs_glosses,
                                           iso[1] + '_baseline')
            baseline.write_hprf_file('evaluation/hprf/'+str(iso[1])+
                                     '_baseline')
            final = confusion_matrix.CM(obj._std_glosses, obj._final_glosses,
                                        iso[1] + '_final')
            final.write_hprf_file('evaluation/hprf/'+str(iso[1])+'_final')
            c_obj = confusion_matrix.Compare(iso[1] + '_final',
                                             iso[1] + '_baseline')
            c_obj.write_cprf_file('evaluation/cprf/'+str(iso[1]))

    """
    General processing functions----------------------------------------
    """
    def get_distances(gloss):
        distances = {}
        for obj in StandardGloss.objects:
            distances[obj] = functions.levenshtein(gloss, obj)
        return distances

"""
Data Storage and Handling Classes---------------------------------------
"""
class Vector:

    objects = {} #(dataset, iso, gloss, ID)
    datasets = {} #(dataset, iso)
    ID_generator = 1

    def __init__(self, dataset, iso, gloss, morphemes, word_match):
        self._dataset = dataset
        self._iso = iso
        self._raw_gloss = gloss
        self._gloss = str(gloss.lower())
        self._ID = hex(Vector.ID_generator)
        Vector.ID_generator += 1
        self._morphemes = morphemes
        self._word_match = word_match
        self._segments = {}
        self.set_segmentation()
        self._distances = MapGloss.get_distances(str(gloss.lower()))
        self._standard = ''
        self.set_features()
        Vector.objects[(dataset, iso, str(gloss.lower()), self._ID)] = self
        Vector.datasets[(dataset, iso)] = True

    def set_features(self):
        self._features = {}
        # General features
        self._features['gloss_' + str(self._gloss)] = 1
        if self._gloss in MapGloss.standard:
            self._features['is_standard'] = 1
            self._features['standard_'+str(self._gloss)] = 1
        # Morphemes
        for M in self._morphemes:
            self._features['shared_morpheme_' + str(M)] = 1
        # Segments
        for S in self._segments:
            if self._segments[S]:
                self._features['segment_match_' + str(S)] = 1
            else:
                self._features['segment_nonmatch_' + str(S)] = 1
        if self._segments:
            self._features['segment_count'] = len(self._segments)
        """
        # Distances
        for D in self._distances:
            self._features['distance_' + str(D) + '_' +
                           str(self._distances[D])] = 1
        """
        # Features to improve incomplete disambiguation
        if self._gloss in StandardValue.objects:
            self._features['std_value_' + str(StandardValue.objects[
                self._gloss]._feature)] = 1
        """
        # Features to improve word disambiguation
        self._features['count_' + str(GoldStandard.objects[(self._dataset,
                       self._iso, self._gloss)]._observed)] = 1
        self._features['length_' + str(len(self._gloss))] = 1
        self._features['vowels_' + str(len(re.findall('[aeiou]', self._gloss,
                                                      re.IGNORECASE)))] = 1
        """
        if self._word_match:
            self._features['word_match'] = 1
        if str(self._raw_gloss).islower():
            self._features['lower_case'] = 1
        elif str(self._raw_gloss).isupper():
            self._features['upper_case'] = 1
        else:
            self._features['mixed_case'] = 1
        return True

    def load(restart=False):
        """Load the glosses CLSO file.
        """
        if restart == False:
            try:
                reader = CSLO('gloss', option='r')
                reader.load()
                return True
            except:
                pass
        Gloss.objects = {}
        return True

    def export():
        """Export the glosses CLSO file.
        """
        writer = CLSO('vector', option='w')
        writer.bulk_dump('Vector')
        return True

    def delete_vector(dataset_value, iso_value, gloss_value, ID_value=''):
        """Delete a vector value.

        Keyword arguments:
          dataset_value -- the dataset value of the gloss
          iso_value -- the iso value of the gloss
          gloss_value -- the gloss value
          ID_value -- the ID value of the gloss
        """
        if ID_value:
            del Vector.objects[(dataset_value, iso_value, gloss_value,
                                ID_value)]
        else:
            matches = []
            for gloss in Vector.objects:
                if (gloss[0] == dataset_value and gloss[1] == iso_value and
                    gloss[2] == gloss_value):
                    matches.append(gloss[3])
            for ID in matches:
                del Vector.objects[(dataset_value, iso_value, gloss_value,
                                    ID)]
        return True

    def set_segmentation(self):
        """Locate all segments within the gloss.
        """
        # Explore all glosses
        for gloss in MapGloss.standard:
            # If there is a match
            if re.search(gloss, self._gloss):
                # Add match to segments
                self._segments[gloss] = True
                match = re.search(gloss, self._gloss)
                # Process values to the left and right of the segment
                self._set_segmentation(self._gloss[:match.span()[0]])
                self._set_segmentation(self._gloss[match.span()[1]:])
        return True

    def _set_segmentation(self, gloss_part):
        """Locate all segments within the gloss, if the gloss is Leipzig
        or Gold it will match itself. This is for inner recursion of the
        remainder.
        """
        if not gloss_part:
            return False
        match = False
        # Try each gloss value
        for gloss in MapGloss.standard:
            # If there is a match
            if re.search(gloss, gloss_part):
                # Add match to segments
                self._segments[gloss] = True
                match = True
                match = re.search(gloss, gloss_part)
                # Process values to the left and right of the segment
                self._set_segmentation(gloss_part[:match.span()[0]])
                self._set_segmentation(gloss_part[match.span()[1]:])
        # If no match has been found
        if not match:
            # Add the gloss part to segments
            self._segments[gloss_part] = False
        return True

class UniqueVector:

    objects = {}
    std_obs = {}
    languages = {}
    p_std_obs = {}
    weights = {'NB': 0.00, 'TBL': 1.0}

    def __init__(self, dataset, iso, gloss):
        self._dataset = dataset
        self._iso = iso
        self._gloss = str(gloss)
        self._results = {}
        # Add values to Language class
        if (dataset, iso) not in Language.objects:
            Language(dataset, iso)
        self._language = Language.objects[(dataset, iso)]
        self._language._obs_glosses[str(gloss)] = True
        # Add observed value to the Langauge class
        if self._dataset not in Language.obs_glosses:
            Language.obs_glosses[dataset] = {}
        Language.obs_glosses[dataset][(iso, str(gloss))] = True
        UniqueVector.objects[(dataset, iso, str(gloss))] = self

    def set_classification(self):
        self._classification = gold_standard.GS.objects[
            (self._dataset, self._iso, self._gloss)]._error_type
        return True

    def set_standard(self):
        self._standard = str(gold_standard.GS.objects[(self._dataset,
                                                       self._iso, self._gloss)]._standard)
        self._language._std_glosses[self._standard] = True
        # Set dataset level value
        if self._dataset not in Language.std_glosses:
            Language.std_glosses[self._dataset] = {}
        Language.std_glosses[self._dataset][(self._iso, self._standard)] = True
        return True

    def set_final(self):
        self._final = str(functions.max_inD(functions.combine_weightD(
            self._results, UniqueVector.weights), tie='word')[0])
        self._language._final_glosses[self._final] = True
        # Set dataset level value
        if self._dataset not in Language.final_glosses:
            Language.final_glosses[self._dataset] = {}
        Language.final_glosses[self._dataset][(self._iso, self._final)] = True
        return True

class Language:

    objects = {}
    std_glosses = {} # {dataset: {(iso, gloss): True}}
    obs_glosses = {}
    final_glosses = {}

    def __init__(self, dataset, iso):
        self._dataset = dataset
        self._iso = iso
        self._std_glosses = {}
        self._obs_glosses = {}
        self._final_glosses = {}
        Language.objects[(dataset, iso)] = self

    def load(restart=False):
        """Load the languages CLSO file.
        """
        if restart == False:
            try:
                reader = CSLO('language', option='r')
                reader.load()
                return True
            except:
                pass
        Language.objects = {}
        return True

    def export():
        """Export the languages CLSO file.
        """
        writer = CLSO('language', option='w')
        writer.bulk_dump('Language')
        return True

    def delete_language(iso_value):
        """Delete a language value.

        Keyword arguments:
          iso_value -- the iso value of the language
        """
        del Language.objects[iso_value]
        return True

    @staticmethod
    def get_language_glosses():
        glosses = {}
        for obj in Language.objects:
            glosses[obj] = {}
            for gloss in Language.objects[obj]._final_glosses:
                glosses[obj][gloss] = True
            glosses[obj]['<obs>'] = {}
            for gloss in Language.objects[obj]._obs_glosses:
                glosses[obj]['<obs>'][gloss] = True
        return glosses

    def process_class_lstd():
        std = {}
        for dataset in Language.std_glosses:
            for gloss in Language.std_glosses[dataset]:
                if gloss[1] not in std:
                    std[gloss[1]] = {}
                std[gloss[1]][gloss[0]] = True
        contra = {}
        for gloss in std:
            if len(std[gloss]) not in contra:
                contra[len(std[gloss])] = {}
            contra[len(std[gloss])][gloss] = True
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/lstd'):
            os.mkdir(os.getcwd() + '/evaluation/lstd')
        writer = open('evaluation/lstd/master_file', 'w')
        for key in sorted(contra.keys(), reverse=True):
            for gloss in contra[key]:
                writer.write('{0:16} {1:4}\n'.format(gloss, key))
        writer.write('\nObserve glosses with ISO values\n')
        for key in sorted(contra.keys(), reverse=True):
            for gloss in contra[key]:
                writer.write('{0:16} {1}\n'.format(gloss, std[gloss]))
        writer.close()
        return True

    def process_lstd(self):
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/lstd'):
            os.mkdir(os.getcwd() + '/evaluation/lstd')
        writer = open('evaluation/lstd/' + str(self._iso), 'w')
        for gloss in self._std_glosses:
            writer.write(gloss, '\n')

    def process_cprf(self):
        if not os.path.exists(os.getcwd() + '/evaluation'):
            os.mkdir(os.getcwd() + '/evaluation')
        if not os.path.exists(os.getcwd() + '/evaluation/cprf'):
            os.mkdir(os.getcwd() + '/evaluation/cprf')
        file = 'evaluation/cprf/' + str(self._iso)



if not os.path.exists(os.getcwd() + '/model.clso'):
    print('Existing map_gloss model not found, constructing one now.')

    MapGloss.process(train, test)

if __name__ == '__main__':
    MapGloss.produce(test)

"""
MapGloss.cross_validation(train, 'dev')
MapGloss.cross_validation(train + test, 'test')
"""

