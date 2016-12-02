#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from eval.confusion_matrix import CM, Compare
from eval.gold_standard import GoldStandard, Lexicon
from gloss.constants import CLASSIFIERS
from gloss.dataset import *
from gloss.errors import *
from gloss.tbl import TBL
from gloss.vector import *
from utils.classes import DataModelTemplate
from utils import functions
from utils.IOutils import set_directory


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


class Model(DataModelTemplate):

    json_path = None
    objects = {}

    def set_object_attrs(self):
        self.train = get_collection(self.train) if self.train else None  # FIX WITH LOADING VECTORS.JSON FROM SRC
        self.test = get_collection(self.test)
        self.classifiers = self.validate_classifiers(self.classifiers)
        self.reference = Reference(**{"model": self.name, "results": self.init_results()})
        Model.objects[self.name] = self

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

            # Add classifier to classifiers and add weights to weight
            classifiers[classifier[0]] = classifier[1]
            weight += classifier[1]

        # Verify that the total weight is equal to 1.00
        if weight != 1.0:
            raise ClassifierWeightError('Model {} weights do not equal 1.0.'.format(self.name))

        return classifiers

    def init_results(self):
        results = {}
        for vector_id in self.test:
            vector = self.test[vector_id]
            results[vector["unique"]] = {
                "gold": GoldStandard.objects[vector["unique"]].gram,  # FIX THIS TO CORRECT ATTR
                "input": vector["gloss"],
                "final": {}
            }
        return results

    def run_classifiers(self, out_path):
        for classifier in self.classifiers:

            # If TBL
            if classifier == 'tbl':
                TBL.default = 'lexical entry'
                TBL.set_cls_path(out_path)
                tbl_classifier = TBL(self.train.vectors, self.name)
                tbl_classifier.train_model()
                tbl_classifier.decode(self.test.vectors)
                self.reference.set_classifier_results(tbl_classifier, 'tbl')

        if out_path:
            set_directory('{}/reports/cprf/'.format(out_path))
            set_directory('{}/reports/unique_gloss/acc'.format(out_path))
            set_directory('{}/reports/unique_gloss/out'.format(out_path))

        self.reference.set_final_results(out_path)


class Reference(DataModelTemplate):

    json_path = None
    objects = {}

    @classmethod
    def get_all_results(cls):
        results = {}
        for model in cls.objects:
            results[model] = cls.objects[model].results
        return results

    def set_classifier_results(self, classifier, classifier_name):
        for gloss in classifier.results:
            self.results[gloss]["final"][classifier_name] = functions.prob_conversion(classifier.results.get(gloss, 0))

    def set_final_results(self, out_path):
        # Aggregate results from all models
        for gloss in self.results:
            self.results[gloss]["final"] = str(functions.max_value(functions.combine_weight(
                self.results[gloss]["final"], self.classifiers), tie='lexical entry')[0])
        # Create reports
        self.output_cprf_reports(out_path, self.get_ref_dict('gold'), self.get_ref_dict('final'))
        self.output_unique_gloss_reports(out_path)

    def get_ref_dict(self, key, value='final'):
        return dict(((gloss[0], gloss[1], key), self.results[gloss][value]) for gloss in self.results)

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
        functions.accuracy(acc, '{}/reports/unique_gloss/acc/{}'.format(out_path, self.model))
        functions.out_evaluation(correct_total, len(self.results), incorrect_list, correct_list,
                                 '{}/reports/unique_gloss/out/{}'.format(out_path, self.model))


def set_gold_standard(vectors):
    annotate = []
    # Process every vector
    for vector in vectors:
        # If GoldStandard object does not exist, create GoldStandard object
        if (vector["dataset"], vector["iso"], vector["gloss"]) not in GoldStandard.objects:
            annotate += [(vector["dataset"], vector["iso"], vector["gloss"])]
            GoldStandard(vector["dataset"], vector["iso"], vector["gloss"])  # USE KWARGS DICT--------------------------

        # If GoldStandard standard does not exist, add observation
        elif not GoldStandard.objects[(vector["dataset"], vector["iso"], vector["gloss"])].label:
            GoldStandard.objects[(vector["dataset"], vector["iso"], vector["gloss"])].add_count()

        # If GoldStandard has a standard send to Vector
        else:
            vector["label"] = str(GoldStandard.objects[(vector["dataset"], vector["iso"], vector["gloss"])].label)

    # If there were values that needed a GoldStandard standard
    if annotate:
        # Seek input and then send to Vector
        GoldStandard.annotate(annotate)
        for unique in annotate:
            for vector in Vector.lookup[unique]:
                vector.label = GoldStandard.objects[unique].label
    return True


def process_models(dataset_file, model_file, evaluate=False, out_path=None, gold_standard_file=None, lexicon_file=None):
    # Set up datasets
    datasets = infer_datasets(json.load(dataset_file))
    vectors = set_vectors(datasets)

    # Configure gold standard -- NEEDS TO BE DONE ON TRAINING BUT ONLY ON TEST IF EVALUATE
    if evaluate:
        GoldStandard.json_path = gold_standard_file if gold_standard_file else 'data/gold_standard.json'
        GoldStandard.load()
        Lexicon.json_path = lexicon_file if lexicon_file else 'data/lexicon.json'
        Lexicon.load()
        set_gold_standard(vectors)

    # Process models
    Model.json_path = model_file
    Model.load()
    for model in Model.objects:
        Model.objects[model].run_classifiers(out_path)

    # Set outputs
    if out_path:
        Reference.json_path = '{}/out/reference.json'.format(out_path)
        Reference.export()
    return Reference.get_all_results()


if __name__ == "__main__":
    pass
