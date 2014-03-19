#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log
import math as m
import scipy.special as ss
import scipy.misc as sm
import numpy as np


def ratio_order_automorphism_to_symmetric_group(groupsize, order):
    """
    Calculates the ratio of the size of a graph's automorphism group, to the
    maximum possible automorphism group for the most symmetric graph with the same
    number of vertices.  For a general graph, this is the order of the symmetric
    group with n vertices, or n!.

    For a rooted tree with n vertices, the maximum symmetry is achieved by the
    corolla with n vertices (i.e., n-1 leaves on the root).

    If the order of the graph is zero, this method returns 0

    """
    if order == 0:
        return 0
    size_sn = sm.factorial(order)
    ratio = float(groupsize) / float(size_sn)
    frac_order = float(1) / float(order)
    beta = np.power(ratio,frac_order)
    return beta


def num_nodes_balanced_tree(r,h):
    """
    Returns the number of nodes in a balanced tree, with branching factor R and height H.
    """
    total = 0
    for i in range(0,h+1):
        total += r ** i
        #log.debug("total: %s", total)

    return total


def num_rooted_trees_otter_approx(n):
    """
    Returns an approximation of the number of rooted trees on n vertices, using Otter's (1948) constants
    for tree enumeration.  See http://en.wikipedia.org/wiki/Tree_(graph_theory)#Unlabeled_trees

    r(n) ~ D * alpha^n * n^(-3/2)  as n -> +inf

    D ~ 0.43992401257
    alpha ~ 2.95576528565

    """
    a = 2.95576528565
    D = 0.43992401257

    rn = int(m.ceil(D * (a ** n) * (n ** (-3.0/2.0))))
    #log.debug("n: %s  r(n): %s", n, rn)
    return rn


def num_ordered_trees_by_leaves(n, k):
    """
    Returns the number of ordered trees with exactly n vertices including k leaves.

    this value is given by R.P. Stanley, Enumerative Combinatorics, Vol 2, p. 237 as:

    s_nk = [ choose(n-2, k-1) * choose(n-1, k-1) ] / k

    where "choose" is the binomial coefficient operator.  This is also the Narayana
    number for (n,k).

    """
    b1 = ss.binom(n-2, k-1)
    b2 = ss.binom(n-1, k-1)
    s_nk = ( b1 * b2 ) / k
    #log.debug("n: %s k leaves: %s  s_nk: %s", n, k, s_nk)
    return s_nk


def num_leaves_in_tree(g):
    """
    Returns the number of leaves in a rooted tree.
    """
    leaves = 0
    node_ids = g.nodes()
    # check root to make sure it's not odd and has only one child
    root_id = min(node_ids)
    if(len(g.neighbors(root_id)) == 1):
        #log.debug("root on graph has only one neighbor, ignoring it for leaf calculation")
        node_ids.remove(root_id)
    # now iterate through nodes, anytime you find a node with only one neighbor, it's a leaf
    for node in node_ids:
        if(len(g.neighbors(node)) == 1):
            leaves += 1

    return leaves