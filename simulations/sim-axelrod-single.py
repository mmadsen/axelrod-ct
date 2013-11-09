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
import networkx as nx
import matplotlib.pyplot as plt




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

    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.info("Configuring Axelrod model with structure class: %s", structure_class_name)


    log.info("Run for popsize %s  features: %s, traits: %s", simconfig.popsize,
             simconfig.num_features, simconfig.num_traits)


    model_constructor = utils.load_class(structure_class_name)

    model = model_constructor(simconfig)
    model.initialize_population()

    axelrod = rules.AxelrodRule(model)

    timestep = 0
    last_interaction = 0

    while(1):
        timestep += 1
        if(timestep % 100000 == 0):
            log.info("time: %s", timestep)
        axelrod.step(timestep)
        if model.get_time_last_interaction() != timestep:
            check_liveness(model, timestep)




def check_liveness(model, timestep):
    diff = timestep - model.get_time_last_interaction()
    num_links = model.model.number_of_edges()

    if (diff > (2 * num_links)):
        log.info("No interactions have occurred for %s ticks, which is 2 * %s network edges", diff, num_links)
        nodes,colors=zip(*nx.get_node_attributes(model.model,'traits').items())
        color_tupled_compressed = [int(''.join(str(i) for i in t)) for t in colors]
        nodes,pos = zip(*nx.get_node_attributes(model.model, 'pos').items())
        nx.draw(model.model,pos=pos,nodelist=nodes,node_color=color_tupled_compressed)
        plt.show()
        finalize_model(model, timestep)
    else:
        pass


def finalize_model(model, timestep):
    exit(0)



if __name__ == "__main__":
    setup()
    main()

