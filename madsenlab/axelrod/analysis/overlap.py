#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

def calc_probability_interaction(agent_traits, neighbor_traits):
        """
        The probability of interaction is simply the inverse of the fraction of the features for which the
        two agents have different traits at any given time.  Since the traits are held in
        arrays, this probability reduces to the Hamming distance between the two arrays.  Which
        scipy does quickly.  So the relevant probability is 1 - hamming(a,b).



        """
        diff = len(get_different_feature_positions(agent_traits,neighbor_traits))
        prob = 1.0 - (float(diff) / float(len(agent_traits)))
        return prob
        #log.debug("num features differ: %s, prob: %s", diff, prob)
        #return (1.0 - ssd.hamming(agent_traits, neighbor_traits))


def calc_overlap(agent_traits, neighbor_traits):
    """
    Returns the number of features at which two lists overlap (ie., the opposite of what we normally
    calcultion for interaction).
    """
    overlap = 0.0
    for i in range(0, len(agent_traits)):
        if agent_traits[i] == neighbor_traits[i]:
            overlap += 1.0

    return overlap


def get_different_feature_positions(agent_traits, neighbor_traits):
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