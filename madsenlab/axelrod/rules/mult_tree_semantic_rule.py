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
                        # TODO:  find the deepest missing prerequisite for rand_trait
                        pass

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
            else:
                # no interaction given the random draw and probability, so just return
                #log.debug("no interaction")
                return



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



class MultipleTreeLeafPrereqRule(object):
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
        Implements a single time step in the Multiple Tree Semantic Axelrod model, selecting a focal agent at
        random, and then one of the focal agent's neighbors (this rule knows nothing about
        how "neighbors" are represented, so the rule itself is fully generic to many
        population structures, including those with long-distance connections.

        The two agents interact based upon their cultural similarity. This is handled as follows:

        1.  When two agents have all of their trait paths in common, they would interact but no traits
        would change.  for speed, this is short-circuited.

        2.  When two agents have none of their trait paths in common, the probability of interaction
        is zero.  here we move on with no interaction.

        3.  If the neighbor's set of trait paths are a strict subset of the agent's set of paths, there
        is nothing new to adopt, so we move on.

        4.  Otherwise, with probability equal to the overlapping fraction of paths, the focal agent attempts
        to adopt one of the neighbor's traits.  Adoption depends upon the focal agent possessing the
        correct prerequisites in its existing trait paths.

        5.  With probability equal to the addition rate, the focal agent adds the adopted trait path to its
        list, otherwise the old trait path with prereqs is replaced with the new trait path.


        """
        add_rate = self.sc.add_rate

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
            draw = npr.random()
            if draw < prob:
                #log.debug("starting interaction")
                neighbor_diff_traits = analysis.get_traits_differing_from_focal_extensible(agent_traits, neighbor_traits)

                # get a random trait from the neighbor that we'd like to try to learn
                # THE ARRAY DEFERENCE IS ESSENTIAL SINCE random.sample returns an array, even with one element.
                rand_trait = random.sample(neighbor_diff_traits, 1)[0]

                # do we have the prerequisites?  No?  We can't learn the trait right now.
                if self.model.trait_universe.has_prereq_for_trait(rand_trait, agent_traits) == False:
                    #log.debug("no prerequisites, moving on")
                    return

                #log.debug("has prereqs, copying")

                # the agent can learn the trait, so it's a question of adding or replacing...
                add_draw = npr.random()
                if add_draw < add_rate:
                    # we add the neighbor's trait, without replacing an existing trait
                    agent_traits.add(rand_trait)
                    #log.debug("adding trait w/o replacement: %s", rand_trait)
                    self.model.set_agent_traits(agent_id, agent_traits)
                else:
                    # we replace an existing trait with the neighbor's trait
                    focal_trait_to_replace = random.sample(agent_traits, 1)[0]
                    #log.debug("replacing trait %s with %s", focal_trait_to_replace, rand_trait)
                    agent_traits.remove(focal_trait_to_replace)
                    agent_traits.add(rand_trait)
                    self.model.set_agent_traits(agent_id, agent_traits)

                # track the interaction and time
                self.model.update_interactions(timestep)
            else:
                # no interaction given the random draw and probability, so just return
                #log.debug("no interaction")
                return


    # DEPRECATED 12/29/13 - IF WE'RE JUST STORING TRAITS, NOT CHAINS, WE
    # DON'T NEED A METHOD LIKE THIS.
    # def get_random_differing_trait_to_learn(self, all_diff_traits):
    #     """
    #     Returns a tuple with a random leaf trait and its associated trait chain
    #     If there's only one trait chain, the tuple simply contains that chain and leaf trait
    #
    #     """
    #     if(len(all_diff_traits) == 1):
    #         # get the single tuple from the set and return its last element
    #         t = all_diff_traits.next()
    #         #log.debug("len 1 diff traits: %s", t)
    #         return (t[-1], t)
    #     else:
    #         # draw is a list containing a tuple, so it needs to be dereferenced
    #         draw = random.sample(all_diff_traits, 1)
    #         drawn_chain = draw[0]
    #         #log.debug("len > 1 traits: %s", drawn_chain)
    #         return (drawn_chain[-1], drawn_chain)


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




