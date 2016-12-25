#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import packages and libraries
import os

from map_gloss.infer.make_choices import *
from map_gloss.eval.eval_infer import Choices, Container


__project_parent__ = 'AGGREGATION'
__project_title__ = 'Automated Gloss Mapping for Inferring Grammatical Properties'
__project_name__ = 'Map Gloss'
__script__ = 'infer/model.py'
__date__ = 'March 2015'

__author__ = 'MichaelLockwood'
__email__ = 'lockwm@uw.edu'
__github__ = 'mlockwood'
__credits__ = 'Emily M. Bender for her guidance'
__collaborators__ = None


def eval_choices(self, out_path, gold_choices):
    """
    THIS IS WHERE THE CRITICAL PROCESSING MUST CHANGE. Evaluation changed from language, dataset, and model levels to
    just the model level which also has language statistics. This needs to be rewritten and rewired to focus on that.
    And inference should be a parameter of the main gloss model, not its own secondary post-process. Something like this
    would occur:
    IFF INFERENCE:
    -References get written by language to choices file as outputs -- NOT to be reloaded for evaluation
    IFF INFERENCE && EVALUATION:
    -Load existing choices files objects for gold standard
    -Build baselines 4 & 5 and final from reference data
    -Output comparisons
    """
    # For each language with a reference
    for language in self:
        # Load choices files for each loadable file
        # Resolve path first
        path = '{}/out/choices/{}'.format(out_path, language.model)
        if not os.path.isdir(path):
            os.makedirs(path)

        # Add base of file name to path
        path += '/{}_{}_{}'.format(language.model, language.dataset, language.iso)

        Choices(gold_choices[language.dataset][language.iso], language.model, language.dataset, language.iso)
        Choices.load_baseline4(language.dataset, language.iso)
        Choices('{}_baseline5.choices'.format(path), language.model, language.dataset, language.iso)
        Choices('{}.choices'.format(path), language.model, language.dataset, language.iso)

    # Write CPRF for the inference evaluation
    for obj in Container.objects:
        container = Container.objects[obj]
        container.set_confusion_matrices()


