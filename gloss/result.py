#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import os

# Import scripts
from src.eval import confusion_matrix, gold_standard
from src.gloss import errors as GlossErrors
from src.utils import functions

# Import classes, functions, and variables
from src.gloss.constants import PATH, CTYPES


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'gloss/result.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class UniqueGloss(object):

    objects = {}

    def __init__(self, model, dataset, iso, gloss):
        self.model = model
        self.dataset = dataset
        self.iso = iso
        self.gloss = gloss
        self.unique = (dataset, iso, gloss)
        self.gold_standard = gold_standard.GoldStandard.objects[self.unique]
        self.results = {}  # {classifier: results -> {label: probability}
        self.final = {}  # {model_id: final_label}
        UniqueGloss.objects[(model, dataset, iso, gloss)] = self

    def set_final(self, weights):
        self.final = str(functions.max_value(functions.combine_weight(self.results, weights), tie='lexical entry')[0])
        return self.disseminate()

    def disseminate(self):
        # Establish containers for the model
        containers = [(self.model, 'model'),
                      ('{}_{}'.format(self.model, self.dataset), 'dataset'),
                      ('{}_{}_{}'.format(self.model, self.dataset, self.iso), 'language')]

        # Disseminate unique gloss to each container
        for container in containers:
            self.disseminate_init_helper(*container)

        # Return containers to send them back to the model
        return [container[0] for container in containers]

    def disseminate_init_helper(self, container, ctype):
        # Get container object
        if container not in Container.objects:
            Container(self.model, container, ctype)
        container = Container.objects[container]

        # Add gold standard of gloss to the gold_set
        container.gold_grams[(self.dataset, self.iso, self.gold_standard.label)] = True

        # Set GoldStandard for gloss
        container.gold_glosses[self.unique] = self.gold_standard

        # Set reference gloss
        container.ref_glosses[self.unique] = self.final

        # Set final gloss
        container.final_glosses[(self.dataset, self.iso, self.final)] = True

        return True


class Container(object):

    objects = {}

    def __init__(self, model, container, ctype='language'):
        """
        Containers are hierarchy values for glosses such as language,
        dataset, and collection.
        :param container: {language: model_dataset_iso,
                           dataset: model_dataset,
                           model: model}
        :param ctype: identify which container is used
        """
        self.model = model
        self.container = container
        if ctype in CTYPES:
            self.ctype = ctype
        else:
            raise GlossErrors.InvalidContainerTypeError(ctype)

        # All glosses here are unique -> (dataset, iso, gloss)
        self.gold_grams = {}  # {(dataset, iso, standard_gram.label): True}
        self.gold_glosses = {}  # {input_unique: standard_gram.label}
        self.ref_glosses = {}  # {input_unique: final}
        self.final_glosses = {}  # {final_unique: True}
        self.cm1 = {}
        self.cm2 = {}
        self.cprf = {}
        Container.objects[container] = self

    def set_confusion_matrices(self, out_path):
        # Create initial confusion matrices for the baseline and the final sets
        self.cm1 = confusion_matrix.CM(self.gold_grams, self.final_glosses, self.container + '_FINAL')
        self.cm2 = confusion_matrix.CM(self.gold_grams, self.ref_glosses, self.container + '_BASELINE')

        # Create a comparative confusion matrix of the two initial confusion matrices
        self.cprf = confusion_matrix.Compare(self.cm1, self.cm2)

        # Set the path for the comparative cprf file
        path = '{}/reports/cprf/{}/{}'.format(out_path, self.model, self.ctype)
        if self.model == self.container:
            path = '{}/reports/cprf/{}'.format(out_path, self.model)

        # Write the comparative cprf to file
        if not os.path.isdir(path):
            os.makedirs(path)
        self.cprf.write_cprf_file('{}/{}'.format(path, self.container))

        return True

    def set_unique_gloss_evaluation(self, out_path):
        # Set the path for the unique_gloss evaluation file
        path = '{}/reports/unique_gloss/{}/{}'.format(out_path, self.model, self.ctype)
        if self.model == self.container:
            path = '{}/reports/unique_gloss/{}'.format(out_path, self.model)

        # Set the writer for the unique_gloss evaluation file
        if not os.path.isdir(path):
            os.makedirs(path)
        writer = open('{}/{}.out'.format(path, self.container), 'w')

        # Set up data structures
        correct_total = 0
        incorrect_list = []
        correct_list = []
        acc = {}

        # Process each gloss
        for gloss in self.ref_glosses:
            # Ensure that the gold standard for the gloss is found for the container
            if gloss not in self.gold_glosses:
                raise GlossErrors.MissingGlossGoldStandardError('The model failed to recover a unique gloss for ' +
                                                                '{}.'.format(gloss))

            # Handle accuracy
            if self.gold_glosses[gloss].label not in acc:
                acc[self.gold_glosses[gloss].label] = {}
            acc[self.gold_glosses[gloss].label][self.ref_glosses[gloss]] = acc[self.gold_glosses[gloss].label].get(
                self.ref_glosses[gloss], 0) + 1

            # If final matches gold_standard set add to correct list
            if self.ref_glosses[gloss] == self.gold_glosses[gloss].label:
                result = 'correct'

            # Set direct evaluation values
            entry = [', '.join(gloss), self.gold_glosses[gloss].label, self.ref_glosses[gloss]]
            if self.gold_glosses[gloss].label == self.ref_glosses[gloss]:
                correct_total += 1
                correct_list += [entry]
            else:
                incorrect_list += [entry]

        # Write results to file
        writer.write('Accuracy: {}\n'.format(correct_total / float(len(self.ref_glosses))))
        writer.write('Total: {}; Correct: {}\n\n'.format(len(self.ref_glosses), correct_total))

        # Write incorrect_list
        writer.write('Incorrect pairs\n')
        for entry in incorrect_list:
            writer.write('{0:56s} Gold: {1:20s} System: {2:20s}\n'.format(*entry))

        # Write correct list
        writer.write('\nCorrect pairs\n')
        for entry in correct_list:
            writer.write('{0:56} Gold: {1:20s} System: {2:20s}\n'.format(*entry))

        # Write accuracy
        file = '{}/{}'.format(path, self.container)
        functions.accuracy(acc, file)

        return True

    def export_references(self, out_path):
        # Set the path for the container reference file
        path = '{}/out/reference/{}/{}'.format(out_path, self.model, self.ctype)
        if self.model == self.container:
            path = '{}/out/reference/{}'.format(out_path, self.model)

        # Set the writer for the container reference file
        if not os.path.isdir(path):
            os.makedirs(path)
        writer = open('{}/{}.ref'.format(path, self.container), 'w')

        for gloss in sorted(self.ref_glosses):
            writer.write('{}\n'.format(','.join([self.model] + list(gloss) + [self.ref_glosses[gloss]])))

        return True
