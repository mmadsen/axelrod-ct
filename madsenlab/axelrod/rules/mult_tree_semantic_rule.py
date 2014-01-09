#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""


"""

import logging as log
import madsenlab.axelrod.population as pop
import math as m
import numpy.random as npr
import random
import scipy.spatial.distance as ssd
import madsenlab.axelrod.analysis as analysis



class MultipleTreePrerequisitesLearningCopyingRule(object):
    """
    Implements an Axelrod model with traits organized as multiple concept trees, where paths in the tree
    represent concept prerequisites.
    """

    def __init__(self, model):
        self.model = model
        self.sc = self.model.simconfig
        self.prng = self.sc.prng

    def step(self, timestep):
        """
        Implements a single time step in the Multiple Tree Prerequisites + Learning "semantic" Axelrod model,
        selecting a focal agent at
        random, and then one of the focal agent's neighbors (this rule knows nothing about
        how "neighbors" are represented, so the rule itself is fully generic to many
        population structures, including those with long-distance connections.

        The two agents interact based upon their cultural similarity, measured as set-theoretic overlap regardless
        of the structure of traits themselves.  If the focal agent if F, and a random neighbor is N, then:

        1.  No interaction is possible if F == N, if F.isdisjoint(N), or if N.issubset(F).
        2.  Otherwise with probability equal to the Jaccard index between F and N, interaction occurs.
        3.  The list of traits which N possesses but F does not is constructed, and a random choice made, of T
        4.  If F possesses the prerequisite traits for T, F either adds T, or replaces a random trait of its own.
        5.  Otherwise, with prob equal to the learning rate, F learns the "most foundational" missing prereq for T.
        6.  Otherwise, nothing happens.
        """


        learning_rate = self.sc.learning_rate
        loss_rate = self.sc.loss_rate
        innov_rate = self.sc.innov_rate

        (agent_id, agent_traits) = self.model.get_random_agent()
        (neighbor_id, neighbor_traits) = self.model.get_random_neighbor_for_agent(agent_id)


        if agent_traits == neighbor_traits:
            return
        elif agent_traits.isdisjoint(neighbor_traits):
            return
        elif neighbor_traits.issubset(agent_traits):
            return
        else:
            prob = analysis.calc_probability_interaction_extensible(agent_traits, neighbor_traits)
            if npr.random() < prob:
                #log.debug("starting interaction")
                neighbor_diff_traits = analysis.get_traits_differing_from_focal_extensible(agent_traits, neighbor_traits)

                # get a random trait from the neighbor that we'd like to try to learn
                # THE ARRAY DEFERENCE IS ESSENTIAL SINCE random.sample returns an array, even with one element.
                rand_trait = random.sample(neighbor_diff_traits, 1)[0]

                if self.model.trait_universe.has_prereq_for_trait(rand_trait, agent_traits) == False:
                    if npr.random() < learning_rate:
                        needed_prereq = self.model.trait_universe.get_deepest_missing_prereq_for_trait(rand_trait, agent_traits)
                        agent_traits.add(needed_prereq)
                        self.model.set_agent_traits(agent_id, agent_traits)

                else:  # has prereqs, add or replace an existing trait, according to the loss rate
                    if npr.random() < loss_rate:
                        # we replace an existing trait with the neighbor's trait
                        focal_trait_to_replace = random.sample(agent_traits, 1)[0]
                        #log.debug("replacing trait %s with %s", focal_trait_to_replace, rand_trait)
                        agent_traits.remove(focal_trait_to_replace)
                        agent_traits.add(rand_trait)
                        self.model.set_agent_traits(agent_id, agent_traits)
                    else:
                        # we add the neighbor's trait, without replacing an existing trait
                        agent_traits.add(rand_trait)
                        #log.debug("adding trait w/o replacement: %s", rand_trait)
                        self.model.set_agent_traits(agent_id, agent_traits)

                # track the interaction and time
                self.model.update_interactions(timestep)



        # now, we see if an innovation happens in the population and perform it if so.
        if npr.random() < innov_rate:
            (innov_agent_id, innov_agent_traits) = self.model.get_random_agent()
            random_innovation = self.model.trait_universe.get_random_trait_not_in_set(innov_agent_traits)
            path = self.model.trait_universe.get_parents_for_node(random_innovation)
            path.append(random_innovation)
            innov_agent_traits.update(path)
            self.model.set_agent_traits(innov_agent_id, innov_agent_traits)
            self.model.update_innovations()
            #log.debug("innovation - adding trait path %s to agent %s", path, innov_agent_id)


    def get_fraction_links_active(self):
        """
        Calculate the fraction of links whose probability of interaction is neither 1.0 nor 0.0
        """
        active_links = 0
        for (a,b) in self.model.model.edges_iter():
            (a_id, a_traits) = self.model.get_agent_by_id(a)
            (b_id, b_traits) = self.model.get_agent_by_id(b)
            prob = analysis.calc_probability_interaction_extensible(a_traits, b_traits)
            if prob > 0.0 and prob < 1.0:
                #log.debug("active link (%s %s) prob: %s  a_trait: %s  b_trait: %s", a_id, b_id, prob, a_traits, b_traits)
                active_links += 1
        num_links_total = self.model.model.number_of_edges()
        #log.debug("active links: %s total links: %s", active_links, num_links_total)
        fraction_active = float(active_links) / float(num_links_total)
        return fraction_active

