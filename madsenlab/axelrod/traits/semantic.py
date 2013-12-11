#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import networkx as nx
from numpy.random import RandomState
import logging as log
import pprint as pp


class TreeStructuredTraitSet(object):

    def __init__(self, graph, prng):
        self.graph = graph
        self.prng = prng


    def get_parents_for_node(self, node_id):
        """
        Given a node in a tree, return a list of its parents (but not the node itself).

        Relies on the fact that all_simple_paths should return only a single path in a tree
        """
        generator = nx.all_simple_paths(self.graph, source=0, target=node_id)
        path = generator.next()  # only one tree should come back
        path.pop() # remove last element, which is the target node_id
        return path


    def has_prereq_for_trait(self, trait, agent_traits):
        """
        Given an agent's trait set, and a potential trait to adopt, returns a boolean
        if the agent possesses traits along the tree path between the focal trait and
        the root of a trait tree.
        """
        prereqs = self.get_parents_for_node(trait)
        for t in prereqs:
            if t not in agent_traits:
                return False

        # otherwise, agent has prereqs
        return True

    def get_random_trait_path(self):
        """
        Returns a random trait from the tree, along with its prerequisites in the tree.

        Useful for initializing a population.
        """
        num_t = len(self.graph.nodes())

        rand_trait = self.graph.node[self.prng.random_integers(0, num_t)]
        path = self.get_parents_for_node(rand_trait)
        # now tack on the rand_trait itself
        path.append(rand_trait)
        log.debug("rand trait path: %s", pp.pformat(path))
        return path




class BalancedTreeStructuredTraitFactory(object):
    """
    A class of semantic trait models represent trait relations as a balanced tree, with depth H, and
    branching factor R.

    An example of using such a tree is to represent concepts or elements of knowledge
    which have "prerequisites," where prerequisites are nodes "up" the tree from the focal element, in a path
    terminating at the root.  Most concept trees will not be balanced, but this is a good place to start
    since NetworkX has a graph generator for it.
    """

    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.prng = RandomState()


    def initialize_traits(self):

        g = nx.balanced_tree(self.simconfig.branching_factor,
                             self.simconfig.depth_factor)

        return TreeStructuredTraitSet(g, self.prng)



    def initialize_population(self, graph):
        pass