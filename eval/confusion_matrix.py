#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'eval/confusion_matrix.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class CM:

    objects = {}

    def __init__(self, gold, test, name):
        self.gold = gold
        self.test = test
        self.name = name
        self.matrix = {'FNeg': {}, 'FPos': {}, 'TPos': {}}
        self.set_confusion()
        self.precision = self.set_precision()
        self.recall = self.set_recall()
        self.fscore = self.set_fscore()
        CM.objects[name] = self

    def __repr__(self):
        return '<CM object with name {}>'.format(self.name)

    def set_confusion(self):
        for label in self.gold:
            if label in self.test:
                self.matrix['TPos'][label] = True
            else:
                self.matrix['FNeg'][label] = True
        for label in self.test:
            if label not in self.gold:
                self.matrix['FPos'][label] = True
        return True

    def set_precision(self):
        try:
            precision = float(len(self.matrix['TPos'])) / (len(self.matrix['TPos']) + len(self.matrix['FPos']))
        except:
            precision = 0.0
        return precision

    def set_recall(self):
        try:
            recall = float(len(self.matrix['TPos'])) / (len(self.matrix['TPos']) + len(self.matrix['FNeg']))
        except:
            recall = 0.0
        return recall

    def set_fscore(self):
        try:
            fscore = 2 * (self.precision * self.recall / (self.precision + self.recall))
        except:
            fscore = 0.0
        return fscore

    def get_final(self):
        return self.precision, self.recall, self.fscore

    def write_prf_file(self, file):
        writer = open(file + '.prf', 'w')
        self.set_prf_file(writer)
        writer.close()

    def set_prf_file(self, writer):
        # Main p/r/f statistics
        writer.write('Precision: {}\n'.format(self.precision))
        writer.write('Recall: {}\n'.format(self.recall))
        writer.write('F-Score: {}\n\n'.format(self.fscore))
        
        # False negatives
        if self.matrix['FNeg']:
            writer.write('False Negatives\n')
            for value in self.matrix['FNeg']:
                writer.write('\t{}\n'.format(value))
            writer.write('\n')
        
        # False positives
        if self.matrix['FPos']:
            writer.write('False Positives\n')
            for value in self.matrix['FPos']:
                writer.write('\t{}\n'.format(value))
            writer.write('\n')
        return True

    def write_hprf_file(self, file):
        writer = open(file + '.hprf', 'w')
        self.set_hprf_file(writer)
        writer.close()

    def set_hprf_file(self, writer):
        # Gold labels
        writer.write('Gold Labels\n')
        for value in self.gold:
            writer.write('G\t{}\n'.format(value))
        
        # Test labels
        writer.write('\nTest Labels\n')
        for value in self.test:
            writer.write('T\t{}\n'.format(value))
        return True


class Compare:

    objects = {}  # (cm1, cm2)
    order = ['TP2FN', 'NO2FP', 'FN2TP', 'FP2NO']
    headers = {'TP2FN': 'True Positives to False Negatives',
               'NO2FP': 'False Positives Added',
               'FN2TP': 'False Negatives to True Positives',
               'FP2NO': 'False Positives Removed'}

    def __init__(self, cm1, cm2):
        self.cm1 = cm1
        self.cm2 = cm2
        self.matrix = {'TP2FN': {}, 'NO2FP': {}, 'FN2TP': {}, 'FP2NO': {}}
        self.set_comparison_matrix()
        self.abs_precision = self.set_abs_precision()
        self.rel_precision = self.set_rel_precision()
        self.abs_recall = self.set_abs_recall()
        self.rel_recall = self.set_rel_recall()
        self.abs_fscore = self.set_abs_fscore()
        self.rel_fscore = self.set_rel_fscore()
        Compare.objects[(cm1.name, cm2.name)] = self

    def __repr__(self):
        return '<Compare object with names {} and {}>'.format(self.cm1.name, self.cm2.name)

    def set_comparison_matrix(self):
        for label in self.cm2.matrix['TPos']:
            if label not in self.cm1.matrix['TPos']:
                self.matrix['TP2FN'][label] = True
        for label in self.cm1.matrix['FPos']:
            if label not in self.cm2.matrix['FPos']:
                self.matrix['NO2FP'][label] = True
        for label in self.cm2.matrix['FNeg']:
            if label not in self.cm1.matrix['FNeg']:
                self.matrix['FN2TP'][label] = True
        for label in self.cm2.matrix['FPos']:
            if label not in self.cm1.matrix['FPos']:
                self.matrix['FP2NO'][label] = True
        return True
    
    def set_abs_precision(self):
        return self.cm1.precision - self.cm2.precision

    def set_rel_precision(self):
        try:
            rel_precision = self.cm1.precision / self.cm2.precision
        except:
            rel_precision = 0.0
        return rel_precision
    
    def set_abs_recall(self):
        return self.cm1.recall - self.cm2.recall

    def set_rel_recall(self):
        try:
            rel_recall = self.cm1.recall / self.cm2.recall
        except:
            rel_recall = 0.0
        return rel_recall
    
    def set_abs_fscore(self):
        return self.cm1.fscore - self.cm2.fscore

    def set_rel_fscore(self):
        try:
            rel_fscore = self.cm1.fscore / self.cm2.fscore
        except:
            rel_fscore = 0.0
        return rel_fscore

    def write_cprf_file(self, file):
        writer = open(file + '.cprf', 'w')
        self.set_cprf_file(writer)
        
        # Write PRF file of the first confusion matrix
        writer.write('\n\n--- {} ---\n\n'.format(self.cm1.name))
        self.cm1.set_prf_file(writer)
        
        # Write PRF file of the second confusion matrix
        writer.write('\n\n--- {} ---\n\n'.format(self.cm2.name))
        self.cm2.set_prf_file(writer)
        
        writer.close()
        return True

    def set_cprf_file(self, writer):
        # Main p/r/f abs statistics
        writer.write('Absolute Change\n')
        writer.write('Precision: {}\n'.format(self.abs_precision))
        writer.write('Recall: {}\n'.format(self.abs_recall))
        writer.write('F-Score: {}\n\n'.format(self.abs_fscore))
        
        # Main p/r/f rel statistics
        writer.write('Relative Change\n')
        writer.write('Precision: {}\n'.format(self.rel_precision))
        writer.write('Recall: {}\n'.format(self.rel_recall))
        writer.write('F-Score: {}\n\n'.format(self.rel_fscore))
        
        # False negatives and false positives
        for entry in Compare.order:
            if self.matrix[entry]:
                writer.write('{}\n'.format(Compare.headers[entry]))
                for value in self.matrix[entry]:
                    writer.write('\t{}\n'.format(value))
                writer.write('\n')
        return True
