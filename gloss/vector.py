#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import uuid

from eval.gold_standard import GoldStandard, Lexicon
from gloss.constants import PUNCTEX
from gloss.standard import Gram, Value
from utils import functions
from utils.xigt.codecs import xigtxml


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'gram/vector.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


vectors = {}  # {id: vector_object}}
vector_lookup = {}  # {(dataset, iso, gloss): {vector_id: True}}
vector_structured = {}  # {dataset: {iso: {vector_id: True}}


def set_vectors(datasets):
    # Process and convert data
    for dataset in datasets:
        for iso in dataset["iso_list"]:
            # Open the current xigt file
            xc = xigtxml.load(open(dataset["iso_list"][iso]["xigt"]))
            for igt in xc:
                # Capture the translated words
                words = dict((w, True) for w in ' '.join([str(line.value()).lower() for line in igt.get('t')]).split())

                # Capture the morphemes
                morphemes = dict((morpheme.id, morpheme.value()) for morpheme in igt.get('m'))

                # Determine which glosses share a morpheme
                s_morphs = {"lookup": {}}
                for gloss in igt.get('g'):
                    if hasattr(gloss, "alignment"):
                        if morphemes[gloss.alignment] not in s_morphs:
                            s_morphs[morphemes[gloss.alignment]] = []
                        s_morphs[morphemes[gloss.alignment]] = (s_morphs.get(
                            morphemes[gloss.alignment], 0) + [re.sub(' ', '', str(gloss.value()).lower())])

                # Create a vector for each gloss instance
                for gloss in igt.get('g'):
                    gloss = re.sub(PUNCTEX, '', gloss.value())
                    if gloss:
                        word_match = True if gloss.lower() in words else False
                        shared = s_morphs[gloss.alignment] if hasattr(gloss, "alignment") else ''
                        set_vector(dataset, iso, gloss, shared, word_match)


def set_vector(dataset, iso, raw_gloss, morphemes, word_match):
    vector = {"id": uuid.uuid4(),
              "dataset": dataset.lower(),
              "iso": iso.lower(),
              "raw_gloss": raw_gloss,
              "gloss": raw_gloss.lower(),
              "unique": (dataset.lower(), iso.lower(), raw_gloss.lower()),
              "morphemes": morphemes,
              "word_match": word_match,
              "gold_requirement": False,
              "gram": '',
              "segments": set_segmentation(raw_gloss.lower()),
              "distances": set_distances(raw_gloss.lower()),
              }
    vector["features"] = set_features(vector)
    vectors[vector["id"]] = vector

    # Set lookup
    if vector["unique"] not in vector_lookup:
        vector_lookup[vector["unique"]] = {}
    vector_lookup[vector["unique"]][vector["id"]] = True

    # Set structured
    if vector["dataset"] not in vector_structured:
        vector_structured[vector["dataset"]] = {}
    if vector["iso"] not in vector_structured[vector["dataset"]]:
        vector_structured[vector["dataset"]][vector["iso"]] = {}
    vector_structured[vector["dataset"]][vector["iso"]][vector["id"]] = True


def set_segmentation(gloss):
    """Locate all segments within the gloss.
    """
    # Explore all glosses
    segments = {}
    for gram in Gram.objects:
        # If there is a match
        if re.search(gram, gloss):
            # Add match to segments
            segments[gram] = True
            match = re.search(gram, gloss)
            # Process values to the left and right of the segment
            segments.update(set_segmentation_helper(gloss[:match.span()[0]]))
            segments.update(set_segmentation_helper(gloss[match.span()[1]:]))
    return segments


def set_segmentation_helper(gloss_part):
    """Locate all segments within the gloss, if the gloss is Leipzig
    or Gold it will match itvector[" This is for inner recursion of the
    remainder.
    """
    segments = {}
    if not gloss_part:
        return False
    match = False
    # Try each gloss value
    for gram in Gram.objects:
        # If there is a match
        if re.search(gram, gloss_part):
            # Add match to segments
            segments[gram] = True
            match = re.search(gram, gloss_part)
            # Process values to the left and right of the segment
            segments.update(set_segmentation_helper(gloss_part[:match.span()[0]]))
            segments.update(set_segmentation_helper(gloss_part[match.span()[1]:]))
    # If no match has been found
    if not match:
        # Add the gloss part to segments
        segments[gloss_part] = False
    return segments


def set_distances(gloss):
    distances = {}
    for gram in Gram.objects:
        distances[gram] = functions.levenshtein(gloss, gram)
    return distances


def set_features(vector):
    features = {}

    # Gloss
    features['gloss_' + str(vector["gloss"])] = 1
    if vector["gloss"] in Gram.objects:
        features['is_standard'] = 1
        features['standard_'+str(vector["gloss"])] = 1

    # Morphemes
    for M in vector["morphemes"]:
        features['shared_morpheme_' + str(M)] = 1

    # Segments
    for S in vector["segments"]:
        if vector["segments"][S]:
            features['segment_match_' + str(S)] = 1
        else:
            features['segment_nonmatch_' + str(S)] = 1
    if vector["segments"]:
        features['segment_count'] = len(vector["segments"])

    # Distances
    # for D in vector["distances"]:
    #     features['distance_' + str(D) + '_' + str(vector["distances"][D])] = 1

    # Features to improve incomplete disambiguation
    if vector["gloss"] in Value.objects:
        features['std_value_' + str(Value.objects[vector["gloss"]][1])] = 1

    # Features to improve word disambiguation
    # features['length_' + str(len(vector["gloss"]))] = 1
    # features['vowels_' + str(len(re.findall('[aeiou]', vector["gloss"], re.IGNORECASE)))] = 1

    # Case matching
    if vector["word_match"]:
        features['word_match'] = 1
    if str(vector["raw_gloss"]).islower():
        features['lower_case'] = 1
    elif str(vector["raw_gloss"]).isupper():
        features['upper_case'] = 1
    else:
        features['mixed_case'] = 1
    return features


collections = {}  # {collection_tuple: vectors}


def get_collection(collection, require=False):
    # If the collection has not been seen create the Collection object
    if collection not in collections:
        collections[collection] = collect_vectors(parse_collection(collection))
    if require:
        [vectors[vector_id].update({"gold_requirement": True}) for vector_id in collections[collection]]
    return collections[collection]


def parse_collection(collection):
    structure = {}

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


def collect_vectors(structure):
    # Select the vectors that match the Collection object's structure
    vectors = []
    for dataset in structure:
        if dataset in vector_structured:
            # Process datasets equal to '<all>'
            if structure[dataset] == '<all>':
                for iso in vector_structured[dataset]:
                    vectors += get_structured_vectors(dataset, iso)
            # Process exception datasets
            elif '<except>' in structure[dataset]:
                for iso in vector_structured[dataset]:
                    if iso not in structure[dataset]:
                        vectors += get_structured_vectors(dataset, iso)

            # Process specified datasets
            else:
                for iso in structure[dataset]:
                    if iso in vector_structured[dataset]:
                        vectors += get_structured_vectors(dataset, iso)
    return vectors


def get_structured_vectors(dataset, iso):
    return {(vector_id, vectors[vector_id]) for vector_id in vector_structured[dataset][iso]}


def set_gold_standard(gold_standard_file, lexicon_file):
    # Load all evaluation files (both map_gloss native and user provided)
    if gold_standard_file:
        GoldStandard.json_path.append(gold_standard_file)
    if lexicon_file:
        Lexicon.json_path.append(lexicon_file)
    GoldStandard.load()
    Lexicon.load()

    annotate = []
    # Process vectors who have gold_requirement set to True
    for vector in [v for v in vectors if v["gold_requirement"]]:
        # If GoldStandard object does not exist, create GoldStandard object
        if (vector["dataset"], vector["iso"], vector["gloss"]) not in GoldStandard.objects:
            annotate += [(vector["dataset"], vector["iso"], vector["gloss"])]
            GoldStandard(**{"dataset": vector["dataset"], "iso": vector["iso"], "gloss": vector["gloss"]})

        # If GoldStandard standard does not exist, add observation
        elif not GoldStandard.objects[(vector["dataset"], vector["iso"], vector["gloss"])].gram:
            GoldStandard.objects[(vector["dataset"], vector["iso"], vector["gloss"])].add_count()

        # If GoldStandard has a standard send to Vector
        else:
            vector["gram"] = GoldStandard.objects[(vector["dataset"], vector["iso"], vector["gloss"])].gram

    # If there were values that needed a GoldStandard standard
    if annotate:
        # Seek input and then send to Vector
        GoldStandard.annotate(annotate)
        for unique in annotate:
            for vector in vector_lookup[unique]:
                vector["gram"] = GoldStandard.objects[unique].gram
        GoldStandard.export(index=-1)
        Lexicon.export(index=-1)
    return True
