#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log

def calc_probability_interaction_axelrod(agent_traits, neighbor_traits):
        """
        The probability of interaction is simply the inverse of the fraction of the features for which the
        two agents have different traits at any given time.  Since the traits are held in
        arrays, this probability reduces to the Hamming distance between the two arrays.  Which
        scipy does quickly.  So the relevant probability is 1 - hamming(a,b).



        """
        diff = len(get_different_feature_positions_axelrod(agent_traits,neighbor_traits))
        prob = 1.0 - (float(diff) / float(len(agent_traits)))
        return prob
        #log.debug("num features differ: %s, prob: %s", diff, prob)
        #return (1.0 - ssd.hamming(agent_traits, neighbor_traits))


def calc_probability_interaction_extensible(agent_traits, neighbor_traits):
    """
    Given sets, the overlap and probabilities are just Jaccard distances or coefficients, which
    are easy in python given symmetric differences and unions between set objects.  This also accounts
    for sets of different length, which is crucial in the extensible and semantic models.
    """
    prob = len(agent_traits.symmetric_difference(neighbor_traits)) / len(agent_traits.union(neighbor_traits))
    log.debug("prob interaction: %s", prob)
    return prob



def calc_overlap_axelrod(agent_traits, neighbor_traits):
    """
    Returns the number of features at which two lists overlap (ie., the opposite of what we normally
    calcultion for interaction).
    """
    overlap = 0.0
    for i in range(0, len(agent_traits)):
        if agent_traits[i] == neighbor_traits[i]:
            overlap += 1.0

    return overlap


def calc_overlap_extensible(agent_traits, neighbor_traits):
    """
    Given sets, the overlap and probabilities are just Jaccard distances or coefficients, which
    are easy in python given symmetric differences and unions between set objects.  This also accounts
    for sets of different length, which is crucial in the extensible and semantic models.
    """
    overlap = len(agent_traits.intersection(neighbor_traits)) / len(agent_traits.union(neighbor_traits))
    log.debug("overlap: %s", overlap)
    return overlap


def get_different_feature_positions_axelrod(agent_traits, neighbor_traits):
    """
    Returns a list of the positions at which two lists of traits differ (but not the differing
    traits themselves).
    """
    features = []
    for i in range(0, len(agent_traits)):
        if agent_traits[i] != neighbor_traits[i]:
            features.append(i)
    #log.debug("differing features: %s", features)
    return features


def get_traits_differing_from_focal_extensible(focal_traits, neighbor_traits):
    return focal_traits.difference(neighbor_traits)

def get_traits_differing_from_neighbor_extensible(focal_traits, neighbor_traits):
    return neighbor_traits.difference(focal_traits)

