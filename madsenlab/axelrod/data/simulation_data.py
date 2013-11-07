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
import madsenlab.axelrod.data as data

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
    return data.generate_collection_id("_samples_raw")



def storeSimulationData(popsize,mutation,sim_id,num_features,num_traits_per_feature,replicates,script):
    """Stores the parameters and metadata for a simulation run in the database.

        Args:

            popsize (int):  Population size

            sim_id (str):  UUID for this simulation run

            num_features (int):  Number of loci/dimensions/features per agent

            num_traits_per_feature (int): Number of traits per feature

            replicates (int):  Number of independent populations to evolve with the same set of parameters

            script (str):  Pathname to the simuPOP simulation script used for this simulation run

        Returns:

            Boolean true:  all PyOperators need to return true.

    """
    SimulationRun(dict(
        replicates=replicates,
        population_size=popsize,
        simulation_run_id=sim_id,
        script_filename=script,
        num_features = num_features,
        num_traits_per_feature = num_traits_per_feature
    )).m.insert()
    return True


class SimulationRun(Document):

    class __mongometa__:
        session = Session.by_name(_get_dataobj_id())
        name = 'simulation_runs'

    _id = Field(schema.ObjectId)
    script_filename = Field(str)
    replicates = Field(int)
    num_features = Field(int)
    num_traits_per_feature = Field(int)
    population_size = Field(int)
    simulation_run_id = Field(str)


