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
import madsenlab.axelrod.rules as rules

import uuid




def setup():
    global args, simconfig

    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", help="provide name for experiment", required=True)
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)
    parser.add_argument("--popsize", help="Population size", required=True)
    parser.add_argument("--features", help="Number of features (int >= 1)", required=True)
    parser.add_argument("--traits", help="Number of traits (int > 1)", required=True)
    parser.add_argument("--periodic", help="Periodic boundary condition", choices=['1','0'], required=True)
    parser.add_argument("--diagram", help="Draw a diagram of the converged model", action="store_true")
    parser.add_argument("--drift_rate", help="Rate of drift")


    args = parser.parse_args()

    simconfig = utils.AxelrodConfiguration(args.configuration)

    if args.debug == '1':
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    log.debug("experiment name: %s", args.experiment)
    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)

    if args.drift_rate:
        simconfig.drift_rate = float(args.drift_rate)

    simconfig.popsize = int(args.popsize)
    simconfig.num_features = int(args.features)
    simconfig.num_traits = int(args.traits)

    simconfig.sim_id = uuid.uuid4().urn
    if args.periodic == '1':
        simconfig.periodic = 1
    elif args.periodic == '0':
        simconfig.periodic = 0


def main():
    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.debug("Configuring Axelrod model with structure class: %s graph factory: %s interaction rule: %s", structure_class_name, simconfig.NETWORK_FACTORY_CLASS, simconfig.INTERACTION_RULE_CLASS)


    log.debug("Run for popsize %s  features: %s, traits: %s", simconfig.popsize,
             simconfig.num_features, simconfig.num_traits)


    model_constructor = utils.load_class(structure_class_name)
    rule_constructor = utils.load_class(simconfig.INTERACTION_RULE_CLASS)
    graph_factor_constructor = utils.load_class(simconfig.NETWORK_FACTORY_CLASS)

    graph_factory = graph_factor_constructor(simconfig)

    model = model_constructor(simconfig, graph_factory)
    model.initialize_population()

    ax = rule_constructor(model)

    timestep = 0
    last_interaction = 0

    while(1):
        timestep += 1
        if(timestep % 10000 == 0):
            log.debug("time: %s  frac active links %s", timestep, ax.get_fraction_links_active())
        ax.step(timestep)
        if model.get_time_last_interaction() != timestep:
            live = utils.check_liveness(ax, model, args, simconfig, timestep)
            if live == False:
                utils.finalize_axelrod_model(model, args, simconfig)
                exit(0)

# end main




if __name__ == "__main__":
    setup()
    main()

