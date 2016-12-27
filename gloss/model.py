#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from gloss.constants import *
from gloss.dataset import *
from gloss.errors import *
from gloss.tbl import TBL
from gloss.vector import *
from infer.load_choices import *
from infer.make_choices import *
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

    datasets = None
    eval_gloss = False
    eval_infer = False
    infer = False
    json_path = None
    loaded_defaults = False
    objects = {}

    def set_objects(self):
        Model.objects[self.name] = self

    def set_object_attrs(self):
        self.train = set_collection(self.train, True) if self.train else Model.set_default_vectors()
        self.test = set_collection(self.test, Model.eval_gloss)
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
                "baseline5": None,
                "category": None,
                "choice": None,
                "gold": None if not Model.eval_gloss else vector["gram"],
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
            if self.results[gloss]["input"] in Gram.objects:
                self.results[gloss]["baseline5"] = Gram.objects[self.results[gloss]["input"]].category[0]
            if self.results[gloss]["final"] in Gram.objects:
                self.results[gloss]["category"] = Gram.objects[self.results[gloss]["final"]].category[0]

        # Evaluate gloss mapping
        if Model.eval_gloss:
            self.output_cprf_reports(out_path, self.get_ref_dict('gold'), self.get_ref_dict('final'))
            self.output_unique_gloss_reports(out_path)

        # Process inference
        if Model.infer:
            languages = self.run_inference(out_path)

            # Evaluate inference
            if Model.eval_infer:
                self.eval_inference(
                    out_path,
                    load_model_choices(Model.datasets, languages),
                    load_model_baseline4(languages),
                    self.get_ref_dict("baseline5", "input"),
                    self.get_ref_dict("category", "final")
                )

    def get_ref_dict(self, *args, value='final'):
        ref_dict = {}
        for gloss in self.results:
            values = [gloss[0], gloss[1]]
            for arg in args:
                if self.results[gloss][arg]:
                    values.append(self.results[gloss][arg])
                else:
                    values = None
                    break
            if values:
                ref_dict[tuple(values)] = self.results[gloss][value]
        return ref_dict

    def output_cprf_reports(self, out_path, gold, final):
        cprf = Compare(CM(gold, final, '{}_final'.format(self.model)),
                       CM(gold, self.results, '{}_baseline'.format(self.model)))
        cprf.write_cprf_file('{}/reports/glosses/cprf/{}'.format(out_path, self.model))

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
        accuracy(acc, '{}/reports/glosses/acc/{}'.format(out_path, self.model))
        out_evaluation(correct_total, len(self.results), incorrect_list, correct_list,
                       '{}/reports/glosses/out/{}'.format(out_path, self.model))

    def run_inference(self, out_path):
        set_directory('{}/out/choices/{}'.format(out_path, self.model))

        # Make dataset, iso level collections of grams with their categories
        languages = {}
        for gloss in self.results:
            key = (gloss[0], gloss[1])
            gls = self.results[gloss]

            # Set up language outfiles and empty category dictionaries
            if key not in languages:
                languages[key] = {
                    "b5_categories": {},
                    "b5_outfile": '{}/out/choices/{}/{}_{}_baseline5.choices'.format(out_path, self.model, *key),
                    "categories": {},
                    "outfile": '{}/out/choices/{}/{}_{}.choices'.format(out_path, self.model, *key)
                }

            # Assign matched grams to categories
            if gls["baseline5"]:
                if gls["baseline5"] not in languages[key]["b5_categories"]:
                    languages[key]["b5_categories"][gls["baseline5"]] = {}
                languages[key]["b5_categories"][gls["baseline5"]][gls["input"]] = True
            if gls["category"]:
                if gls["category"] not in languages[key]["categories"]:
                    languages[key]["categories"][gls["category"]] = {}
                languages[key]["categories"][gls["category"]][gls["final"]] = True

        # Send each language to be made into choices files
        for language in languages:
            make_choices(languages[language]["b5_categories"], languages[language]["b5_outfile"])
            make_choices(languages[language]["categories"], languages[language]["outfile"])
            languages[language] = True
        return languages

    def eval_inference(self, out_path, gold, b4, b5, infer):
        infer_cm = CM(gold, infer, '{}_infer'.format(self.model))
        cprf4 = Compare(infer_cm, CM(gold, b4, '{}_b4'.format(self.model)))
        cprf5 = Compare(infer_cm, CM(gold, b5, '{}_b5'.format(self.model)))
        cprf4.write_cprf_file('{}/reports/choices/{}_b4'.format(out_path, self.model))
        cprf5.write_cprf_file('{}/reports/choices/{}_b5'.format(out_path, self.model))


def process_models(dataset_file, model_file, out_path=None, eval_gloss=False, gold_standard_file=None,
                   lexicon_file=None, infer=False, eval_infer=False):
    # Set up datasets and vectors
    Model.datasets = infer_datasets(json.load(open(dataset_file, 'r')))
    set_vectors(Model.datasets)

    # If there is an out_path set up all model output directories even if they will not all be used
    if out_path:
        set_directory('{}/reports/choices'.format(out_path))
        set_directory('{}/reports/glosses/cprf'.format(out_path))
        set_directory('{}/reports/glosses/acc'.format(out_path))
        set_directory('{}/reports/glosses/out'.format(out_path))

    # Process models
    Model.eval_gloss = eval_gloss if out_path else False
    Model.eval_infer = eval_infer if infer and out_path else False
    Model.infer = infer if out_path else False
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


refs = process_models(DATASET_FILE, MODEL_FILE, OUT_PATH, eval_gloss=True, infer=True, eval_infer=True)
