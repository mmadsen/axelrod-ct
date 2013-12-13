#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import unittest
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.rules as rules
import madsenlab.axelrod.population as pop
import madsenlab.axelrod.traits as traits
import madsenlab.axelrod.analysis as analysis
import logging as log
import pprint as pp
import tempfile


class AxelrodAnalytics(unittest.TestCase):


    def setUp(self):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
        self.tf = tempfile.NamedTemporaryFile(dir="/tmp", delete=False)
        self.tf.write("""
        {
    "REPLICATIONS_PER_PARAM_SET" : 5,
    "POPULATION_SIZES_STUDIED" : [500,1000],
    "NUMBER_OF_DIMENSIONS_OR_FEATURES" : [1,2,4,8,16],
    "NUMBER_OF_TRAITS_PER_DIMENSION" :  [2,3,4,6,8,12,16,32]
}
        """)
        self.tf.flush()
        config = utils.AxelrodConfiguration(self.tf.name)
        self.config = config

        config.popsize = 25
        config.num_features = 4
        config.num_traits = 4

        graph_factory = pop.SquareLatticeFactory(config)
        trait_factory = traits.AxelrodTraitFactory(config)
        self.pop = pop.FixedTraitStructurePopulation(config, graph_factory, trait_factory)
        self.pop.initialize_population()


    def test_culture_counts(self):
        counts = analysis.get_culture_counts(self.pop)
        log.info("counts: %s", counts)

    def test_klemm(self):
        klemm_val = analysis.klemm_normalized_L_axelrod(self.pop, self.config)
        log.info("klemm axelrod value: %s", klemm_val)


class ExtensibleAnalytics(unittest.TestCase):


    def setUp(self):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
        self.tf = tempfile.NamedTemporaryFile(dir="/tmp", delete=False)
        self.tf.write("""
       {
    "REPLICATIONS_PER_PARAM_SET" : 10,
    "POPULATION_SIZES_STUDIED" : [64,100],
    "TRAIT_ADDITION_RATE" : [0.01, 0.05, 0.1, 0.25],
    "MAXIMUM_INITIAL_TRAITS" : [4,8,16,32],
    "POPULATION_STRUCTURE_CLASS" : "madsenlab.axelrod.population.ExtensibleTraitStructurePopulation",
    "INTERACTION_RULE_CLASS" : "madsenlab.axelrod.rules.AxelrodRule",
    "NETWORK_FACTORY_CLASS" : "madsenlab.axelrod.population.SquareLatticeFactory"
}
        """)
        self.tf.flush()
        config = utils.AxelrodExtensibleConfiguration(self.tf.name)
        self.config = config

        config.popsize = 25
        config.maxtraits = 16
        config.add_rate = 0.1

        graph_factory = pop.SquareLatticeFactory(config)
        trait_factory = traits.ExtensibleTraitFactory(config)
        self.pop = pop.ExtensibleTraitStructurePopulation(config, graph_factory, trait_factory)
        self.pop.initialize_population()


    def test_culture_counts(self):
        counts = analysis.get_culture_counts(self.pop)
        log.info("counts: %s", counts)

    def test_klemm(self):
        klemm_val = analysis.klemm_normalized_L_extensible(self.pop, self.config)
        log.info("klemm extensible value: %s", klemm_val)


if __name__ == "__main__":
    unittest.main