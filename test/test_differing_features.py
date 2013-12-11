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
import tempfile


class DifferingFeaturesTest(unittest.TestCase):


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

        config.popsize = 25
        config.num_features = 4
        config.num_traits = 4

        graph_factory = pop.SquareLatticeFactory(config)
        trait_factory = traits.AxelrodTraitFactory(config)
        self.pop = pop.FixedTraitStructurePopulation(config, graph_factory, trait_factory)
        self.pop.initialize_population()
        self.rule = rules.AxelrodRule(self.pop)


    def test_differing_features(self):
        a = [3,3,0,2]
        b = [3,0,0,0]
        expected = [1,3]
        obs = analysis.get_different_feature_positions_axelrod(a,b)
        log.info("obs: %s expected: %s", obs, expected)

if __name__ == "__main__":
    unittest.main