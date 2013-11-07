#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import unittest
import madsenlab.axelrod.utils as utils
import os
import tempfile

class ConfigurationTest(unittest.TestCase):
    filename = "test"

    def setUp(self):
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

    def tearDown(self):
        os.remove(self.tf.name)


    def test_configuration(self):
        print "tempfile: %s" % self.tf.name

        config = utils.AxelrodConfiguration(self.tf.name)
        print "configured REPLICATIONS_PER_PARAM_SET: %s" % config.REPLICATIONS_PER_PARAM_SET
        self.assertEqual(5, config.REPLICATIONS_PER_PARAM_SET, "Config file value does not match")



    def test_latex_output(self):

        config = utils.AxelrodConfiguration(self.tf.name)
        table = config.to_latex_table("test")

        print table

    def test_pandoc_output(self):

        config = utils.AxelrodConfiguration(self.tf.name)
        table = config.to_pandoc_table("test")

        print table

if __name__ == "__main__":
    unittest.main()