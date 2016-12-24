#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from gloss.constants import *
from gloss.dataset import *
from gloss.errors import *
from gloss.tbl import TBL
from gloss.vector import *
from utils.confusion_matrix import CM, Compare
from utils.data_model import DataModel
from utils.dict_calculations import *
from utils.IOutils import set_directory
from utils.stat_reports import accuracy, out_evaluation

__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'model.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class Model(DataModel):

    evaluate = False
    json_path = None
    loaded_defaults = False
    objects = {}

    def set_objects(self):
        Model.objects[self.name] = self

    def set_object_attrs(self):
        self.train = set_collection(self.train, True) if self.train else Model.set_default_vectors()
        self.test = set_collection(self.test, Model.evaluate)
        self.classifiers = self.validate_classifiers(self.classifiers)

    @classmethod
    def set_default_vectors(cls):
        if not cls.loaded_defaults:
            cls.loaded_defaults = True
            set_vectors(infer_datasets(json.load(open(DATASET_FILE, 'r'))))
            set_collection(DEFAULT_TRAINING, True)
        return DEFAULT_TRAINING if isinstance(DEFAULT_TRAINING, str) else ' '.join(DEFAULT_TRAINING)

    def validate_classifiers(self, classifiers):
        weight = 0.0
        for classifier in classifiers:

            # Verify that the classifier is a valid/known classifier
            if classifier not in CLASSIFIERS:
                raise InvalidClassifierError('{} for model {} is not a valid classifier'.format(self.name, classifier))

            # Verify that the weight is a valid weight
            if not (0.0 <= classifiers[classifier] <= 1.0):
                raise InvalidClassifierWeightError('Model {} has an invalid weight for {} of {}.'.format(
                    self.name, classifier, classifiers[classifier]))

            # Add weights to weight
            weight += classifiers[classifier]

        # Verify that the total weight is equal to 1.00
        if weight != 1.0:
            raise ClassifierWeightError('Model {} weights do not equal 1.0.'.format(self.name))

        return classifiers

    def init_results(self):
        results = {}
        for vector in self.test:
            results[vector["unique"]] = {
                "gold": None if not Model.evaluate else vector["gram"],
                "input": vector["gloss"],
                "final": {}
            }
        return results

    def run_classifiers(self, out_path):
        self.train = get_collection(self.train)
        self.test = get_collection(self.test)
        self.reference = Reference(**{"model": self.name, "classifiers": self.classifiers,
                                      "results": self.init_results()})
        for classifier in self.classifiers:

            # If TBL
            if classifier == 'tbl':
                TBL.default = 'lexical entry'
                TBL.set_cls_path(out_path)
                tbl_classifier = TBL(self.train, self.name)
                tbl_classifier.train_model()
                tbl_classifier.decode(self.test)
                self.reference.set_classifier_results(tbl_classifier, 'tbl')

        if out_path:
            set_directory('{}/reports/cprf/'.format(out_path))
            set_directory('{}/reports/unique_gloss/acc'.format(out_path))
            set_directory('{}/reports/unique_gloss/out'.format(out_path))

        self.reference.set_final_results(out_path)


class Reference(DataModel):

    json_path = None
    objects = {}

    def set_objects(self):
        Reference.objects[self.model] = self

    @classmethod
    def get_all_results(cls):
        results = {}
        for model in cls.objects:
            results[model] = cls.objects[model].results
        return results

    def set_classifier_results(self, classifier, classifier_name):
        for gloss in classifier.results:
            self.results[gloss]["final"][classifier_name] = prob_conversion(classifier.results.get(gloss, 0))

    def set_final_results(self, out_path):
        # Aggregate results from all models
        for gloss in self.results:
            self.results[gloss]["final"] = str(max_value(combine_weight(self.results[gloss]["final"], self.classifiers),
                                                         tie='lexical entry')[0])
        # Create reports
        if Model.evaluate:
            self.output_cprf_reports(out_path, self.get_ref_dict('gold'), self.get_ref_dict('final'))
            self.output_unique_gloss_reports(out_path)

    def get_ref_dict(self, key, value='final'):
        return dict(((gloss[0], gloss[1], self.results[gloss][key]), self.results[gloss][value]
                     ) for gloss in self.results)

    def output_cprf_reports(self, out_path, gold, final):
        # Create a comparative confusion matrix of the two initial confusion matrices
        cprf = Compare(CM(gold, final, '{}_final'.format(self.model)),
                       CM(gold, self.results, '{}_baseline'.format(self.model)))
        cprf.write_cprf_file('{}/reports/cprf/{}'.format(out_path, self.model))

    def output_unique_gloss_reports(self, out_path):
        # Set up data structures
        correct_total = 0
        incorrect_list = []
        correct_list = []
        acc = {}

        # Process each gloss
        for gloss in self.results:
            # Build accuracy DS
            if self.results[gloss]["gold"] not in acc:
                acc[self.results[gloss]["gold"]] = {}
            acc[self.results[gloss]["gold"]][self.results[gloss]["final"]] = acc[self.results[gloss]["gold"]].get(
                self.results[gloss]["final"], 0) + 1

            # Build out DS (direct evaluation of each unique gloss)
            entry = [', '.join(gloss), self.results[gloss]["gold"], self.results[gloss]["final"]]
            if self.results[gloss]["gold"] == self.results[gloss]["final"]:
                correct_total += 1
                correct_list += [entry]
            else:
                incorrect_list += [entry]

        # Write accuracy and out_evaluation
        accuracy(acc, '{}/reports/unique_gloss/acc/{}'.format(out_path, self.model))
        out_evaluation(correct_total, len(self.results), incorrect_list, correct_list,
                       '{}/reports/unique_gloss/out/{}'.format(out_path, self.model))


def process_models(dataset_file, model_file, evaluate=False, out_path=None, gold_standard_file=None, lexicon_file=None):
    # Set up datasets and vectors
    set_vectors(infer_datasets(json.load(open(dataset_file, 'r'))))

    # Process models
    Model.evaluate = evaluate
    Model.json_path = model_file
    Model.load()
    set_gold_standard(gold_standard_file, lexicon_file)
    GoldStandard.report(out_path)
    for model in Model.objects:
        Model.objects[model].run_classifiers(out_path)

    # Set outputs
    if out_path:
        Reference.json_path = '{}/out/reference.json'.format(out_path)
        # Reference.export()
    return Reference.get_all_results()


# refs = process_models(DATASET_FILE, MODEL_FILE, True, OUT_PATH)
