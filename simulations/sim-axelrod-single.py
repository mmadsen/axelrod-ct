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
import madsenlab.axelrod.analysis as stats
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
    parser.add_argument("--diagram", help="Draw a diagram of the converged model", action="store_true")

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
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)

    simconfig.popsize = int(args.popsize)
    simconfig.num_features = int(args.features)
    simconfig.num_traits = int(args.traits)


def main():
    global sim_id
    sim_id = uuid.uuid4().urn

    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.info("Configuring Axelrod model with structure class: %s", structure_class_name)


    log.info("Run for popsize %s  features: %s, traits: %s", simconfig.popsize,
             simconfig.num_features, simconfig.num_traits)


    model_constructor = utils.load_class(structure_class_name)

    model = model_constructor(simconfig)
    model.initialize_population()

    ax = rules.AxelrodRule(model)

    timestep = 0
    last_interaction = 0

    while(1):
        timestep += 1
        if(timestep % 10000 == 0):
            log.info("time: %s  frac active links %s", timestep, ax.get_fraction_links_active())
        ax.step(timestep)
        if model.get_time_last_interaction() != timestep:
            check_liveness(ax, model, timestep)


# end main



def check_liveness(ax, model, timestep):
    diff = timestep - model.get_time_last_interaction()
    num_links = model.model.number_of_edges()

    if (diff > (5 * num_links)):
        log.info("No interactions have occurred for %s ticks, which is 5 * %s network edges", diff, num_links)
        if ax.get_fraction_links_active() == 0.0:
            log.info("No active links found in the model, finalizing")
            finalize_model(model, simconfig)
            if args.diagram == True:
                model.draw_network_colored_by_culture()
            exit(0)
        else:
            pass
    else:
        pass


def finalize_model(model,simconfig):
    counts = stats.get_culture_counts(model)
    data.store_stats_axelrod_original(simconfig.popsize,None,sim_id,simconfig.num_features,simconfig.num_traits,__file__,len(counts),model.get_time_last_interaction(),counts)




if __name__ == "__main__":
    setup()
    main()

