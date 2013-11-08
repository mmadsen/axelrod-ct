#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import logging as log
import ming
import argparse
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.data as data



def setup():
    global args, simconfig

    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", help="provide name for experiment", required=True)
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)

    args = parser.parse_args()

    simconfig = utils.AxelrodConfiguration(args.configuration)

    if args.debug:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    log.debug("experiment name: %s", args.experiment)
    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration()
    ming.configure(**config)




def main():


    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.info("Configuring Axelrod model with structure class: %s", structure_class_name)

    state_space = [
        simconfig.POPULATION_SIZES_STUDIED,
        simconfig.NUMBER_OF_DIMENSIONS_OR_FEATURES,
        simconfig.NUMBER_OF_TRAITS_PER_DIMENSION,
        simconfig.STRUCTURE_PERIODIC_BOUNDARY
    ]

