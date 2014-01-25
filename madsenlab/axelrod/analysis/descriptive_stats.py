#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""

import logging as log
from collections import defaultdict
import numpy as np
import math

def get_culture_counts(pop):
    """
    Takes an instance of a "population" and counts the distinct trait lists (i.e., cultures in the
    Axelrod model sense) in the population.  Cultures are represented by packing the feature/trait list
    into an integer which serves as an identifier for a unique combination of features and traits.

    The return value is a dict of culture id, count.
    """
    counts = defaultdict(int)
    graph = pop.model
    for nodename in graph.nodes():
        traits = graph.node[nodename]['traits']
        culture = pop.get_traits_packed(traits)
        counts[culture] += 1

    # transform into the list of dicts that's more convenient to stuff into mongodb
    stored_counts = []
    for key,val in counts.items():
        stored_counts.append(dict(cultureid=str(key),count=val))
    #log.debug("counts: %s", stored_counts)
    return stored_counts


def get_num_traits_per_individual_stats(pop):
    """
    Takes an instance of a population and returns a tuple with the mean and standard deviation of the
    number of traits per individual.  Only useful for the extensible and semantic models.

    """
    sizes = []
    for nodename in pop.model.nodes():
        sizes.append(len(pop.model.node[nodename]['traits']))
    mean = np.mean(np.asarray(sizes))
    sd = math.sqrt(np.var(np.asarray(sizes)))
    return (mean, sd)


