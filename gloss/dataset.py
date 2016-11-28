#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import os
import re

# Import scripts
from gloss import errors as GlossErrors


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'gloss/dataset.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def infer_datasets(datasets):
    """
    Take a JSON representation of the datasets to be loaded and create
    a DS representation with all paths for XIGT and choices files.
    Args:
        datasets: [{"name": dataset name, "path": abs path}]

    Returns:
        JSON representation for internal map_gloss usage that extracted
        ISO values and paths to corresponding XIGT and choices files.
        If choices files are not present then a None value will be
        displayed.
    """
    for dataset in datasets:
        if "iso_list" not in dataset:
            dataset["iso_list"] = find_iso_directories(dataset["path"])
    return datasets


def find_iso_directories(path):
    """
    Use a path for a dataset and discover all ISO directories. This
    means that a dataset must have subdirectories that are named after
    ISO values. If a dataset needs additional directories they must
    have a length greater than 3 to be ignored.
    Args:
        path: a path to a dataset extracted from the datasets JSON

    Returns:
        iso_list attribute for the dataset
    """
    iso_list = {}
    for iso in [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x)) and len(x) <= 3]:
        iso_list[iso] = find_files(path)
    return iso_list


def find_files(path):
    """
    Use simple inference logic and traverse a directory to find the
    XIGT and hoices files for an ISO.
    Args:
        path: ISO path

    Returns:
        {"xigt": xigt path for ISO, "choices": choices path for ISO}
    """
    xigt = None
    choices = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if re.search('testsuite-enriched.xml', file):
                xigt = os.path.join(root, file)
            elif re.search('choices.up', file):
                choices = os.path.join(root, file)
    return {"xigt": xigt, "choices": choices}