#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import unittest
import madsenlab.axelrod.utils as utils
import logging as log


class ClassLoadingTest(unittest.TestCase):
    filename = "test"



    def test_loading(self):
        classname = "calendar.Calendar"
        constructor = utils.load_class(classname)
        obj = constructor()

        t = type(obj)
        print "observed type: %s" % str(t)

        self.assertEqual("<class \'calendar.Calendar\'>", str(t), "class name doesn't match after dynamic loading")

if __name__ == "__main__":
    unittest.main()