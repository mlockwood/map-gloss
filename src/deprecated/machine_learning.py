#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__program__ = models.py
__author__ = MichaelLockwood
__projecttopic__ = AGGREGATION Inferrence
__projectname__ = Mapping Input Glosses to Standard Outputs
__date__ = September2015
__credits__ = None
__collaborators__ = None
"""

import inspect
import re
import sys
import types


"""
Import packages and scripts---------------------------------------------
"""
import pickle
import math
import os

# Import scripts
from src.utils import functions


class Model:

    objects = {}
    ID_generator = 1
    models = ['kNN', 'MaxEnt', 'NB', 'TBL']
    standard = {}

    def __init__(self, training, run_kNN, run_MaxEnt, run_NB, run_TBL, ID=''):
        self._training = training
        self._run_kNN = run_kNN
        self._run_MaxEnt = run_MaxEnt
        self._run_NB = run_NB
        self._run_TBL = run_TBL
        # Manage models ID
        if ID:
            self._ID = ID
        if not ID:
            self._ID = hex(Model.ID_generator)
            Model.ID_generator += 1
        self._results = {}
        Model.objects[self._ID] = self

    def load():
        """Load a CLSO file containing all DS.
        """
        try:
            reader = CLSO('models', option='r')
            reader.load()
            return True
        except:
            print('Error loading models.clso')
            Model.objects = {}
            return False

    def load_standard_glosses():
        reader = open('standard_grams', 'r')
        for row in reader:
            if row[0] == '#':
                continue
            line = row.rstrip('\n')
            line = line.lower()
            line = re.sub(' ', '', line)
            line = line.split(',')
            # Send standard glosses to Model.standard
            Model.standard[line[0].lower()] = True
            Model.standard[line[1].lower()] = True
        reader.close()
        return True

    def export():
        """Export a CLSO file containing all relevant DS.
        """
        writer = CLSO('models', option='w')
        writer.bulk_dump('Model')
        writer.bulk_dump('kNN')
        writer.bulk_dump('MaxEnt')
        writer.bulk_dump('NB')
        writer.bulk_dump('TBL')
        writer.close()
        return True

    def model_cleanup():
        for obj in Model.objects:
            Model.objects[obj]._results = {}
            Model.objects[obj]._training = []
        for model in Model.models:
            exec(model + '.model_cleanup()')
        return True

    def train(self):
        if self._run_kNN:
            self._kNN = kNN(self._training)
            self._kNN = self._kNN._ID
        if self._run_MaxEnt:
            self._MaxEnt = MaxEnt(self._training)
            self._MaxEnt.train()
            self._MaxEnt = self._MaxEnt._ID
        if self._run_NB:
            self._NB = NB(self._training)
            self._NB.train1()
            self._NB.train2()
            self._NB.train3()
            self._NB = self._NB._ID
        if self._run_TBL:
            self._TBL = TBL(self._training)
            self._TBL.initialize()
            self._TBL.train()
            self._TBL = self._TBL._ID
        self._object_links = False
        Model.model_cleanup() # all results should be already empty, precaution
        Model.export()

    def reconstruct_object_links(self):
        for model in Model.models:
            if eval('self._run_' + model + ' and self._run_' + model +
                    ' != \'False\''):
                exec('self._' + model + ' = ' + model + '.objects[hex(self._' +
                     model + ')]')
                if model == 'MaxEnt':
                    self._MaxEnt._classifier = pickle.load(
                        mod._MaxEnt._maxent_file)
        self._object_links = True
        return True

    def test_models(self, vectors, collection):
        if not self._object_links:
            self.reconstruct_object_links()
        for model in Model.models:
            if eval('self._run_' + model + ' and self._run_' + model +
                    ' != \'False\''):
                eval('self._' + model + '.test(vectors, collection)')
        self.set_results()
        return True

    def set_results(self):
        for model in Model.models:
            if eval('self._run_' + model + ' and self._run_' + model +
                    ' != \'False\''):
                for value in eval('self._' + model + '._results'):
                    if value not in self._results:
                        self._results[value] = {}
                    exec('self._results[value][\'' + model +
                         '\'] = copy.deepcopy(self._' + model +
                         '._results[value])')
        return True


class kNN:

    objects = {} # ID
    ID_generator = 1

    def __init__(self, training, ID=''):
        self._training = training
        # Manage kNN ID
        if ID:
            self._ID = ID
        if not ID:
            self._ID = hex(kNN.ID_generator)
            kNN.ID_generator += 1
        self._results = {}
        kNN.objects[self._ID] = self


    def model_cleanup():
        for obj in kNN.objects:
            kNN.objects[obj]._results = {}
        return True

    def get_ID(self):
        return self._ID

    # System function
    def system(self, syst, collection, method):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        writer = open('machine_learning/kNN_' + method + '_' +
                      collection + '.sys', 'w')
        writer.write('%%%%% '+str(collection)+' data:\n')
        for line in syst:
            output = 'array:'+str(line[0])+' '+str(line[1])
            # Write out probabilities
            for item in line[2]:
                output += ' '+str(item[1])+' '+str(item[0])
            output += '\n'
            writer.write(output)
        writer.close()
        return True

    # Accuracy function
    def accuracy(self, acc, collection, method):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        file = 'machine_learning/kNN_' + method + '_' + collection
        functions.accuracy(acc, file)
        return True

    @staticmethod
    def cosine_denominator(D):
        denominator = 0.0
        for value in D:
            try:
                denominator += float(D[value])
            except:
                pass
        return denominator ** 0.5

    # Function for selecting from the k best neighbors
    @staticmethod
    def knn_accept(kNN, curK, reverse=False):
        accept_D = {}
        accept_L = []
        # Sort the features by distance
        kNN = sorted(kNN)
        # If reverse is F select k closest to point, if T select k closest to 1
        if reverse == False:
            accept = kNN[:curK]
        else:
            accept = kNN[-curK:]
        # Of k selected features, add up the total per label
        for a in accept:
            accept_D[a[1]] = accept_D.get(a[1], 0) + 1
        # Convert the above to a list format with tuples (count, label)
        for key in accept_D:
            accept_L.append((accept_D[key], key))
        # Sort accept_L so that the end has the maximum count/probability
        accept_L = sorted(accept_L)
        # If the list has len > 1, check for a tie
        if len(accept_L) > 1:
            # If they are tied check the next nearest neighbor for a tiebreaker
            if accept_L[-1][0] == accept_L[-2][0]:
                return knn_accept(kNN, curK+1, reverse)
        # When there is no tie, return the probabilities or the current k
        # neighbors
        syst_list = []
        for a in accept_L:
            syst_list.append((float(a[0])/curK, a[1]))
        return syst_list

    # Function for testing with euclidean distance
    def test(self, vectors, collection, k=10, method='cosine'):
        syst = []
        acc = {}
        # Set cosine values on training values
        for train in self._training:
            train._cosine = kNN.cosine_denominator(train._features)
        # For each testing instance
        for vector in vectors:
            vector._cosine = kNN.cosine_denominator(vector._features)
            kNN_distances = []
            # For each training instance
            for train in self._training:
                dist = 0.0
                # For the features in the testing instance
                for feat in vector._features:
                    # If method is cosine
                    if method == 'cosine':
                        # If that feature is in the training instance, add the
                        # product of their locations
                        if feat in train._features:
                            dist += (vector._features[feat] *
                                     train._vectors[feat])
                    # If method is euclidean
                    elif method == 'euclidean':
                        # If that feature is the training instance, add the
                        # squared distance between the two
                        if feat in train._features:
                            dist += (vector._features[feat] -
                                     train._features[feat])**2
                        # Else add the squared distances from the origin
                        else:
                            dist += (vector._features[feat])**2
                    # Send error for unknown method
                    else:
                        raise ValueError('kNN method of ' + str(method) +
                                         ' is unknown.')
                # Normalize cosine values by their denominator values
                if method == 'cosine':
                    dist = dist/(vector._cosine * train._vector)
                # If we want to follow the correct formula we would take the
                # square root of the euclidean distance, doing so does not
                # impact results and adds to computation so it is ignored
                kNN_distances.append((dist, train._standard))
            # Call the function to sort probabilities and most likely value
            if method == 'cosine':
                syst_list = kNN.knn_accept(kNN_distances, k, reverse=True)
            elif method == 'euclidean':
                syst_list = kNN.knn_accept(kNN_distances, k)
            syst.append([vector._standard, syst_list])
            # Handle the accuracies
            kNN_label = syst_list[-1][1]
            if vector._standard not in acc:
                acc[vector._standard] = {}
            acc[vector._standard][kNN_label] = acc[vector._standard].get(
                kNN_label, 0) + 1
        # Call system and accuracy functions
        self.system(syst, collection, method)
        self.accuracy(acc, collection, method)
        return True


class MaxEnt:

    objects = {} # ID
    ID_generator = 1

    def __init__(self, training, ID=''):
        self._training = training
        # Manage MaxEnt ID
        if ID:
            self._ID = ID
        if not ID:
            self._ID = hex(MaxEnt.ID_generator)
            MaxEnt.ID_generator += 1
        self._results = {}
        MaxEnt.objects[self._ID] = self


    def model_cleanup():
        for obj in MaxEnt.objects:
            MaxEnt.objects[obj]._results = {}
        return True

    def get_ID(self):
        return self._ID

    # Accuracy function
    def accuracy(self, acc, collection, number):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        file = 'machine_learning/max_ent' + number + '_' + collection
        functions.accuracy(acc, file)
        return True

    def train(self):
        try:
            from nltk.classify import maxent
        except:
            raise IOError('NLTK not found. The MaxEnt option requires the NLTK'
                          + ' package. Please install or set MaxEnt to False')
        train_input = []
        for vector in self._training:
            train_input.append((vector._features, vector._standard))
        encoding = maxent.TypedMaxentFeatureEncoding.train(train_input,
            alwayson_features=True)
        self._classifier = maxent.MaxentClassifier.train(train_input,
            bernoulli=False, encoding=encoding, trace=0)
        self._maxent_file = 'maxent_classifier_' + str(self._ID) + '.pickle'
        maxent_file = open(self._maxent_file, 'w')
        pickle.dump(self._classifier, maxent_file, -1)
        maxent_file.close()
        return True

    def test(self, vectors, collection):
        try:
            from nltk.classify import maxent
        except:
            raise IOError('NLTK not found. The MaxEnt option requires the NLTK'
                          + ' package. Please install or set MaxEnt to False')
        test_input = []
        for vector in vectors:
            test_input.append(vector._features)
        decoded = self._classifier.classify_many(test_input)
        results_list = zip(vectors, decoded)
        for result in results_list:
            vector = result[0]
            # Add to results
            gloss = (vector._dataset, vector._iso, vector._gloss)
            if gloss not in self._results:
                self._results[gloss] = {}
            self._results[gloss][result[1]] = self._results[gloss].get(
                result[1], 0) + 1
            # Add to acc
            if vector._standard not in acc:
                acc[vector._standard] = {}
            acc[vector._standard][result[1]] = acc[vector._standard].get(
                result[1], 0) + 1
        return True


class NB:

    objects = {} # ID
    ID_generator = 1
    c_delta = 0
    delta = 1.0

    def __init__(self, training, ID=''):
        self._training = training
        # Manage NB ID
        if ID:
            self._ID = ID
        if not ID:
            self._ID = hex(NB.ID_generator)
            NB.ID_generator += 1
        self._results1 = {}
        self._results2 = {}
        self._results3 = {}
        self._results = {}
        NB.objects[self._ID] = self

    def model_cleanup():
        for obj in NB.objects:
            NB.objects[obj]._results = {}
            NB.objects[obj]._results1 = {}
            NB.objects[obj]._results2 = {}
            NB.objects[obj]._results3 = {}
        return True

    def get_ID(self):
        return self._ID

    # Model function
    def model(self, distr, mod, number):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        writer = open('machine_learning/naive_bayes' + number + '.mod', 'w')
        writer.write('%%%%% prior prob P(c) %%%%%\n')
        for L in distr:
            writer.write(str(L)+'\t'+str(10**distr[L])+'\t'+str(distr[L])+'\n')
        writer.write('%%%%% conditional prob P(f|c) %%%%%\n')
        for L in mod:
            writer.write('%%%%% conditional prob P(f|c) c='+str(L)+' %%%%%\n')
            for feat in mod[L]:
                if number == '1':
                    writer.write(str(feat) + '\t' + str(L) + '\t' +
                        str(10**mod[L][feat][1]) + '\t' + str(mod[L][feat][1])
                        + '\n')
                else:
                    writer.write(str(feat) + '\t' + str(L) + '\t' +
                        str(10**mod[L][feat]) + '\t' + str(mod[L][feat]) +
                        '\n')
        writer.close()
        return True

    # System function
    def system(self, syst, collection, number):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        writer = open('machine_learning/naive_bayes' + number + '_' +
                      collection + '.sys', 'w')
        writer.write('%%%%% '+str(collection)+' data:\n')
        for line in syst:
            output = 'array:'+str(line[0])+' '+str(line[1])
            lgmin = min(line[2])[0]
            denom = 0.0
            # Convert probabilities
            for item in line[2]:
                denom += item[0]-lgmin
            for item in line[2]:
                output += ' '+str(item[1])+' '+str((item[0]-lgmin)/denom)
            output += '\n'
            writer.write(output)
        writer.close()
        return True

    # Accuracy function
    def accuracy(self, acc, collection, number):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        file = 'machine_learning/naive_bayes' + number + '_' + collection
        functions.accuracy(acc, file)
        return True

    # train1 and test1 apply the multivariate Bernolli models of Naive Bayes
    def train1(self):
        distr = {} # Store the distribution of the labels
        unknown = {} # Store the lgprob for unseen testing values
        pwk = 0.0 # Store Pi_w_k, all null/0 values of every word_k
        mod = {} # Store the trained NB models
        # Store the count of all features by label across all instances
        for vector in self._training:
            # Increment label count
            distr[vector._standard] = distr.get(vector._standard, 0) + 1
            if vector._standard not in mod:
                mod[vector._standard] = {}
            for feat in vector._features:
                if feat not in mod[vector._standard]:
                    mod[vector._standard][feat] = {}
                mod[vector._standard][feat][1] = mod[vector._standard][feat
                    ].get(1, 0) + 1
        # Convert counts to lgprob values
        distr_sum = 0.0
        for L in distr:
            distr_sum += distr[L] + NB.c_delta
        for L in mod:
            unknown[L] = math.log((float(NB.delta) / (float(
                NB.delta)*2 + distr[L])), 10)
            for feat in mod[L]:
                mod[L][feat][1] = (mod[L][feat].get(1, 0) + NB.delta)/(
                    float(NB.delta) * 2 + distr[L])
                mod[L][feat][0] = math.log(1 - mod[L][feat][1], 10)
                mod[L][feat][1] = math.log(mod[L][feat].get(1, 0), 10)
                pwk += mod[L][feat][0]
            distr[L] = math.log(((distr.get(L, 0) + NB.c_delta) /
                                 distr_sum), 10)
        self._distr1 = distr
        self._unknown1 = unknown
        self._pwk1 = pwk
        self._mod1 = mod
        #self.models(distr, mod, '1')
        return self._ID

    def test1(self, vectors, collection):
        n = 0
        syst = []
        acc = {}
        # For each instance, start with prob = lbprob(class) then add for each
        # feat
        for vector in vectors:
            C = []
            for L in self._mod1:
                prob = self._distr1[L] + self._pwk1
                for feat in vector._features:
                    # If feature in training, add lg(p(f|c)) - lg(1-p(f|c))
                    if feat in self._mod1[L]:
                        prob += self._mod1[L][feat][1] - self._mod1[L][feat][0]
                    else:
                        prob += self._unknown1[L]
                C.append((prob, L))
            # Store all results as tuples then select the maximum
            syst.append([n, vector._standard, C])
            n += 1
            NB_label = max(C)[1]
            # Add to acc
            if vector._standard not in acc:
                acc[vector._standard] = {}
            acc[vector._standard][NB_label] = acc[vector._standard].get(
                NB_label, 0) + 1
            # Add to results
            gloss = (vector._dataset, vector._iso, vector._gloss)
            if gloss not in self._results1:
                self._results1[gloss] = {}
            self._results1[gloss][NB_label] = self._results1[gloss].get(
                NB_label, 0) + 1
        # Call system and accuracy functions
        #self.system(syst, collection, '1')
        self.accuracy(acc, collection, '1')
        return True

    # train2 and test2 apply the multinomial non-binary models of Naive Bayes
    def train2(self):
        distr = {} # Store the distribution of the labels
        unknown = {} # Store the lgprob for unseen testing values
        Vsum = {} # Count total features by label
        mod = {} # Store the trained NB models
        # Store the count of all features by label across all instances
        for vector in self._training:
            # Increment label count
            distr[vector._standard] = distr.get(vector._standard, 0) + 1
            if vector._standard not in mod:
                mod[vector._standard] = {}
            for feat in vector._features:
                mod[vector._standard][feat] = mod[vector._standard].get(feat,
                    0) + vector._features[feat]
                Vsum[vector._standard] = Vsum.get(vector._standard, 0
                    ) + vector._features[feat]
        # Convert counts to lgprob values
        distr_sum = 0.0
        for L in distr:
            distr_sum += distr[L] + NB.c_delta
        for L in mod:
            distr[L] = math.log(((distr.get(L, 0) + NB.c_delta) /
                                 distr_sum), 10)
            unknown[L] = math.log(((float(NB.delta)) / ((len(mod[L]) *
                                    float(NB.delta)) + Vsum[L])), 10)
            for feat in mod[L]:
                mod[L][feat] = math.log(((mod[L].get(feat, 0) +
                    float(NB.delta))/(len(mod[L]) *
                    float(NB.delta) + Vsum[L])), 10)
        self._distr2 = distr
        self._unknown2 = unknown
        self._mod2 = mod
        #self.models(distr, mod, '2')
        return self._ID

    def test2(self, vectors, collection):
        n = 0
        syst = []
        acc = {}
        # For each instance, start with prob = lbprob(class) then add for each
        # feat
        for vector in vectors:
            C = []
            for L in self._mod2:
                prob = self._distr2[L]
                for feat in vector._features:
                    # If feature in training, add lg(p(f|c)) * frequency
                    if feat in self._mod2[L]:
                        prob += vector._features[feat] * self._mod2[L][feat]
                    else:
                        prob += vector._features[feat] * self._unknown2[L]
                C.append((prob, L))
            # Store all results as tuples then select the maximum
            syst.append([n, vector._standard, C])
            n += 1
            NB_label = max(C)[1]
            # Add to acc
            if vector._standard not in acc:
                acc[vector._standard] = {}
            acc[vector._standard][NB_label] = acc[vector._standard].get(
                NB_label, 0) + 1
            # Add to results
            gloss = (vector._dataset, vector._iso, vector._gloss)
            if gloss not in self._results2:
                self._results2[gloss] = {}
            self._results2[gloss][NB_label] = self._results2[gloss].get(
                NB_label, 0) + 1
        # Call system and accuracy functions
        #self.system(syst, collection, '2')
        self.accuracy(acc, collection, '2')
        return True

    # train3 and test3 apply the multinomial (use-binary) models of Naive Bayes
    def train3(self):
        distr = {} # Store the distribution of the labels
        unknown = {} # Store the lgprob for unseen testing values
        Vsum = {} # Count total words by label
        mod = {} # Store the trained NB models
        # Store the count of all features by label across all instances
        for vector in self._training:
            # Increment label count
            distr[vector._standard] = distr.get(vector._standard, 0) + 1
            if vector._standard not in mod:
                mod[vector._standard] = {}
            for feat in vector._features:
                mod[vector._standard][feat] = mod[vector._standard].get(
                    feat, 0) + 1
                Vsum[vector._standard] = Vsum.get(vector._standard, 0) + 1
        # Convert counts to lgprob values
        distr_sum = 0.0
        for L in distr:
            distr_sum += distr[L] + NB.c_delta
        for L in mod:
            distr[L] = math.log(((distr.get(L, 0) + NB.c_delta)/
                                 distr_sum), 10)
            unknown[L] = math.log(((float(NB.delta))/(
                (len(mod[L]) * float(NB.delta))+ Vsum[L])), 10)
            for feat in mod[L]:
                mod[L][feat] = math.log(((mod[L].get(feat, 0) + NB.delta
                    )/(len(mod[L]) * float(NB.delta) + Vsum[L])), 10)
        self._distr3 = distr
        self._unknown3 = unknown
        self._mod3 = mod
        #self.models(distr, mod, '3')
        return self._ID

    def test3(self, vectors, collection):
        n = 0
        syst = []
        acc = {}
        for L in self._mod3:
            acc[L] = {}
        # For each instance, start with prob = lbprob(class) then add for each
        # feat
        for vector in vectors:
            C = []
            for L in self._mod3:
                prob = self._distr3[L]
                for feat in vector._features:
                    # If feature in training, add lg(p(f|c)) * frequency
                    if feat in self._mod3[L]:
                        prob += self._mod3[L][feat]
                    else:
                        prob += self._unknown3[L]
                C.append((prob, L))
            # Store all results as tuples then select the maximum
            syst.append([n, vector._standard, C])
            n += 1
            NB_label = max(C)[1]
            # Add to acc
            if vector._standard not in acc:
                acc[vector._standard] = {}
            acc[vector._standard][NB_label] = acc[vector._standard].get(
                NB_label, 0) + 1
            # Add to results
            gloss = (vector._dataset, vector._iso, vector._gloss)
            if gloss not in self._results3:
                self._results3[gloss] = {}
            self._results3[gloss][NB_label] = self._results3[gloss].get(
                NB_label, 0) + 1
        # Call system and accuracy functions
        #self.system(syst, collection, '3')
        self.accuracy(acc, collection, '3')
        return True

    def set_results(self):
        for gloss in self._results1:
            self._results[gloss] = {}
            for out1 in self._results1[gloss]:
                self._results[gloss][out1] = self._results1[gloss][out1]
            """
            for out2 in self._results2[gloss]:
                self._results[gloss][out2] = self._results[gloss].get(out2, 0
                    ) + self._results2[gloss][out2]
            for out3 in self._results3[gloss]:
                self._results[gloss][out3] = self._results[gloss].get(out3, 0
                    ) + self._results3[gloss][out3]
            """
            self._results[gloss] = functions.probD_conversion(
                self._results.get(gloss, 0))
        return True

    def test(self, vectors, collection):
        self.test1(vectors, collection)
        self.test2(vectors, collection)
        self.test3(vectors, collection)
        self.set_results()
        return True

class TBL:

    objects = {} # ID
    ID_generator = 1
    default = 'word'

    def __init__(self, training, ID=''):
        self._training = TBL.format_vectors(training)
        self._min_gain = 1
        # Manage TBL ID
        if ID:
            self._ID = ID
        if not ID:
            self._ID = hex(TBL.ID_generator)
            TBL.ID_generator += 1
        self._results = {}
        TBL.objects[self._ID] = self

    def model_cleanup():
        for obj in TBL.objects:
            TBL.objects[obj]._results = {}
        return True

    def get_ID(self):
        return self._ID

    # Model function
    def model(self):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        writer = open('machine_learning/tbl.mod', 'w')
        writer.write(TBL.default+'\n')
        for rule in self._tbl_rules:
            writer.write(str(rule[0])+' '+str(rule[1])+' '+str(rule[2])+' '+
                          str(rule[3])+'\n')
        writer.close()
        return True

    # System function
    def system(self, syst, collection):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        writer = open('machine_learning/tbl_' +
                      collection + '.sys', 'w')
        writer.write('%%%%% ' + collection + ' data:\n')
        for line in syst:
            output = 'array:'+str(line[0])+' '+str(line[1])+' '+str(line[2])
            # Write out probabilities
            for item in line[3]:
                output += ' '+str(item)
            output += '\n'
            writer.write(output)
        writer.close()
        return True

    # Accuracy function
    def accuracy(self, acc, collection):
        if not os.path.exists(os.getcwd() + '/machine_learning'):
            os.mkdir(os.getcwd() + '/machine_learning')
        file = 'machine_learning/tbl_' + collection
        functions.accuracy(acc, file)
        return True

    # Function to format vector IDs
    @staticmethod
    def format_vectors(vectors):
        vector_ID = 1
        ID_vectors = {}
        for vector in vectors:
            ID_vectors[hex(vector_ID)] = vector
            vector_ID += 1
        return ID_vectors

    @staticmethod
    def set_default(gloss):
        if gloss in Model.standard:
            return gloss
        else:
            return TBL.default

    # Function to set the initial TBL map that matches indices, labels, and
    # feats
    def initialize(self):
        tbl = {}
        # Read each vector ID (VID)
        for VID in self._training:
            vector = self._training[VID]
            vector._tbl_cur = TBL.set_default(vector._gloss)
            # For each feat in the instance's features
            for feat in vector._features:
                # Set internal dictionaries if key unseen
                if feat not in tbl:
                    tbl[feat] = {}
                if vector._tbl_cur not in tbl[feat]:
                    tbl[feat][vector._tbl_cur] = {}
                if vector._standard not in tbl[feat][vector._tbl_cur]:
                    tbl[feat][vector._tbl_cur][vector._standard] = {}
                # Set tbl[feat][cur][gold][ID] = True
                tbl[feat][vector._tbl_cur][vector._standard][VID] = True
        self._tbl = tbl
        return True

    # Function to train TBL
    def train(self):
        tbl_rules = []
        gain = self._min_gain
        # Stop rule creation when gain falls below the minimum gain threshold
        while gain >= self._min_gain:
            gain = 0
            best = (True, True, True, 0)
            # For each feat in TBL
            for feat in self._tbl:
                # For each current label
                for cur in self._tbl[feat]:
                    # For each gold label
                    for gold in self._tbl[feat][cur]:
                        # If gold label does not equal current label
                        if gold != cur:
                            # If gain of gold in cur label and feat less loss
                            # of cur in gold label is > best gain, make it new
                            # best
                            positive = len(self._tbl[feat][cur][gold])
                            try:
                                negative = len(self._tbl[feat][cur][cur])
                            except:
                                negative = 0
                            if (positive - negative) > gain:
                                gain = positive - negative
                                best = (feat, cur, gold, gain)
            # Test if gain was 0
            if best == (True, True, True, 0):
                break
            # Changed location of indices based on accepted transformation rule
            for label in self._tbl[best[0]][best[1]].keys():
                # Critical to use .keys() here, otherwise deletion won't work
                for VID in list(self._tbl[best[0]][best[1]][label].keys()):
                    vector = self._training[VID]
                    # Update each for each vector and then update the vector's
                    # cur
                    for feat in vector._features.keys():
                        # Delete previous cur state and instantiate new cur
                        # state
                        del self._tbl[feat][vector._tbl_cur][vector._standard][
                            VID]
                        if best[2] not in self._tbl[feat]:
                            self._tbl[feat][best[2]] = {}
                        if vector._standard not in self._tbl[feat][best[2]]:
                            self._tbl[feat][best[2]][vector._standard] = {}
                        self._tbl[feat][best[2]][vector._standard][VID] = True
                    vector._tbl_cur = best[2]
            # Add best rule to TBL rule set
            tbl_rules.append(best)
        # Once all rules have been created send them to output
        self._tbl_rules = tbl_rules
        self.model()
        return True

    # Function to decode test vectors
    def decode(self, vectors, collection):
        n = 0
        syst = []
        acc = {}
        # For each instance in vectors
        for vector in vectors:
            # Set default class
            vector._tbl_cur = TBL.set_default(vector._gloss)
            # Transformation list for system output
            transformations = []
            # For each transformation rule in order
            for rule in self._tbl_rules:
                # If rule feature is in instance's features
                if rule[0] in vector._features:
                    # If from class equals instance's current class
                    if rule[1] == vector._tbl_cur:
                        # Set instance's current class to the to class of the
                        # rule
                        vector._tbl_cur = rule[2]
                        transformations.append(rule)
            # Prepare for outputs
            syst.append((n, vector._standard, vector._tbl_cur,
                         transformations))
            n += 1
            # Send result to confusion matrix
            if vector._standard not in acc:
                acc[vector._standard] = {}
            if vector._tbl_cur not in acc:
                acc[vector._tbl_cur] = {}
            acc[vector._standard][vector._tbl_cur] = acc[vector._standard].get(
                vector._tbl_cur, 0) + 1
            # Add to results
            gloss = (vector._dataset, vector._iso, vector._gloss)
            if gloss not in self._results:
                self._results[gloss] = {}
            self._results[gloss][vector._tbl_cur] = self._results[gloss].get(
                vector._tbl_cur, 0) + 1
        # Call system and accuracy functions
        self.system(syst, collection)
        self.accuracy(acc, collection)
        return True

    def set_results(self):
        for gloss in self._results:
            self._results[gloss] = functions.probD_conversion(
                self._results.get(gloss, 0))
        return True

    def test(self, vectors, collection):
        self.decode(vectors, collection)
        self.set_results()
        return True

Model.load_standard_glosses()
