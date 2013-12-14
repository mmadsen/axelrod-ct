#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import unittest
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.traits as traits
import madsenlab.axelrod.population as pop
import networkx as nx
import matplotlib.pyplot as plt
import logging as log
import pprint as pp
import tempfile

class TreeStructuredTraitTest(unittest.TestCase):

    def setUp(self):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
        self.tf = tempfile.NamedTemporaryFile(dir="/tmp", delete=False)
        self.tf.write("""
        {
    "REPLICATIONS_PER_PARAM_SET" : 10,
    "POPULATION_SIZES_STUDIED" : [64,100],
    "TRAIT_ADDITION_RATE" : [0.01, 0.05, 0.1, 0.25],
    "MAXIMUM_INITIAL_TRAITS" : [4,8,16,32],
    "NUM_TRAIT_TREES" : [1,4,8,16],
    "TREE_BRANCHING_FACTOR" : [2,3,4,8],
    "TREE_DEPTH_FACTOR" : [4,5,6,8],
    "POPULATION_STRUCTURE_CLASS" : "madsenlab.axelrod.population.ExtensibleTraitStructurePopulation",
    "INTERACTION_RULE_CLASS" : "madsenlab.axelrod.rules.ExtensibleAxelrodRule",
    "NETWORK_FACTORY_CLASS" : "madsenlab.axelrod.population.SquareLatticeFactory",
    "TRAIT_FACTORY_CLASS" : "madsenlab.axelrod.traits.BalancedTreeStructuredTraitFactory"
}
        """)
        self.tf.flush()
        self.config = utils.TreeStructuredConfiguration(self.tf.name)

    @unittest.skip("Skipping test_tree_construction: this creates a graph and blocks - run manually")
    def test_tree_construction(self):
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()

        pos=nx.graphviz_layout(trait_univ.graph,prog='dot')
        nx.draw(trait_univ.graph,pos,with_labels=True,arrows=False)
        plt.show()
        self.assertTrue(True)

    def test_path(self):
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        expected = [0, 3, 12, 39]
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        path = trait_univ.get_parents_for_node(120)
        log.info("path for trait 120: %s", pp.pformat(path))
        self.assertEqual(expected, path)

    def test_has_prerequisites(self):
        agent_traits = set([0, 3, 12, 39])
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        self.assertTrue(trait_univ.has_prereq_for_trait(120, agent_traits))

    def test_nothave_prerequisites(self):
        agent_traits = set([0, 3])
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        self.assertFalse(trait_univ.has_prereq_for_trait(120, agent_traits))

    def test_random_trait_paths(self):
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        factory = traits.BalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        for i in range(0, 10):
            rand_path = trait_univ.get_random_trait_path()
            log.info("rand path %s: %s", i, rand_path)

    @unittest.skip("Skipping test_multiple_tree_creation: this creates a graph and blocks - run manually")
    def test_multiple_tree_creation(self):
        self.config.depth_factor = 3
        self.config.branching_factor = 2
        self.config.num_trees = 3

        factory = traits.MultipleBalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        pos=nx.graphviz_layout(trait_univ.graph,prog='dot')
        nx.draw(trait_univ.graph,pos,with_labels=True,arrows=False)
        plt.show()
        self.assertTrue(True)

    def test_multiple_tree_correct_root(self):
        self.config.depth_factor = 4
        self.config.branching_factor = 3
        self.config.num_trees = 4
        factory = traits.MultipleBalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()

        node = 255
        root_for_node = trait_univ._get_root_for_node(node)
        expected = 242
        log.info("the root for node %s is %s, expected %s", node, root_for_node, expected)
        self.assertEqual(root_for_node, expected)

    def test_path_multiple_trees(self):
        self.config.depth_factor = 3
        self.config.branching_factor = 2
        self.config.num_trees = 2
        expected = [15, 17, 21]

        factory = traits.MultipleBalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        path = trait_univ.get_parents_for_node(29)
        log.info("mult tree path - expected: %s obs: %s", expected, path)
        self.assertEqual(expected,path)

    def test_prereq_mult_trees(self):
        self.config.depth_factor = 3
        self.config.branching_factor = 2
        self.config.num_trees = 2
        agent_traits = [15, 17, 21]

        factory = traits.MultipleBalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()
        self.assertTrue(trait_univ.has_prereq_for_trait(29, agent_traits))

    def test_random_trait_paths(self):
        self.config.depth_factor = 3
        self.config.branching_factor = 3
        self.config.num_trees = 8
        factory = traits.MultipleBalancedTreeStructuredTraitFactory(self.config)
        trait_univ = factory.initialize_traits()

        for i in range(0, 10):
            log.info("%s", trait_univ.get_random_trait_path())

    def test_mult_tree_population(self):
        self.config.depth_factor = 3
        self.config.branching_factor = 3
        self.config.num_trees = 8
        self.config.popsize = 25
        trait_factory = traits.MultipleBalancedTreeStructuredTraitFactory(self.config)
        graph_factory = pop.SquareLatticeFactory(self.config)
        self.pop = pop.TreeTraitStructurePopulation(self.config,graph_factory,trait_factory)
        self.pop.initialize_population()






if __name__ == "__main__":
    unittest.main