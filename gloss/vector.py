#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import uuid

from eval.gold_standard import GoldStandard, Lexicon
from gloss.constants import PUNCTEX
from gloss.standard import Gram
from utils.distance import levenshtein
from xigt.codecs import xigtxml


__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


vectors = {}  # {id: vector_object}}
vector_lookup = {}  # {(dataset, iso, gloss): {vector_id: True}}
vector_structured = {}  # {dataset: {iso: {vector_id: True}}


def set_vectors(datasets):
    """
    Take loaded datasets pointing to XIGT files, load the IGT from the
    files and then send the glosses to vectors.

    Args:
        datasets: loaded dataset objects

    Returns: None

    """
    # Process and convert data
    for dataset in datasets:
        for iso in datasets[dataset]["iso_list"]:
            # Open the current xigt file
            xc = xigtxml.load(open(datasets[dataset]["iso_list"][iso]["xigt"]))
            for igt in xc:
                # Ignore lines without glosses
                if not igt.get('g'):
                    continue

                # Capture the translated words if a translation line exists
                try:
                    words = dict((w, True) for w in ' '.join([str(line.value()).lower() for line in igt.get('t')]
                                                             ).split())
                except:
                    words = {}

                # Determine which glosses share a morpheme
                morphemes = {}
                for gloss in igt.get('g'):
                    if gloss.alignment not in morphemes:
                        morphemes[gloss.alignment] = []
                    morphemes[gloss.alignment] = (morphemes.get(gloss.alignment, 0) +
                                                 [re.sub(' ', '', str(gloss.value()).lower())])

                # Create a vector for each gloss instance
                for gloss in igt.get('g'):
                    if re.sub(PUNCTEX, '', gloss.value()):
                        word_match = True if re.sub(PUNCTEX, '', gloss.value()).lower() in words else False
                        shared = morphemes[gloss.alignment] if gloss.alignment else ''
                        set_vector(dataset, iso, re.sub(PUNCTEX, '', gloss.value()), shared, word_match)


def set_vector(dataset, iso, raw_gloss, morphemes, word_match):
    """
    Build a vector from attributes extracted from the XIGT file. Send
    the vector to the vectors DS.

    Args:
        dataset: gloss' dataset
        iso: gloss' iso
        raw_gloss: raw_gloss before any string processing
        morphemes: glosses sharing the same morpheme
        word_match: boolean for whether the gram matched a word

    Returns: None

    """
    vector = {"id": str(uuid.uuid4()),
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
              # "distances": set_distances(raw_gloss.lower()),
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
    """
    Locate all gram and non-gram segments within the gloss.

    Args:
        gloss: the input gloss

    Returns: dictionary of segments matched to the gloss

    """
    # Explore all grams
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
    """
    This is for inner recursion of the string pieces before and after
    a gram that is discovered in a gloss.

    Args:
        gloss_part: str before or after a gram from a gloss

    Returns: dictionary of segments matched to the gloss

    """
    segments = {}
    if not gloss_part:
        return {}
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
    """
    Find the Levenshtein distance between the gloss and every standard
    gram.

    Args:
        gloss: the input gloss

    Returns: dictionary of distances

    """
    distances = {}
    for gram in Gram.objects:
        distances[gram] = levenshtein(gloss, gram)
    return distances


def set_features(vector):
    """
    Set all the features for the vector.

    Args:
        vector: vector representing the input gloss instance

    Returns: dictionary of features

    """
    features = {}

    # Gloss
    features['gloss_{}'.format(vector["gloss"])] = 1
    if vector["gloss"] in Gram.objects:
        features['is_standard'] = 1
        features['standard_{}'.format(vector["gloss"])] = 1

    # Case matching
    if vector["word_match"]:
        features['word_match'] = 1
    if str(vector["raw_gloss"]).islower():
        features['lower_case'] = 1
    elif str(vector["raw_gloss"]).isupper():
        features['upper_case'] = 1
    else:
        features['mixed_case'] = 1

    # Morphemes
    for M in vector["morphemes"]:
        features['shared_morpheme_{}'.format(M)] = 1

    # Segments
    for S in vector["segments"]:
        if vector["segments"][S]:
            features['segment_match_'.format(S)] = 1
        else:
            features['segment_nonmatch_'.format(S)] = 1
    if vector["segments"]:
        features['segment_count'] = len(vector["segments"])

    # Distances
    # for D in vector["distances"]:
    #     features['distance_{}_{}'.format(D, vector["distances"][D])] = 1

    # Features to improve incomplete disambiguation
    # if vector["gloss"] in Value.objects:
    #     features['std_value_' + str(Value.objects[vector["gloss"]]["category"])] = 1

    # Features to improve word disambiguation
    # features['length_{}'.format(len(vector["gloss"]))] = 1
    # features['vowels_{}'.format(len(re.findall('[aeiou]', vector["gloss"], re.IGNORECASE)))] = 1
    return features


collections = {}  # {collection_tuple: vectors}


def set_collection(collection, require=False):
    """
    Set up a collection of vectors and requirements for whether a gold
    standard is needed for its containing vectors.

    Args:
        collection: train or test collection representation from model
        require: whether these vectors require a gold standard or not

    Returns: collection_str for later collection of vectors

    """
    collection_str = collection if isinstance(collection, str) else ' '.join(collection)
    # If the collection has not been previously structured
    if collection_str not in collections:
        collections[collection_str] = collect_vectors(parse_collection(collection))
    if require:
        [vectors[vector["id"]].update({"gold_requirement": True}) for vector in collections[collection_str]]
    return collection_str


def get_collection(collection_str):
    """
    Collect the vectors from a collection.

    Args:
        collection_str: name for collection

    Returns: dictionary of all vectors for the collection

    """
    return collections[collection_str]


def update_collections():
    """
    Update a collection once gold standard has been processed.

    Returns: None

    """
    for collection in collections:
        for vector in collections[collection]:
            vector["gram"] = vectors[vector["id"]]["gram"]


def parse_collection(collection):
    """
    Parse a collection to determine which datasets and languages it
    includes and excludes.

    Args:
        collection: train or test collection representation from model

    Returns: structured version of the collection

    """
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
    """
    Take a structured collection and collect all of the vectors that
    fit its description.

    Args:
        structure: structured version of the collection

    Returns: dictionary of selected vectors

    """
    # Select the vectors that match the Collection object's structure
    select_vectors = []
    for dataset in structure:
        if dataset in vector_structured:

            # Process datasets equal to '<all>'
            if structure[dataset] == '<all>':
                for iso in vector_structured[dataset]:
                    select_vectors += get_structured_vectors(dataset, iso)

            # Process exception datasets
            elif '<except>' in structure[dataset]:
                for iso in vector_structured[dataset]:
                    if iso not in structure[dataset]:
                        select_vectors += get_structured_vectors(dataset, iso)

            # Process specified datasets
            else:
                for iso in structure[dataset]:
                    if iso in vector_structured[dataset]:
                        select_vectors += get_structured_vectors(dataset, iso)

    return select_vectors


def get_structured_vectors(dataset, iso):
    """
    Helper function to pull exactly the vectors who have matching ids
    within the vector_structured lookup.

    Args:
        dataset: specified dataset within the structured collection
        iso: specified language within the structured collection

    Returns: dictionary of selected vectors

    """
    return [vectors[vector_id] for vector_id in vector_structured[dataset][iso]]


def set_gold_standard(gold_standard_file=None, lexicon_file=None):
    """
    Manages the process for setting a gold standard for the vectors and
    then assigning the gold standard to the vectors.

    Args:
        gold_standard_file: optional user provided gold standard
        lexicon_file: optional user provided lexicon

    Returns: None

    """
    # Load all evaluation files (both map_gloss native and user provided)
    if gold_standard_file:
        GoldStandard.json_path.append(gold_standard_file)
    if lexicon_file:
        Lexicon.json_path.append(lexicon_file)
    GoldStandard.load()
    Lexicon.load()

    annotate = []
    # Process vectors who have gold_requirement set to True
    for vector_id in [v for v in vectors if vectors[v]["gold_requirement"]]:

        # If GoldStandard object does not exist, create GoldStandard object
        vector = vectors[vector_id]
        if vector["unique"] not in GoldStandard.objects:
            annotate += [vector["unique"]]
            GoldStandard(**{"dataset": vector["dataset"], "iso": vector["iso"], "gloss": vector["gloss"], "gram": None})

    # If there were values that needed a GoldStandard gram
    if annotate:

        # Seek user input on GoldStandard
        GoldStandard.annotate(annotate)
        GoldStandard.export(index=-1)
        Lexicon.export(index=-1)

    # Set gold_standard for all vectors
    for vector_id in [v for v in vectors if vectors[v]["gold_requirement"]]:
        vectors[vector_id]["gram"] = GoldStandard.objects[vectors[vector_id]["unique"]].gram
    update_collections()
