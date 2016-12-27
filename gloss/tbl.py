from gloss.standard import Gram
from utils.stat_reports import accuracy
from utils.IOutils import set_directory


class TBL(object):

    objects = {}  # model_name
    default = None
    path = None

    def __init__(self, train_vectors, model_name, min_gain=1):
        self.train_vectors = train_vectors
        self.model = model_name
        self.min_gain = min_gain
        self.tbl = {}
        self.tbl_rules = []
        self.results = {}
        self.lookup = {}
        TBL.objects[model_name] = self

    @classmethod
    def set_cls_path(cls, out_path):
        cls.path = '{}/reports/classifiers/tbl'.format(out_path) if out_path else None
        set_directory(cls.path)

    # Model function
    def report_model(self):
        writer = open('{}/{}.mod'.format(TBL.path, self.model), 'w')
        writer.write(TBL.default+'\n')
        for rule in self.tbl_rules:
            writer.write('{0:36s} {1:36s} {2:36s} {3:10s}\n'.format(*[str(s) for s in rule]))
        writer.close()

    # System function
    def report_system(self, syst):
        writer = open('{}/{}.sys'.format(TBL.path, self.model), 'w')
        writer.write('%%%%% ' + self.model + ' data:\n')
        for line in syst:
            writer.write('array: {}\n'.format(' '.join(str(s) for s in line)))
        writer.close()

    # Accuracy function
    def report_accuracy(self, acc):
        file = '{}/{}'.format(TBL.path, self.model)
        accuracy(acc, file)

    # Function to set the initial TBL map that matches indices, labels, and feats
    def initialize(self):
        tbl = {}
        # Read each vector object in the training DS
        i = 0
        while i < len(self.train_vectors):
            vector = self.train_vectors[i]
            self.lookup[vector["id"]] = i
            vector["tbl_cur"] = vector["gloss"] if vector["gloss"] in Gram.objects else TBL.default
            # For each feat in the instance's features
            for feat in vector["features"]:
                # Set internal dictionaries if feet unseen
                if feat not in tbl:
                    tbl[feat] = {}
                if vector["tbl_cur"] not in tbl[feat]:
                    tbl[feat][vector["tbl_cur"]] = {}
                if vector["gram"] not in tbl[feat][vector["tbl_cur"]]:
                    tbl[feat][vector["tbl_cur"]][vector["gram"]] = {}
                # Set tbl[feat][cur][gold][vector["id"]] = True
                tbl[feat][vector["tbl_cur"]][vector["gram"]][vector["id"]] = True
            i += 1
        self.tbl = tbl

    # Function to train TBL
    def train_model(self):
        self.initialize()
        gain = self.min_gain
        # Stop rule creation when gain falls below the minimum gain threshold
        while gain >= self.min_gain:
            gain = 0
            best = (True, True, True, 0)

            # For each feat in TBL
            for feat in self.tbl:
                # For each current label
                for cur in self.tbl[feat]:
                    # For each gold label
                    for gold in self.tbl[feat][cur]:
                        # If gold label does not equal current label
                        if gold != cur:
                            # If gain of gold in cur label and feat less loss of cur in gold label is > best gain, make
                            # it new best
                            positive = len(self.tbl[feat][cur][gold])
                            try:
                                negative = len(self.tbl[feat][cur][cur])
                            except KeyError:
                                negative = 0
                            if (positive - negative) > gain:
                                gain = positive - negative
                                best = (feat, cur, gold, gain)

            # Test if gain was 0
            if best[3] < self.min_gain:
                break

            # Change location of indices based on accepted transformation rule
            for label in self.tbl[best[0]][best[1]].keys():
                # Critical to use .keys() here, otherwise deletion won't work
                for vid in list(self.tbl[best[0]][best[1]][label].keys()):
                    vector = self.train_vectors[self.lookup[vid]]
                    # Update each feature for each vector and then update the vector's cur
                    for feat in vector["features"].keys():
                        # Delete previous cur state and instantiate new cur state
                        del self.tbl[feat][vector["tbl_cur"]][vector["gram"]][vid]
                        if best[2] not in self.tbl[feat]:
                            self.tbl[feat][best[2]] = {}
                        if vector["gram"] not in self.tbl[feat][best[2]]:
                            self.tbl[feat][best[2]][vector["gram"]] = {}
                        self.tbl[feat][best[2]][vector["gram"]][vid] = True
                    vector["tbl_cur"] = best[2]
            # Add best rule to TBL rule set
            self.tbl_rules.append(best)

        # Once all rules have been created send them to output
        if TBL.path:
            self.report_model()

    # Function to decode test vectors
    def decode(self, vectors):
        n = 0
        syst = []
        acc = {}
        # For each instance in vectors
        for vector in vectors:
            # Set default class
            vector["tbl_cur"] = vector["gloss"] if vector["gloss"] in Gram.objects else TBL.default
            transformations = []

            # For each transformation rule in order
            for rule in self.tbl_rules:
                # If rule feature is in instance's features
                if rule[0] in vector["features"]:
                    # If from class equals instance's current class
                    if rule[1] == vector["tbl_cur"]:
                        # Set instance's current class to the to class of the rule
                        vector["tbl_cur"] = rule[2]
                        transformations.append(rule)

            # Prepare for outputs
            syst.append((vector["id"], vector["gram"], vector["tbl_cur"], transformations))
            n += 1

            # Send result to confusion matrix
            if vector["gram"] not in acc:
                acc[vector["gram"]] = {}
            if vector["tbl_cur"] not in acc:
                acc[vector["tbl_cur"]] = {}
            acc[vector["gram"]][vector["tbl_cur"]] = acc[vector["gram"]].get(vector["tbl_cur"], 0) + 1

            # Add to results
            if vector["unique"] not in self.results:
                self.results[vector["unique"]] = {}
            self.results[vector["unique"]][vector["tbl_cur"]] = self.results[vector["unique"]].get(vector["tbl_cur"], 0
                                                                                                   ) + 1

        # Call system and accuracy functions
        if TBL.path:
            self.report_system(syst)
            self.report_accuracy(acc)
