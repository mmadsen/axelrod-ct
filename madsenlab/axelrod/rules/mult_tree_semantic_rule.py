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
import pprint as pp



class MultipleTreePrerequisitesLearningCopyingRule(object):
    """
    Implements an Axelrod model with traits organized as multiple concept trees, where paths in the tree
    represent concept prerequisites.
    """

    def __init__(self, model):
        self.model = model
        self.sc = self.model.simconfig
        self.prng = self.sc.prng
        self.active_link_set = set()
        self.initialize()

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

        When any change happens to the focal agent, we update the active link cache, either for the single
        agent-neighbor pair involved in the interaction, or all of the agent's links.  This allows model checking
        at the global level to be a simple O(1) operation.
        """


        learning_rate = self.sc.learning_rate
        loss_rate = self.sc.loss_rate
        innov_rate = self.sc.innov_rate

        (agent_id, agent_traits) = self.model.get_random_agent()
        (neighbor_id, neighbor_traits) = self.model.get_random_neighbor_for_agent(agent_id)

        # FIXED BUG - WE DO NOT RETURN HERE, WE PASS, BECAUSE WE ALWAYS NEED TO STILL CHECK FOR
        # INNOVATIONS, OTHERWISE (A) INNOVATIONS AREN'T HAPPENING AT THE CONSTANT GIVEN RATE, AND (B)
        # WE CANNOT ESCAPE A CONVERGED STATE THROUGH NOISE
        if agent_traits == neighbor_traits:
            pass
        elif agent_traits.isdisjoint(neighbor_traits):
            pass
        elif neighbor_traits.issubset(agent_traits):
            pass
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
                        #log.debug("agent %s learned prereq %s from agent %s", agent_id, needed_prereq, neighbor_id)

                else:
                    # find a random trait that focal has but the neighbor does not
                    # and we get rid of it, learning the neighbor's trait instead
                    #log.debug("agent: %s neighbor: %s", agent_traits, neighbor_traits)
                    unique_to_focal = agent_traits.difference(neighbor_traits)
                    #log.debug("unique to focal: %s", unique_to_focal)
                    if len(unique_to_focal) > 0:
                        focal_trait_to_replace = random.sample(unique_to_focal, 1)[0]
                        #log.debug("replacing trait %s with %s", focal_trait_to_replace, rand_trait)
                        agent_traits.remove(focal_trait_to_replace)
                    agent_traits.add(rand_trait)
                    self.model.set_agent_traits(agent_id, agent_traits)

                # track the interaction and time, and update the link cache
                self.model.update_interactions(timestep)
                self.update_link_cache_for_agent(agent_id, agent_traits)


        # now we see if somebody forgets something
        if npr.random() < loss_rate:
            (loss_agent_id, loss_agent_traits) = self.model.get_random_agent()
            if len(loss_agent_traits) < 1:
                return
            trait_to_lose = random.sample(loss_agent_traits, 1)[0]
            loss_agent_traits.remove(trait_to_lose)
            self.model.set_agent_traits(loss_agent_id, loss_agent_traits)
            self.model.update_loss_events()
            self.update_link_cache_for_agent(loss_agent_id, loss_agent_traits)

        # now, we see if an innovation happens in the population and perform it if so.
        if npr.random() < innov_rate:
            (innov_agent_id, innov_agent_traits) = self.model.get_random_agent()
            random_innovation = self.model.trait_universe.get_random_trait_not_in_set(innov_agent_traits)
            path = self.model.trait_universe.get_parents_for_node(random_innovation)
            path.append(random_innovation)
            innov_agent_traits.update(path)
            self.model.set_agent_traits(innov_agent_id, innov_agent_traits)
            self.model.update_innovations()
            self.update_link_cache_for_agent(innov_agent_id, innov_agent_traits)
            #log.debug("innovation - adding trait path %s to agent %s", path, innov_agent_id)


    def initialize(self):
        """
        Given an initialized population model, this method initializes the link cache used to speed
        up iterations of the model by not running a full edge iteration.  We do a full iteration
        at initialization, and then keep the active link set up to date in step() instead.
        """
        self.full_update_link_cache()


    def full_update_link_cache(self):
        for (a,b) in self.model.agentgraph.edges_iter():
            (a_id, a_traits) = self.model.get_agent_by_id(a)
            (b_id, b_traits) = self.model.get_agent_by_id(b)
            prob = analysis.calc_probability_interaction_extensible(a_traits, b_traits)
            if prob > 0.0 and prob < 1.0:
                #log.debug("active link (%s %s) prob: %s  a_trait: %s  b_trait: %s", a_id, b_id, prob, a_traits, b_traits)
                self.add_pair_to_cache(a_id, b_id)

        #log.debug("active link cache: %s", pp.pformat(self.active_link_set))

    def update_link_cache_for_agent(self, agent_id, agent_traits):
        """
        When we perform an action to an agent randomly (e.g., loss or mutation), we need to check ALL of the
        agent's links to neighbors and update the link cache accordingly.
        """
        #log.debug("updating link cache for agent: %s after innovation or loss event", agent_id)
        neighbors = self.model.get_all_neighbors_for_agent(agent_id)
        for neighbor in neighbors:
            (neighbor_id, neighbor_traits) = self.model.get_agent_by_id(neighbor)
            prob = analysis.calc_probability_interaction_extensible(agent_traits, neighbor_traits)
            if prob == 0.0 or prob == 1.0:
                #log.debug("removing (%s,%s) from active link cache", agent_id, neighbor_id)
                self.remove_pair_from_cache(agent_id,neighbor_id)
            else:
                self.add_pair_to_cache(agent_id, neighbor_id)

    def remove_pair_from_cache(self, a_id, b_id):
        """
        necessary because we don't know which order the tuple entries will occur in -- e.g., (1,2) or (2,1)
        """
        if a_id < b_id:
            pair = (a_id, b_id)
        else:
            pair = (b_id, a_id)
        try:
            self.active_link_set.remove(pair)
        except KeyError:
            pass

    def add_pair_to_cache(self, a_id, b_id):
        if a_id < b_id:
            pair = (a_id, b_id)
        else:
            pair = (b_id, a_id)

        self.active_link_set.add(pair)


    def get_fraction_links_active(self):
        """
        Calculate the fraction of links whose probability of interaction is neither 1.0 nor 0.0
        """
        active_links = len(self.active_link_set)

        num_links_total = self.model.agentgraph.number_of_edges()
        #log.debug("active links: %s total links: %s", active_links, num_links_total)
        fraction_active = float(active_links) / float(num_links_total)
        return fraction_active

