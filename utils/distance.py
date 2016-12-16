#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__email__ = 'lockwm@uw.edu'


def levenshtein(a, b):
    """This function applies the levenshtein algorithm between an
    the object's gloss and a leipzig or gold tag.
    """
    # Reset to calculate whereas b has greater length
    if len(a) < len(b):
        return levenshtein(b, a)
    # If b has length of 0 return length of a
    if len(b) == 0:
        return len(a)
    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]