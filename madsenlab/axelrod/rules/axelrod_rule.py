#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
This rule implements the original Axelrod model on a lattice, given descriptions in Axelrod (1997) and:

@book{Barrat2009,
    Author = {Barrat, A and Barth\'elemy, M and Vespignani, A},
    Publisher = {Cambridge University Press},
    Title = {Dynamical processes on complex networks},
    Year = {2009}}


"""

import logging as log
import madsenlab.axelrod.population as pop
import math as m
import numpy.random as npr
import scipy.spatial.distance as ssd


class AxelrodRule(object):
    """
    Implements the original Axelrod model, taking an instance of a lattice model at construction.
    Returns control to the caller after each step(), so that other code can run to determine completion,
    take samples, etc.
    """

    def __init__(self, model):
        self.model = model


    def step(self, timestep):
        """
        Implements a single time step in the Axelrod model, selecting a focal agent at
        random, and then one of the focal agent's neighbors (this rule knows nothing about
        how "neighbors" are represented, so the rule itself is fully generic to many
        population structures, including those with long-distance connections.

        The two agents interact based upon their cultural similarity. This is handled as follows:

        1.  When two agents have all traits in common, technically they would interact with probability
        one, but no traits would change.  For speed, this is short-circuited.

        2.  When two agents have no traits in common, the probability of interaction is zero.  Here we
        simply move on, and don't make a random trial because there's no point.

        3.  Otherwise, with probability equal to similarity (or, usually, 1 - dissimilarity), the focal
        agent adopts one of the neighbor's traits for which they are dissimilar.

        """
        (agent_id, agent_traits) = self.model.get_random_agent()
        (neighbor_id, neighbor_traits) = self.model.get_random_neighbor_for_agent(agent_id)

        prob = self.calc_probability_interaction(agent_traits, neighbor_traits)

        if prob == 0.0:
            return
        elif prob == 1.0:
            return
        else:
            draw = npr.random()
            if draw < prob:
                differing_features = self.get_different_feature_positions(agent_traits, neighbor_traits)
                old_agent_traits = list(agent_traits)
                if len(differing_features) == 1:
                    random_feature = differing_features[0]
                else:
                    rand_feature_num = npr.randint(0, len(differing_features))
                    random_feature = differing_features[rand_feature_num]
                neighbor_trait = neighbor_traits[random_feature]
                agent_traits[random_feature] = neighbor_trait
                #log.debug("agent %s: old: %s  neighbor: %s  post: %s differing: %s feature: %s val: %s ", agent_id, old_agent_traits, neighbor_traits, agent_traits,differing_features, random_feature, neighbor_trait )
                self.model.set_agent_traits(agent_id, agent_traits)

                # track the interaction and time
                self.model.update_interactions(timestep)
            else:
                # no interaction given the random draw and probability, so just return
                #log.debug("no interaction")
                return


    def get_fraction_links_active(self):
        """
        Calculate the fraction of links whose probability of interaction is not 1.0 or 0.0.
        """
        active_links = 0
        for (a,b) in self.model.model.edges_iter():
            (a_id, a_traits) = self.model.get_agent_by_id(a)
            (b_id, b_traits) = self.model.get_agent_by_id(b)
            prob = self.calc_probability_interaction(a_traits, b_traits)
            if prob > 0.0 and prob < 1.0:
                #log.debug("active link (%s %s) prob: %s  a_trait: %s  b_trait: %s", a_id, b_id, prob, a_traits, b_traits)
                active_links += 1
        num_links_total = self.model.model.number_of_edges()
        #log.debug("active links: %s total links: %s", active_links, num_links_total)
        fraction_active = float(active_links) / num_links_total
        return fraction_active


    def calc_probability_interaction(self, agent_traits, neighbor_traits):
        """
        The probability of interaction is simply the inverse of the fraction of the features for which the
        two agents have different traits at any given time.  Since the traits are held in
        arrays, this probability reduces to the Hamming distance between the two arrays.  Which
        scipy does quickly.  So the relevant probability is 1 - hamming(a,b).



        """
        diff = len(self.get_different_feature_positions(agent_traits,neighbor_traits))
        prob = 1.0 - (float(diff) / float(len(agent_traits)))
        return prob
        #log.debug("num features differ: %s, prob: %s", diff, prob)
        #return (1.0 - ssd.hamming(agent_traits, neighbor_traits))


    def get_different_feature_positions(self, agent_traits, neighbor_traits):
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