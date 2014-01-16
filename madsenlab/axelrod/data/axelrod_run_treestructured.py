#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
.. module:: simulation_data
    :platform: Unix, Windows
    :synopsis: Data object for storing metadata and parameter about a simulation run in MongoDB, via the Ming ORM.

.. moduleauthor:: Mark E. Madsen <mark@madsenlab.org>

"""

import logging as log
from ming import Session, Field, schema
from ming.declarative import Document
from dbutils import generate_collection_id


__author__ = 'mark'

def _get_dataobj_id():
    """
        Returns the short handle used for this data object in Ming configuration
    """
    return 'simulations'

def _get_collection_id():
    """
    :return: returns the collection name for this data object
    """
    return generate_collection_id("_samples_raw")



def store_stats_axelrod_treestructured(popsize,sim_id,maxinit,learning_rate,
                                 loss_rate, num_trees, branching, depth,ruleclass,popclass,script,
                                 num_cultures,convergence_time,counts,klemm,mean_traits,sd_traits,graphml_blobs):
    """Stores the parameters and metadata for a simulation run in the database.

    """
    AxelrodStatsTreestructured(dict(
        population_size=popsize,
        simulation_run_id=sim_id,
        script_filename=script,
        max_init_traits = maxinit,
        learning_rate = learning_rate,
        loss_rate = loss_rate,
        num_trait_trees = num_trees,
        branching_factor = branching,
        depth_factor = depth,
        rule_class = ruleclass,
        pop_class = popclass,
        num_culture_regions = num_cultures,
        convergence_time = convergence_time,
        culture_counts = counts,
        klemm_normalized_L = klemm,
        mean_trait_num = mean_traits,
        sd_trait_num = sd_traits,
        culture_graphml_repr = graphml_blobs
    )).m.insert()
    return True


class AxelrodStatsTreestructured(Document):

    class __mongometa__:
        session = Session.by_name(_get_dataobj_id())
        name = 'axelrod_stats_treestructured'

    _id = Field(schema.ObjectId)
    script_filename = Field(str)
    max_init_traits = Field(int)
    learning_rate = Field(float)
    num_trait_trees = Field(int)
    branching_factor = Field(int)
    depth_factor = Field(int)
    loss_rate = Field(float)
    rule_class = Field(str)
    pop_class = Field(str)
    population_size = Field(int)
    simulation_run_id = Field(str)
    num_culture_regions = Field(int)
    culture_counts = Field([dict(cultureid=str,count=int)])
    convergence_time = Field(int)
    klemm_normalized_L = Field(float)
    mean_trait_num = Field(float)
    sd_trait_num = Field(float)
    culture_graphml_repr = Field([dict(cultureid=str,content=str)])


