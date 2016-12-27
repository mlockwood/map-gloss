#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from eval.constants import *
from gloss.standard import Gram, Value
from utils.data_model import DataModel
from utils.dict_calculations import *
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


class GoldStandard(DataModel):

    json_path = [GOLD_STANDARD_FILE]
    objects = {}  # (dataset, iso, gloss)
    stats = {}
    temp = {}

    def set_objects(self):
        GoldStandard.objects[(self.dataset, self.iso, self.gloss)] = self

    def set_object_attrs(self):
        if hasattr(self, "count"):
            delattr(self, "count")

    @classmethod
    def annotate(cls, glosses):
        """
        Allow the user to annotate glosses.
        :param glosses: (dataset, iso, gloss); these are unique glosses
        :return: True once all glosses have been annotated
        """
        # Check for default annotations
        annotate = []
        for gloss in glosses:
            # If a standard gloss; CONCERN WITH COMBINED LIKE RUSSIAN IMP/IPFV
            if gloss[2] in Gram.objects:
                cls.set_standard(gloss, 'standard', gloss[2])
            # If a known word
            elif gloss[2] in Lexicon.objects:
                cls.set_standard(gloss, 'lexical entry', 'lexical entry')
            # If a known value
            elif gloss[2] in Value.objects:
                cls.set_standard(gloss, Value.objects[gloss[2]].classification, Value.objects[gloss[2]].gram)
            # Otherwise seek standard
            else:
                annotate.append(gloss)

        # If there are glosses to annotate print the instructions for annotation
        if annotate:
            print('For each gloss please first enter:')
            for label in LABEL_TEXT:
                print('\t({}) If it is {}'.format(*label))

        # Process the annotations
        prev_iso = ''
        for gloss in sorted(annotate):
            # Alert user of current dataset and iso
            if prev_iso != gloss[1]:
                print('Dataset: {} | Language: {}'.format(*gloss[:2]))
                prev_iso = gloss[1]

            # Until an acceptable classification type number is entered
            while True:
                label = input('\t{}:'.format(gloss[2]))

                # If entered value is not one of the options
                if label not in LABELS:
                    print('The value entered is not one of the options. Please try again')

                # If entered value is recognized handle the discovery of the grams by L(abel) type
                else:
                    L = LABELS[label][1]
                    repeat = True if L == 2 else False
                    gram = gloss[2] if L == 0 else (LABELS[label][0] if L == 3 else cls.seek_standard(gloss[2], repeat))
                    cls.set_standard(gloss, LABELS[label][0], gram)

                    # Add lexical entries to the Lexicon
                    if LABELS[label][0] == 'lexical entry':
                        Lexicon(**{"entry": gloss[2]})
                    break

        cls.export()

    @classmethod
    def set_standard(cls, gloss, classification_type, gram):
        cls.objects[gloss].classification_type = classification_type
        if classification_type == 'incomplete' or classification_type == 'combined':
            cls.objects[gloss].gram = classification_type
            cls.objects[gloss].final_grams = gram
        else:
            cls.objects[gloss].gram = gram

    @staticmethod
    def seek_standard(gloss, repeat=False):
        if repeat:
            standard = []
            value = ''
            while str(value) != '0':
                value = input('\tWhat is one of the glosses for {} (use 0 if no more values): '.format(gloss))
                if str(value) != '0' and value != '':
                    standard.append(value.lower())
        else:
            standard = input('\tWhat is the correct value for {}: '.format(gloss))
        return standard

    @classmethod
    def report(cls, out_path):
        """Report all of the GS statistics to file.
        """
        if out_path:
            set_directory('{}/reports/gold_standard'.format(out_path))
            cls.run_statistics()
            for dataset in cls.stats:
                if dataset != 'complete':
                    writer = open('{}/reports/gold_standard/{}_report.txt'.format(out_path, str(dataset)), 'w')
                    iso_map = {}
                    for iso in cls.stats[dataset]:
                        iso_map[iso] = True
                    del iso_map['aggregate']
                    iso_list = ['aggregate'] + sorted(iso_map.keys())
                else:
                    writer = open('{}/reports/gold_standard/complete_report.txt'.format(out_path), 'w')
                    iso_list = ['complete']

                writer.write('Gold Standard Statistics for: {}\n\n'.format(dataset))

                for iso in iso_list:
                    writer.write('{} statistics:\n'.format(iso))
                    total = 0.0
                    for error in cls.stats[dataset][iso]:
                        total += cls.stats[dataset][iso][error]
                    err = {}
                    for error in cls.stats[dataset][iso]:
                        err[error] = cls.stats[dataset][iso][error] / total

                    for clsf in CLASSIFICATION_TYPES:
                        if clsf in cls.stats[dataset][iso]:
                            writer.write('\t{0:16s}: {1:4d} & {2:.4f}\n'.format(clsf.title(),
                                                                                cls.stats[dataset][iso][clsf],
                                                                                err[clsf]))
                    writer.write('\n')
                writer.close()

    @classmethod
    def run_statistics(cls):
        cls.stats = {'complete': {'complete': {}}}
        for gloss in cls.objects:

            # Define gloss components
            dataset = gloss[0]
            iso = gloss[1]
            clsf = cls.objects[gloss].classification_type

            # Set cls.languages[dataset][iso] = {}
            if dataset not in cls.stats:
                cls.stats[dataset] = {'aggregate': {}}
            if iso not in cls.stats[dataset]:
                cls.stats[dataset][iso] = {}

            # Set GoldStandard classification type breakdowns
            cls.stats[dataset][iso][clsf] = cls.stats[dataset][iso].get(clsf, 0) + 1
            cls.stats[dataset]['aggregate'][clsf] = cls.stats[dataset]['aggregate'].get(clsf, 0) + 1
            cls.stats['complete']['complete'][clsf] = cls.stats['complete']['complete'].get(clsf, 0) + 1

    @classmethod
    def unigram_baseline(cls, train, test):
        model = {}
        test_obj = []
        test_acc = {'pos': 0, 'neg': 0}
        for obj in cls.objects:
            if obj[0] in train:
                if cls.objects[obj].gloss not in model:
                    model[cls.objects[obj].gloss] = {}
                model[cls.objects[obj].gloss][cls.objects[obj].gram] = (
                    model[cls.objects[obj].gloss].get(cls.objects[obj].gram, 0) + 1)
            elif obj[0] in test:
                test_obj.append(cls.objects[obj])
        for obj in test_obj:
            # Known glosses
            if obj.gloss in model:
                key = 'pos' if max_value(model[obj.gloss])[0] == obj.gram else 'neg'
            # Gloss unknown but in standard set
            elif obj.gloss in Gram.objects:
                key = 'pos' if obj.gloss == obj.label else 'neg'
            # Otherwise assume it is a word
            else:
                key = 'pos' if obj.gram == 'lexical entry' else 'neg'
            test_acc[key] = test_acc.get(key, 0) + 1
        acc = prob_conversion(test_acc)
        return acc


class Lexicon(DataModel):

    json_path = [LEXICON_FILE]
    objects = {}

    def set_objects(self):
        Lexicon.objects[self.entry] = self


# print(GoldStandard.unigram_baseline({'dev1': True, 'dev2': True}, {'test': True}))
