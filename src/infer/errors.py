#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'infer/errors.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


class InferError(Exception):

    def __init__(self, message):
        self.message = message


class InvalidContainerTypeError(InferError):
    pass


class InvalidFileTypeError(InferError):
    pass
