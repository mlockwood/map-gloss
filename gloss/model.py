#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import re
import os

from gloss.errors import *
from utils import functions
from eval.gold_standard import GoldStandard, Lexicon
from gloss.constants import CLASSIFIERS
from gloss.dataset import *
from gloss.result import UniqueGloss, Container
from gloss.standard import Gram
from gloss.tbl import TBL
from gloss.vector import *
from utils.classes import DataModelTemplate


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
        self.train = get_collection(self.train)
        self.test = get_collection(self.test)
        self.classifiers = self.validate_classifiers(self.classifiers)
        self.reference = Reference(**{"model": self.name})
        self.reference.init_results()
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

    def run_classifiers(self, evaluate, out_path):
        for classifier in self.classifiers:

            # If TBL
            if classifier == 'tbl':
                TBL.default = 'lexical entry'
                TBL.set_cls_path(out_path)
                tbl_classifier = TBL(self.train.vectors, self.name)
                tbl_classifier.train_model()
                tbl_classifier.decode(self.test.vectors)
                self.reference.set_classifier_results(tbl_classifier, 'tbl')

        self.reference.set_final_results(evaluate, out_path)


class Reference(DataModelTemplate):

    json_path = None
    objects = {}

    def init_results(self):
        self.results = {}
        for vector_id in self.test:
            vector = self.test[vector_id]
            if vector["dataset"] not in self.results:
                self.results[vector["dataset"]] = {}
            if vector["iso"] not in self.results[vector["dataset"]]:
                self.results[vector["dataset"]][vector["iso"]] = {}
            self.results[vector["dataset"]][vector["iso"]][vector["gloss"]] = {
                "gold": GoldStandard.objects[vector["unique"]].gram,  # FIX THIS TO CORRECT ATTR
                "input": vector["gloss"],
                "final": {}
            }

    def set_classifier_results(self, classifier, classifier_name):
        for dataset, iso, gloss in classifier.results:
            self.results[dataset][iso][gloss]["final"][classifier_name] = functions.prob_conversion(
                classifier.results.get((dataset, iso, gloss), 0))

    def set_final_results(self, evaluate, out_path):
        # Aggregate results from all models
        for dataset in self.results:
            for iso in self.results[dataset]:
                for gloss in self.results[dataset][iso]:
                    self.results[dataset][iso][gloss]["final"] = str(functions.max_value(functions.combine_weight(
                        self.results[dataset][iso][gloss]["final"], self.classifiers), tie='lexical entry')[0])

        if evaluate:
            # Set files for each container in the model
            for container in self.containers:
                Container.objects[container].set_confusion_matrices(out_path)
                Container.objects[container].set_unique_gloss_evaluation(out_path)


def set_gold_standard():
    annotate = []
    # Process every vector
    for vector in Vector.objects:
        # Collect vector obj
        obj = Vector.objects[vector]

        # If GoldStandard object does not exist, create GoldStandard object
        if (obj.dataset, obj.iso, obj.gloss) not in GoldStandard.objects:
            annotate += [(obj.dataset, obj.iso, obj.gloss)]
            GoldStandard(obj.dataset, obj.iso, obj.gloss)

        # If GoldStandard standard does not exist, add observation
        elif not GoldStandard.objects[(obj.dataset, obj.iso, obj.gloss)].label:
            GoldStandard.objects[(obj.dataset, obj.iso, obj.gloss)].add_count()

        # If GoldStandard has a standard send to Vector
        else:
            obj.label = str(GoldStandard.objects[(obj.dataset, obj.iso, obj.gloss)].label)

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
    set_vectors(datasets)

    # Configure gold standard
    if evaluate:
        GoldStandard.json_path = gold_standard_file if gold_standard_file else 'data/gold_standard.json'
        GoldStandard.load()
        Lexicon.json_path = lexicon_file if lexicon_file else 'data/lexicon.json'
        Lexicon.load()
        set_gold_standard()

    # Process models
    Model.json_path = model_file
    Model.load()
    for model in Model.objects:
        Model.objects[model].run_classifiers(evaluate, out_path)
    Reference.export()


def use_internal_parameters():

    return True


if __name__ == "__main__":
    use_internal_parameters()
