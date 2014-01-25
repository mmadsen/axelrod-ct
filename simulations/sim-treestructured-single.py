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
import madsenlab.axelrod.analysis as analysis
import madsenlab.axelrod.data as data
import madsenlab.axelrod.rules as rules
import pprint as pp

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
    parser.add_argument("--maxinittraits", help="Max initial number of traits per indiv", required=True)
    parser.add_argument("--learningrate", help="Rate at which traits are learned during interactions", required=True)
    parser.add_argument("--lossrate", help="Rate at which traits are lost randomly by individuals (0.0 turns this off)", required=True)
    parser.add_argument("--innovrate", help="Rate at which innovations occur in population", required=True)
    parser.add_argument("--periodic", help="Periodic boundary condition", choices=['1','0'], required=True)
    parser.add_argument("--diagram", help="Draw a diagram of the converged model", action="store_true")
    parser.add_argument("--drift_rate", help="Rate of drift")
    parser.add_argument("--numtraittrees", help="Number of trait trees in the design space", required=True)
    parser.add_argument("--branchingfactor", help="Value or mean for tree branching factor", required=True)
    parser.add_argument("--depthfactor", help="Value or mean for tree depth factor", required=True)



    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)

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
    simconfig.maxtraits = int(args.maxinittraits)
    simconfig.learning_rate = float(args.learningrate)
    simconfig.num_trees = int(args.numtraittrees)
    simconfig.branching_factor = float(args.branchingfactor)
    simconfig.depth_factor = float(args.depthfactor)
    simconfig.loss_rate = float(args.lossrate)
    simconfig.innov_rate = float(args.innovrate)
    simconfig.maxtime = simconfig.SIMULATION_CUTOFF_TIME
    simconfig.script = __file__

    simconfig.sim_id = uuid.uuid4().urn
    if args.periodic == '1':
        simconfig.periodic = 1
    elif args.periodic == '0':
        simconfig.periodic = 0


def main():
    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.debug("Configuring Axelrod model with structure class: %s graph factory: %s interaction rule: %s", structure_class_name, simconfig.NETWORK_FACTORY_CLASS, simconfig.INTERACTION_RULE_CLASS)


    #log.debug("Run for popsize %s  maxinittraits: %s, addrate: %s, ", simconfig.popsize,  simconfig.maxtraits, simconfig.add_rate)


    model_constructor = utils.load_class(structure_class_name)
    rule_constructor = utils.load_class(simconfig.INTERACTION_RULE_CLASS)
    graph_factory_constructor = utils.load_class(simconfig.NETWORK_FACTORY_CLASS)
    trait_factory_constructor = utils.load_class(simconfig.TRAIT_FACTORY_CLASS)

    graph_factory = graph_factory_constructor(simconfig)
    trait_factory = trait_factory_constructor(simconfig)

    model = model_constructor(simconfig, graph_factory, trait_factory)
    model.initialize_population()

    #counts = analysis.get_culture_counts(model)


    log.info("population initialization complete - beginning simulation run")

    ax = rule_constructor(model)

    timestep = 0
    last_interaction = 0

    while(1):
        timestep += 1
        ax.step(timestep)
        if (timestep % 100000) == 0:
            log.debug("time: %s  active: %s  copies: %s  innov: %s losses: %s", timestep, ax.get_fraction_links_active(), model.get_interactions(), model.get_innovations(), model.get_losses())
        if timestep > 250000 and timestep % 250000  == 0:
            utils.sample_treestructured_model(model, args, simconfig, finalized=0)
        if model.get_time_last_interaction() != timestep:
            live = utils.check_liveness(ax, model, args, simconfig, timestep)
            if live == False:
                utils.sample_treestructured_model(model, args, simconfig, finalized=1)
                exit(0)

        # if the simulation is cycling endlessly, and after the cutoff time, sample and end
        if timestep > simconfig.maxtime:
            log.info("Simulation has not converged within %s, taking final sample and terminating", simconfig.maxtime)
            utils.sample_treestructured_model(model, args, simconfig, finalized=0)
            exit(0)

# end main




if __name__ == "__main__":
    setup()
    main()

