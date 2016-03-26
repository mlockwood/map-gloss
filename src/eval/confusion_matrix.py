class CM:

    objects = {}

    def __init__(self, gold, test, name):
        self._gold = gold
        self._test = test
        self._name = name
        self._matrix = {'FNeg': {}, 'FPos': {}, 'TPos': {}}
        self.set_confusion()
        self.set_precision()
        self.set_recall()
        self.set_fscore()
        CM.objects[name] = self

    def set_confusion(self):
        for value in self._gold:
            if value in self._test:
                self._matrix['TPos'][value] = True
            else:
                self._matrix['FNeg'][value] = True
        for value in self._test:
            if value not in self._gold:
                self._matrix['FPos'][value] = True
        return True

    def set_precision(self):
        try:
            self._precision = float(len(self._matrix['TPos'])) / (
                len(self._matrix['TPos']) + len(self._matrix['FPos']))
        except:
            self._precision = 0.0
        return True

    def set_recall(self):
        try:
            self._recall = float(len(self._matrix['TPos'])) / (
                len(self._matrix['TPos']) + len(self._matrix['FNeg']))
        except:
            self._recall = 0.0
        return True

    def set_fscore(self):
        try:
            self._fscore = 2 * (self._precision * self._recall / (
                self._precision + self._recall))
        except:
            self._fscore = 0.0
        return True

    def get_final(self):
        return (self._precision, self._recall, self._fscore)

    def write_prf_file(self, file):
        writer = open(file + '.prf', 'w')
        self._write_prf_file(writer)
        writer.close()

    def _write_prf_file(self, writer):
        # Main p/r/f statistics
        writer.write('Precision: ' + str(self._precision) + '\n')
        writer.write('Recall: ' + str(self._recall) + '\n')
        writer.write('F-Score: ' + str(self._fscore) + '\n\n')
        # False negatives and false positives
        if self._matrix['FNeg']:
            writer.write('False Negatives\n')
            for value in self._matrix['FNeg']:
                writer.write('\t' + str(value) + '\n')
            writer.write('\n')
        if self._matrix['FPos']:
            writer.write('False Positives\n')
            for value in self._matrix['FPos']:
                writer.write('\t' + str(value) + '\n')
            writer.write('\n')
        return True

    def write_hprf_file(self, file):
        writer = open(file + '.hprf', 'w')
        self._write_hprf_file(writer)
        writer.close()

    def _write_hprf_file(self, writer):
        writer.write('Gold Values\n')
        for value in self._gold:
            writer.write('G\t' + str(value) + '\n')
        writer.write('\nTest Values\n')
        for value in self._test:
            writer.write('T\t' + str(value) + '\n')
        return True

class Compare:

    objects = {} # (cm1, cm2)

    def __init__(self, cm1, cm2):
        self._cm1 = cm1
        self._cm2 = cm2
        self._matrix = {'TP2FN': {}, 'NO2FP': {}, 'FN2TP': {}, 'FP2NO': {}}
        self.set_comparison_matrix()
        self.compare_precision()
        self.compare_recall()
        self.compare_fscore()
        Compare.objects[(cm1, cm2)] = self

    def set_comparison_matrix(self):
        for value in CM.objects[self._cm2]._matrix['TPos']:
            if value not in CM.objects[self._cm1]._matrix['TPos']:
                self._matrix['TP2FN'][value] = True
        for value in CM.objects[self._cm1]._matrix['FPos']:
            if value not in CM.objects[self._cm2]._matrix['FPos']:
                self._matrix['NO2FP'][value] = True
        for value in CM.objects[self._cm2]._matrix['FNeg']:
            if value not in CM.objects[self._cm1]._matrix['FNeg']:
                self._matrix['FN2TP'][value] = True
        for value in CM.objects[self._cm2]._matrix['FPos']:
            if value not in CM.objects[self._cm1]._matrix['FPos']:
                self._matrix['FP2NO'][value] = True
        return True

    def compare_precision(self):
        self._abs_precision = (CM.objects[self._cm1]._precision -
                               CM.objects[self._cm2]._precision)
        try:
            self._rel_precision = (CM.objects[self._cm1]._precision /
                                   CM.objects[self._cm2]._precision)
        except:
            self._rel_precision = 0.0
        return True

    def compare_recall(self):
        self._abs_recall = (CM.objects[self._cm1]._recall -
                            CM.objects[self._cm2]._recall)
        try:
            self._rel_recall = (CM.objects[self._cm1]._recall /
                                CM.objects[self._cm2]._recall)
        except:
            self._rel_recall = 0.0
        return True

    def compare_fscore(self):
        self._abs_fscore = (CM.objects[self._cm1]._fscore -
                            CM.objects[self._cm2]._fscore)
        try:
            self._rel_fscore = (CM.objects[self._cm1]._fscore /
                                CM.objects[self._cm2]._fscore)
        except:
            self._rel_fscore = 0.0
        return True

    def write_cprf_file(self, file):
        writer = open(file + '.cprf', 'w')
        self._write_cprf_file(writer)
        writer.write('\n\n--- ' + str(self._cm1) + ' ---\n\n')
        CM.objects[self._cm1]._write_prf_file(writer)
        writer.write('\n\n--- ' + str(self._cm2) + ' ---\n\n')
        CM.objects[self._cm2]._write_prf_file(writer)
        writer.close()
        return True

    def _write_cprf_file(self, writer):
        # Main p/r/f abs statistics
        writer.write('Absolute Change\n')
        writer.write('Precision: ' + str(self._abs_precision) + '\n')
        writer.write('Recall: ' + str(self._abs_recall) + '\n')
        writer.write('F-Score: ' + str(self._abs_fscore) + '\n\n')
        # Main p/r/f rel statistics
        writer.write('Relative Change\n')
        writer.write('Precision: ' + str(self._rel_precision) + '\n')
        writer.write('Recall: ' + str(self._rel_recall) + '\n')
        writer.write('F-Score: ' + str(self._rel_fscore) + '\n\n')
        # False negatives and false positives
        if self._matrix['TP2FN']:
            writer.write('True Positives to False Negatives\n')
            for value in self._matrix['TP2FN']:
                writer.write('\t' + str(value) + '\n')
            writer.write('\n')
        if self._matrix['NO2FP']:
            writer.write('False Positives Added\n')
            for value in self._matrix['NO2FP']:
                writer.write('\t' + str(value) + '\n')
            writer.write('\n')
        if self._matrix['FN2TP']:
            writer.write('False Negatives to True Positives\n')
            for value in self._matrix['FN2TP']:
                writer.write('\t' + str(value) + '\n')
            writer.write('\n')
        if self._matrix['FP2NO']:
            writer.write('False Positives Removed\n')
            for value in self._matrix['FP2NO']:
                writer.write('\t' + str(value) + '\n')
            writer.write('\n')
        return True

