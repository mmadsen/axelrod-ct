#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log

def num_nodes_balanced_tree(r,h):
    """
    Returns the number of nodes in a balanced tree, with branching factor R and height H.
    """
    total = 0
    for i in range(0,h+1):
        total += r ** i
        #log.debug("total: %s", total)

    return total