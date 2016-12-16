#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Lockwood'
__github__ = 'mlockwood'
__email__ = 'lockwm@uw.edu'


# Function to combined weighted dictionaries
def combine_weight(D, weights):
    final = {}
    for method in weights:
        if method in D:
            for entry in D[method]:
                final[entry] = final.get(entry, 0) + (D[method][entry] * weights[method])
    return final


# Function to select maximum value in a dictionary
def max_value(D, tie=False):
    max_value = ('', 0)
    for key in D:
        if D[key] > max_value[1]:
            max_value = (key, D[key])
        elif tie:
            if key == tie:
                if D[key] == max_value[1]:
                    max_value = (key, D[key])
    return max_value


# Function to convert a dictionary's values to probabilities
def prob_conversion(D, retotal=False):
    if not isinstance(D, dict):
        raise TypeError('Data structure is not a dictionary')
    probD = {}
    total = 0.0
    # Add every value in the dictionary to a total variable
    for key in D:
        total += float(D[key])
    # For each value, divide by total for the probability conversion
    for key in D:
        try:
            probD[key] = float(D[key])/total
        except ZeroDivisionError:
            probD[key] = 0.0
    # Return only probD if retotal is False
    if retotal == False:
        return probD
    elif retotal == True:
        return probD, total


