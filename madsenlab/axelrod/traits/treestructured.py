#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import networkx as nx
from numpy.random import RandomState
import madsenlab.axelrod.utils as utils
import logging as log
import pprint as pp

##########################################################################
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

        draw = self.prng.random_integers(0, num_t - 1)
        path = self.get_parents_for_node(draw)
        # now tack on the rand_trait itself
        path.append(draw)
        #log.debug("rand trait: %s path: %s", draw, pp.pformat(path))
        return path

##########################################################################

class MultipleTreeStructuredTraitSet(TreeStructuredTraitSet):

    def __init__(self, graph, root_list, prng):
        self.graph = graph
        self.prng = prng
        self.roots = root_list


    def _get_root_for_node(self, node):
        result = 0
        for root in self.roots:
            if node < root:
                break
            result = root
        return result


    def get_parents_for_node(self, node_id):
        """
        Given a node in a tree, return a list of its parents (but not the node itself).

        Relies on the fact that all_simple_paths should return only a single path in a tree, but
        allows for multiple roots (i.e., we may have multiple trees)
        """
        root_for_node = self._get_root_for_node(node_id)
        #log.debug("getting paths from %s to %s", root_for_node, node_id)
        generator = nx.all_simple_paths(self.graph, source=root_for_node, target=node_id)
        path = generator.next()  # only one tree should come back
        path.pop() # remove last element, which is the target node_id
        return path




##########################################################################

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



    def initialize_population(self, pop_graph):
        pass


##########################################################################

class MultipleBalancedTreeStructuredTraitFactory(object):
    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.prng = RandomState()

    def initialize_traits(self):
        r = self.simconfig.branching_factor
        h = self.simconfig.depth_factor
        n = self.simconfig.num_trees

        graphs = []
        roots = []

        num_nodes = utils.num_nodes_balanced_tree(r, h)
        starting_num = 0

        for i in range(0, n):
            #log.debug("building tree with starting root: %s", starting_num)
            g = nx.balanced_tree(r,h)
            g = nx.convert_node_labels_to_integers(g, first_label = starting_num)

            #log.debug("nodes: %s", pp.pformat(g.nodes()))

            graphs.append(g)
            roots.append(starting_num)
            starting_num += num_nodes

        trees = nx.union_all(graphs)
        #log.debug("roots: %s", pp.pformat(roots))
        self.trait_set = MultipleTreeStructuredTraitSet(trees, roots, self.prng)
        return self.trait_set

    def initialize_population(self, pop_graph):
        mt = self.simconfig.maxtraits
        for nodename in pop_graph.nodes():
            # get a random number of initial trait chains
            agent_traits = set()
            init_trait_num = self.prng.random_integers(1, mt)

            for i in range(0, init_trait_num):
                chain = self.trait_set.get_random_trait_path()
                agent_traits.add(tuple(chain))

            #log.debug("traits: %s", pp.pformat(agent_traits))
            pop_graph.node[nodename]['traits'] = agent_traits



