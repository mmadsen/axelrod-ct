#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
from axelrod_rule import AxelrodRule
import logging as log
import madsenlab.axelrod.population as pop
import math as m
import numpy.random as npr
import scipy.spatial.distance as ssd

class AxelrodDriftRule(AxelrodRule):
    """
    Subclass of AxelrodRule, we want to keep everything since it's now well tested, and
    simply add another aspect to the step() method.
    """

    def __init__(self,model):
        self.model = model
        self.sc = self.model.simconfig



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

        4.  With probability R, perturb a random feature to a random trait value to simulate drift.
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

        # now do the independent drift step
        draw2 = npr.random()
        if draw2 < self.model.simconfig.drift_rate:
            old_agent_traits = list(agent_traits)
            rand_feature_num = npr.randint(0, len(agent_traits))
            rand_trait_val = npr.randint(0, self.model.simconfig.num_traits)
            agent_traits[rand_feature_num] = rand_trait_val
            log.debug("drift event: old: %s  new: %s", old_agent_traits, agent_traits)
            self.model.set_agent_traits(agent_id, agent_traits)

