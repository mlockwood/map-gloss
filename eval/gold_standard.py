#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import os

from utils.classes import DataModelTemplate
from utils import functions
from eval.constants import CLASSIFICATION_TYPES, LABELS, LABEL_TEXT
from gloss.standard import Gram, Value


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


class GoldStandard(DataModelTemplate):

    json_path = None
    objects = {}  # (dataset, iso, gloss)
    languages = {}
    lexicon = {}

    def set_object_attrs(self):
        GoldStandard.objects[(self.dataset, self.iso, self.gloss)] = self

    @staticmethod
    def annotate(glosses):
        """
        Allow the user to annotate glosses.
        :param glosses: (dataset, iso, gloss); these are unique glosses
        :return: True once all glosses have been annotated
        """
        # Check for default annotations
        annotate = []
        for gloss in glosses:
            # If a standard gloss
            # NOTE CONCERN WITH RUSSIAN IMP/IPFV
            if gloss[2] in Gram.objects:
                GoldStandard.set_standard(gloss, 'standard', gloss[2])
            # If a known word
            elif gloss[2] in Lexicon.objects:
                GoldStandard.set_standard(gloss, 'lexical entry', 'lexical entry')
            # If a known value
            elif gloss[2] in Value.objects:
                if Value.objects[gloss[2]]["category"] == "part-of-speech":
                    GoldStandard.set_standard(gloss, 'part-of-speech', 'part-of-speech')
                else:
                    GoldStandard.set_standard(gloss, 'incomplete', 'incomplete')
            # Otherwise seek standard
            else:
                annotate.append(gloss)

        # If there are glosses to annotate print the instructions for annotation
        if annotate:
            text = 'For each gloss please first enter:\n'
            for label in LABEL_TEXT:
                text += ('\t({}) If it is {}\n'.format(*label))
            print(text)

        # Process the annotations
        dataset = ''
        iso = ''
        for gloss in sorted(annotate):
            # Alert user of current dataset and iso
            valid = False
            if dataset != gloss[0]:
                print('Dataset: ' + str(gloss[0]))
                dataset = gloss[0]
            if iso != gloss[1]:
                print('Language: ' + str(gloss[1]))
                iso = gloss[1]

            # Until an acceptable classification type number is entered
            while not valid:
                classification_type = input('\t{}:'.format(gloss[2]))

                try:
                    classification_type = int(classification_type)
                except TypeError:
                    print('The value entered is not one of the options. Please try again')
                    continue

                # If entered value is not one of the options
                if classification_type not in LABELS:
                    print('The value entered is not one of the options. Please try again')

                # If entered value is recognized, set the standard
                else:
                    valid = True

                    # Process labels of 'standard'
                    if LABELS[classification_type][1] == 0:
                        GoldStandard.set_standard(gloss, LABELS[classification_type][0], gloss[2])

                    # Process labels of 'misspelled, confused'
                    elif LABELS[classification_type][1] == 1:
                        GoldStandard.set_standard(gloss, LABELS[classification_type][0],
                                                  GoldStandard.seek_standard(gloss[2]))

                    # Process labels of 'incomplete, combined'
                    elif LABELS[classification_type][1] == 2:
                        GoldStandard.set_standard(gloss, LABELS[classification_type][0],
                                                  GoldStandard.seek_standard(gloss[2], repeat=True))

                    # Process labels where label is equal to the classification type
                    if LABELS[classification_type][1] == 3:
                        GoldStandard.set_standard(gloss, LABELS[classification_type][0], LABELS[classification_type][0])

                    # Add lexical entries to the Lexicon
                    if LABELS[classification_type][0] == 'lexical entry':
                        GoldStandard.lexicon[gloss[2]] = True

        GoldStandard.export()
        return True

    @staticmethod
    def set_standard(gloss, classification_type, gold_grams):
        GoldStandard.objects[gloss].classification_type = classification_type
        if classification_type == 'incomplete' or classification_type == 'combined':
            GoldStandard.objects[gloss].label = classification_type
            GoldStandard.objects[gloss].gold_grams = gold_grams
        else:
            GoldStandard.objects[gloss].label = gold_grams
        return True

    @staticmethod
    def seek_standard(gloss, repeat=False):
        if repeat:
            s_list = []
            standard = ''
            while str(standard) != '0':
                standard = input('\tWhat is one of the glosses for {} (use 0 if no more values): '.format(gloss))
                if str(standard) != '0' and standard != '':
                    s_list.append(standard.lower())
            standard = s_list
        else:
            standard = input('\tWhat is the correct value for {}: '.format(gloss))
        return standard

    @staticmethod
    def run_statistics():
        GoldStandard.languages = {'complete': {'complete': {}}}
        for gloss in GoldStandard.objects:

            # Define gloss components
            unique = gloss
            dataset = gloss[0]
            iso = gloss[1]
            gloss = gloss[2]

            # Set GoldStandard.languages[dataset][iso] = {}
            if dataset not in GoldStandard.languages:
                GoldStandard.languages[dataset] = {'Aggregate': {}}
            if iso not in GoldStandard.languages[dataset]:
                GoldStandard.languages[dataset][iso] = {}

            # Set GoldStandard classification type breakdowns
            clsf = GoldStandard.objects[unique].classification_type
            GoldStandard.languages[dataset][iso][clsf] = GoldStandard.languages[dataset][iso].get(clsf, 0) + 1
            GoldStandard.languages[dataset]['Aggregate'][clsf] = GoldStandard.languages[dataset]['Aggregate'].get(
                clsf, 0) + 1
            GoldStandard.languages['complete']['complete'][clsf] = GoldStandard.languages['complete']['complete'].get(
                clsf, 0) + 1
        return True

    @staticmethod
    def report():
        """Report all of the GS statistics to file.
        """
        GoldStandard.run_statistics()
        for dataset in GoldStandard.languages:
            if dataset != 'complete':
                if not os.path.isdir('{}/reports/gold_standard'.format(PATH)):
                    os.makedirs('{}/reports/gold_standard'.format(PATH))
                writer = open('{}/reports/gold_standard/{}_report.txt'.format(PATH, str(dataset)), 'w')

                iso_map = {}
                for iso in GoldStandard.languages[dataset]:
                    iso_map[iso] = True
                del iso_map['Aggregate']
                iso_list = ['Aggregate'] + sorted(iso_map.keys())
            else:
                if not os.path.isdir('{}/reports/gold_standard'.format(PATH)):
                    os.makedirs('{}/reports/gold_standard'.format(PATH))
                writer = open('{}/reports/gold_standard/complete_report.txt'.format(PATH), 'w')
                iso_list = ['complete']

            writer.write('Gold Standard Statistics for: ' + str(dataset) + '\n\n')

            for iso in iso_list:
                writer.write(str(iso) + ' Statistics:\n')
                total = 0.0
                for error in GoldStandard.languages[dataset][iso]:
                    total += GoldStandard.languages[dataset][iso][error]
                err = {}
                for error in GoldStandard.languages[dataset][iso]:
                    err[error] = GoldStandard.languages[dataset][iso][error] / total

                for clsf in CLASSIFICATION_TYPES:
                    if clsf in GoldStandard.languages[dataset][iso]:
                        writer.write('    {0:16s} {1:4d} & {2:.4f}\n'.format(clsf.title() + ':',
                                                                          GoldStandard.languages[dataset][iso][clsf],
                                                                          err[clsf]))
                writer.write('\n')
            writer.close()
        return True

    def add_count(self):
        """Add an entry to the observation set for the dataset,
        iso_code, and gloss.
        """
        # Increment occurrence count for the gloss
        self.count += 1
        return True

    @staticmethod
    def unigram_baseline(train, test):
        model = {}
        test_obj = []
        test_acc = {'pos': 0, 'neg': 0}
        for obj in GoldStandard.objects:
            if obj[0] in train:
                if GoldStandard.objects[obj].gloss not in model:
                    model[GoldStandard.objects[obj].gloss] = {}
                model[GoldStandard.objects[obj].gloss][GoldStandard.objects[obj].label] = (
                    model[GoldStandard.objects[obj].gloss].get(GoldStandard.objects[obj].label, 0) + GoldStandard.objects[obj].count)
            elif obj[0] in test:
                test_obj.append(GoldStandard.objects[obj])
        for obj in test_obj:
            # Known glosses
            if obj.gloss in model:
                if functions.max_value(model[obj.gloss])[0] == obj.label:
                    test_acc['pos'] = test_acc.get('pos', 0) + 1
                else:
                    test_acc['neg'] = test_acc.get('neg', 0) + 1
            # Unknown glosses
            # Gloss in standard set
            elif obj.gloss in GRAMS:
                if obj.gloss == obj.label:
                    test_acc['pos'] = test_acc.get('pos', 0) + 1
                else:
                    test_acc['neg'] = test_acc.get('neg', 0) + 1
            # Otherwise assume it is a word
            else:
                if obj.label == 'lexical entry':
                    test_acc['pos'] = test_acc.get('pos', 0) + 1
                else:
                    test_acc['neg'] = test_acc.get('neg', 0) + 1
        acc = functions.prob_conversion(test_acc)
        return acc


class Lexicon(DataModelTemplate):

    json_file = None
    objects = {}

    def set_object_attrs(self):
        Lexicon.objects[self.entry] = self



if __name__ == '__main__':
    print(GoldStandard.unigram_baseline({'dev1': True, 'dev2': True}, {'test': True}))
    GoldStandard.export()
    GoldStandard.report()

