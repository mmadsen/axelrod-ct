#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
import overlap as o
import logging as log

def klemm_normalized_L_axelrod(pop,simconfig):
    """
    The normalized Lyapunov potential defined in Klemm et al. 2003, Physica A (327) 1-5.  Implements
    Equation (1).

    Ranges between [0,1], with 0 possible only for the completely homogeneous configurations.
    Variable names differ from the rest of the codebase, but are designed to be identical to the Klemm notation.
    """
    # following is shorthand for the NetworkX graph
    g = pop.model
    N = simconfig.popsize
    z = pop.get_coordination_number()
    F = simconfig.num_features

    #log.debug("z: %s F: %s N: %s", z, F, N)

    norm_constant = 2.0 / (z * N * F)
    sums = 0

    for (a,b) in g.edges_iter():
        (a_id, a_traits) = pop.get_agent_by_id(a)
        (b_id, b_traits) = pop.get_agent_by_id(b)
        overlap = o.calc_overlap_axelrod(a_traits, b_traits)
        sums += (F - overlap)

    result = norm_constant * sums
    log.debug("Klemm normalized L: %s  norm constant: %s sum: %s", result, norm_constant, sums )
    return result
