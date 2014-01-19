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
    log.debug("n: %s  r(n): %s", n, rn)
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
    log.debug("n: %s k leaves: %s  s_nk: %s", n, k, s_nk)
    return s_nk

