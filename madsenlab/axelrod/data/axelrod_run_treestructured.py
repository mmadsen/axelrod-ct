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


def updateFieldAxelrodStatsTreestructured(record_id, field_name, value):
    record = AxelrodStatsTreestructured.m.find(dict(_id=record_id)).one()
    record[field_name] = value
    record.m.save()



def store_stats_axelrod_treestructured(popsize,sim_id,maxinit,learning_rate,
                                 loss_rate, innov_rate, num_trees, branching, depth,ruleclass,popclass,networkclass,script,
                                 num_cultures,trait_spectrum,convergence_time,sample_time,counts,klemm,mean_traits,sd_traits,graphml_blobs,
                                 trait_stats,trait_rich,trait_entropy,final,swrewiring):
    """Stores the parameters and metadata for a simulation run in the database.

    """
    AxelrodStatsTreestructured(dict(
        population_size=popsize,
        simulation_run_id=sim_id,
        script_filename=script,
        max_init_traits = maxinit,
        learning_rate = learning_rate,
        loss_rate = loss_rate,
        innovation_rate = innov_rate,
        num_trait_trees = num_trees,
        branching_factor = branching,
        depth_factor = depth,
        rule_class = ruleclass,
        pop_class = popclass,
        network_class = networkclass,
        num_culture_regions = num_cultures,
        trait_spectrum=trait_spectrum,
        convergence_time = convergence_time,
        sample_time = sample_time,
        culture_counts = counts,
        klemm_normalized_L = klemm,
        mean_trait_num = mean_traits,
        sd_trait_num = sd_traits,
        culture_graphml_repr = graphml_blobs,
        trait_graph_stats = trait_stats,
        trait_richness = trait_rich,
        trait_evenness_entropy = trait_entropy,
        run_finalized = final,
        sw_rewiring_prob = swrewiring


    )).m.insert()
    return True


def columns_to_export_for_analysis():
    cols = [
        "simulation_run_id",
        "network_class",
        "population_size",
        "max_init_traits",
        "learning_rate",
        "loss_rate",
        "innovation_rate",
        "num_trait_trees",
        "branching_factor",
        "depth_factor",
        "num_culture_regions",
        "run_finalized",
        "sample_time",
        "convergence_time",
        "mean_trait_num",
        "trait_richness",
        "sw_rewiring_prob",
    ]
    return cols


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
    innovation_rate = Field(float)
    rule_class = Field(str)
    pop_class = Field(str)
    network_class = Field(str)
    population_size = Field(int)
    simulation_run_id = Field(str)
    num_culture_regions = Field(int)
    culture_counts = Field([dict(cultureid=str,count=int)])
    trait_spectrum = Field([dict(popcount=int,numtraits=int)])
    convergence_time = Field(int)
    sample_time = Field(int)
    klemm_normalized_L = Field(float)
    mean_trait_num = Field(float)
    sd_trait_num = Field(float)
    culture_graphml_repr = Field([dict(cultureid=str,content=str)])
    trait_graph_stats = Field([dict(cultureid=str,
                                    culture_count=int,
                                    orbit_multiplicities=[int],
                                    orbit_number = float,
                                    autgroupsize = float,
                                    remaining_density = float,
                                    mean_radii = float,
                                    sd_radii = float,
                                    mean_degree = float,
                                    sd_degree = float,
                                    mean_orbit_multiplicity = float,
                                    sd_orbit_multiplicity = float,
                                    max_orbit_multiplicity = int,
                                    order = int,
                                    msg_lambda = float,
                                    msg_beta = float,
                                    mem_beta = float
                                    )])
    trait_richness = Field(float)
    trait_evenness_entropy = Field(float)
    sw_rewiring_prob = Field(float)
    #trait_freq = Field()
    run_finalized = Field(int)




