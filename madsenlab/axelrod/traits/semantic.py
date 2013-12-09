#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import networkx as nx
from numpy.random import RandomState

class TreeStructuredTraitFactory(object):
    """
    A class of semantic trait models represent trait relations as a tree
    """

    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.prng = RandomState()


    def initialize_population(self, graph):
        pass