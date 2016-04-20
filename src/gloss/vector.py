import re
import string

# Import scripts
from src.eval import gold_standard
from src.utils import functions
from src.utils.xigt.codecs import xigtxml
from src.gloss.constants import GRAMS, VALUES, DATASETS, EVAL


__author__ = 'Michael Lockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


def set_vectors():
    """Function for the user to call to process a set(s) of glosses.
    Ensures that /src/xigt is in the PYTHONPATH.

    Keyword arguments:
      collection -- the list of xigt files organized into tuples as
                    following:
                    [(collection_name, iso_code, xigt_file), ... ]
    """
    # Process and convert data
    for dataset in DATASETS:
        for iso in DATASETS[dataset]:
            # Open the current xigt file
            file = open(DATASETS[dataset][iso])
            xc = xigtxml.load(file)
            file.close()
            punctex = re.compile('[%s]' % string.punctuation)
            # Train each IGT sentence
            for igt in xc:

                # Capture the morphemes
                morphemes = {}
                for morpheme in igt.get('m'):
                    morphemes[morpheme.id] = morpheme.value()

                # Determine which glosses share a morpheme
                shared_morphemes = {}
                for gloss in igt.get('g'):
                    try:
                        if morphemes[gloss.alignment] not in shared_morphemes:
                            shared_morphemes[morphemes[gloss.alignment]] = []
                        shared_morphemes[morphemes[gloss.alignment]] = (shared_morphemes.get(
                            morphemes[gloss.alignment], 0) + [re.sub(' ', '', str(gloss.value()).lower())])
                    except:
                        pass

                # Capture the translated words
                words = {}
                for line in igt.get('t'):
                    line = str(line.value()).lower()
                    line = line.split()
                    for word in line:
                        words[word] = True

                # Create a vector for each gloss instance
                for gloss in igt.get('g'):
                    gloss = re.sub(punctex, '', str(gloss.value()))
                    if gloss:
                        word_match = False
                        if gloss.lower() in words:
                            word_match = True
                        try:
                            Vector(dataset, iso, gloss, shared_morphemes[morphemes[gloss.alignment]], word_match)
                        except:
                            Vector(dataset, iso, gloss, '', word_match)

    return True


def set_gold_standard():
    annotate = []
    # Process every vector
    for vector in Vector.objects:
        # Collect vector obj
        obj = Vector.objects[vector]

        # If GoldStandard object does not exist, create GoldStandard object
        if (obj.dataset, obj.iso, obj.gloss) not in gold_standard.GoldStandard.objects:
            annotate += [(obj.dataset, obj.iso, obj.gloss)]
            gold_standard.GoldStandard(obj.dataset, obj.iso, obj.gloss)

        # If GoldStandard standard does not exist, add observation
        elif not gold_standard.GoldStandard.objects[(obj.dataset, obj.iso, obj.gloss)].label:
            gold_standard.GoldStandard.objects[(obj.dataset, obj.iso, obj.gloss)].add_count()

        # If GoldStandard has a standard send to Vector
        else:
            obj.label = str(gold_standard.GoldStandard.objects[(obj.dataset, obj.iso, obj.gloss)].label)

    # If there were values that needed a GoldStandard standard
    if annotate:
        # Seek input and then send to Vector
        gold_standard.GoldStandard.annotate(annotate)
        for unique in annotate:
            for vector in Vector.lookup[unique]:
                vector.label = gold_standard.GoldStandard.objects[unique].label
    return True


class Collection:

    objects = {}
    strings = {}
    id_generator = 1

    def __init__(self, structure, id=None):
        self.structure = structure
        self.vectors = self.retrieve_vectors()

        # Set id and store in objects
        self.id = id if not None else hex(Collection.id_generator)
        if self.id == Collection.id_generator:
            Collection.id_generator += 1
        Collection.objects[id] = self

    @staticmethod
    def parse_collection_string(collection):
        structure = {}

        # Split & delimited datasets for the collection
        collection = re.split('&', collection)

        # For each dataset after the split
        for dataset in collection:

            # Test for exception datasets
            dataset = re.split('!', dataset)
            if len(dataset) == 2:
                # Set an <except> key and then add each iso to the dataset that is an exception
                structure[dataset[0]] = {'<except>': True}
                languages = re.split('-', dataset[1])
                for iso in languages:
                    structure[dataset[0]][iso] = True

            # Test for specified datasets
            else:
                dataset = re.split('-', dataset[0])
                if len(dataset) > 1:
                    structure[dataset[0]] = {}
                    for iso in dataset[1:]:
                        structure[dataset[0]][iso] = True

                # Otherwise make the dataset an all-inclusive set
                else:
                    structure[dataset[0]] = '<all>'

        return structure

    @staticmethod
    def init_string_collection(collection):
        # If the collection has not been seen create the Collection object
        if collection not in Collection.strings:
            structure = Collection.parse_collection_string(collection)
            Collection.strings[collection] = Collection(structure)
        return Collection.strings[collection]

    def retrieve_vectors(self):
        # Select the vectors that match the Collection object's structure
        vectors = []
        for dataset in self.structure:
            if dataset in Vector.structured:
                # Process datasets equal to '<all>'
                if self.structure[dataset] == '<all>':
                    for iso in Vector.structured[dataset]:
                        vectors += Vector.structured[dataset][iso]

                # Process exception datasets
                elif '<except>' in self.structure[dataset]:
                    for iso in Vector.structured[dataset]:
                        if iso not in self.structure[dataset]:
                            vectors += Vector.structured[dataset][iso]

                # Process specified datasets
                else:
                    for iso in self.structure[dataset]:
                        if iso in Vector.structured[dataset]:
                            vectors += Vector.structured[dataset][iso]
        return vectors


class Vector:

    objects = {}  # id
    lookup = {}  # {(dataset, iso, gloss): {vector_obj: True}}
    structured = {}  # {dataset: {iso: True}}
    id_generator = 1

    def __init__(self, dataset, iso, raw_gloss, morphemes, word_match):
        # Initialized attributes
        self.dataset = dataset.lower()
        self.iso = iso.lower()
        self.raw_gloss = raw_gloss
        self.gloss = str(raw_gloss.lower())
        self.unique = (self.dataset, self.iso, self.gloss)
        self.morphemes = morphemes
        self.word_match = word_match

        # Empty structures and function based attributes
        self.label = ''
        self.segments = {}
        self.set_segmentation()
        self.distances = {}
        self.features = {}
        self.set_features()

        # Set id
        self.id = hex(Vector.id_generator)
        Vector.id_generator += 1
        Vector.objects[self.id] = self

        # Set unique dataset
        if self.unique not in Vector.lookup:
            Vector.lookup[self.unique] = {}
        Vector.lookup[self.unique][self] = True

        # Set class level structures
        if self.dataset not in Vector.structured:
            Vector.structured[self.dataset] = {}
        if self.iso not in Vector.structured[self.dataset]:
            Vector.structured[self.dataset][self.iso] = []
        Vector.structured[self.dataset][self.iso] = Vector.structured[self.dataset].get(self.iso, 0) + [self]

    def set_features(self):
        # General self.features
        self.features['gloss_' + str(self.gloss)] = 1
        if self.gloss in GRAMS:
            self.features['is_standard'] = 1
            self.features['standard_'+str(self.gloss)] = 1
        # Morphemes
        for M in self.morphemes:
            self.features['shared_morpheme_' + str(M)] = 1
        # Segments
        for S in self.segments:
            if self.segments[S]:
                self.features['segment_match_' + str(S)] = 1
            else:
                self.features['segment_nonmatch_' + str(S)] = 1
        if self.segments:
            self.features['segment_count'] = len(self.segments)
        """
        # Distances
        self.set_distances
        for D in self.distances:
            self.self.features['distance_' + str(D) + '_' +
                           str(self.distances[D])] = 1
        """
        # Features to improve incomplete disambiguation
        if self.gloss in VALUES:
            self.features['std_value_' + str(VALUES[self.gloss][1])] = 1
        """
        # Features to improve word disambiguation
        self.features['count_' + str(GoldStandard.objects[(self.dataset, self.iso, self.gloss)].observed)] = 1
        self.features['length_' + str(len(self.gloss))] = 1
        self.features['vowels_' + str(len(re.findall('[aeiou]', self.gloss, re.IGNORECASE)))] = 1
        """
        if self.word_match:
            self.features['word_match'] = 1
        if str(self.raw_gloss).islower():
            self.features['lower_case'] = 1
        elif str(self.raw_gloss).isupper():
            self.features['upper_case'] = 1
        else:
            self.features['mixed_case'] = 1
        return True

    def set_distances(self):
        for gram in GRAMS:
            self.distances[gram] = functions.levenshtein(self.gloss, gram)
        return True

    def set_segmentation(self):
        """Locate all segments within the gloss.
        """
        # Explore all glosses
        for gram in GRAMS:
            # If there is a match
            if re.search(gram, self.gloss):
                # Add match to segments
                self.segments[gram] = True
                match = re.search(gram, self.gloss)
                # Process values to the left and right of the segment
                self._set_segmentation(self.gloss[:match.span()[0]])
                self._set_segmentation(self.gloss[match.span()[1]:])
        return True

    def _set_segmentation(self, gloss_part):
        """Locate all segments within the gloss, if the gloss is Leipzig
        or Gold it will match itself. This is for inner recursion of the
        remainder.
        """
        if not gloss_part:
            return False
        match = False
        # Try each gloss value
        for gram in GRAMS:
            # If there is a match
            if re.search(gram, gloss_part):
                # Add match to segments
                self.segments[gram] = True
                match = True
                match = re.search(gram, gloss_part)
                # Process values to the left and right of the segment
                self._set_segmentation(gloss_part[:match.span()[0]])
                self._set_segmentation(gloss_part[match.span()[1]:])
        # If no match has been found
        if not match:
            # Add the gloss part to segments
            self.segments[gloss_part] = False
        return True


set_vectors()
if EVAL:
    set_gold_standard()
