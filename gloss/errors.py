#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'


class GlossError(Exception):

    def __init__(self, message):
        self.message = message


class InvalidClassifierError(GlossError):
    pass


class ClassifierWeightError(GlossError):
    pass


class InvalidClassifierWeightError(GlossError):
    pass