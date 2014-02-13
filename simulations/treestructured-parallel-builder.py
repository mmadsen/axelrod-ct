#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""


import logging as log
import argparse
import itertools
import madsenlab.axelrod.utils as utils




def setup():
    global args, simconfig

    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", help="provide name for experiment", required=True)
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)
    parser.add_argument("--parallelism", help="Number of concurrent processes to run", default="4")

    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)

    if args.debug == '1':
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    log.debug("experiment name: %s", args.experiment)



def main():

    structure_class_name = simconfig.POPULATION_STRUCTURE_CLASS
    log.info("Configuring TreeStructured Axelrod model with structure class: %s", structure_class_name)


    log.debug("Opening %s output files given parallelism", args.parallelism)
    num_files = int(args.parallelism)
    file_list = []
    base_name = "simrunner-exp-"
    base_name += args.experiment
    base_name += "-"

    for i in range(0, num_files):
        filename = ''
        filename += base_name
        filename += str(i)
        filename += ".py"

        f = open(filename, 'w')

        f.write("#!/bin/sh\n\n")
        file_list.append(f)

    file_cycle = itertools.cycle(file_list)


    basic_config = utils.TreeStructuredConfiguration(args.configuration)

    if basic_config.INTERACTION_RULE_CLASS == 'madsenlab.axelrod.rules.MultipleTreePrerequisitesLearningCopyingRule':
        state_space = [
            basic_config.POPULATION_SIZES_STUDIED,
            basic_config.TRAIT_LEARNING_RATE,
            basic_config.MAXIMUM_INITIAL_TRAITS,
            basic_config.NUM_TRAIT_TREES,
            basic_config.TREE_BRANCHING_FACTOR,
            basic_config.TREE_DEPTH_FACTOR,
            basic_config.TRAIT_LOSS_RATE,
            basic_config.INNOVATION_RATE,
        ]
    else:
        log.error("This parallel sim runner not compatible with rule class: %s", basic_config.INTERACTION_RULE_CLASS)
        exit(1)


    if basic_config.NETWORK_FACTORY_CLASS == 'madsenlab.axelrod.population.WattsStrogatzSmallWorldFactory':
        state_space.append(basic_config.WS_REWIRING_FACTOR)


    for param_combination in itertools.product(*state_space):
        for replication in range(0, basic_config.REPLICATIONS_PER_PARAM_SET):
            cmd = "simulations/sim-treestructured-single.py "
            cmd += " --experiment "
            cmd += args.experiment
            cmd += " --configuration "
            cmd += args.configuration
            cmd += " --popsize "
            cmd += str(param_combination[0])
            cmd += " --maxinittraits "
            cmd += str(param_combination[2])
            cmd += " --learningrate "
            cmd += str(param_combination[1])
            cmd += " --lossrate "
            cmd += str(param_combination[6])
            cmd += " --innovrate "
            cmd += str(param_combination[7])
            cmd += " --periodic 0 "
            cmd += " --numtraittrees "
            cmd += str(param_combination[3])
            cmd += " --branchingfactor "
            cmd += str(param_combination[4])
            cmd += " --depthfactor "
            cmd += str(param_combination[5])
            cmd += " --debug "
            cmd += args.debug

            if len(param_combination) == 9:
                cmd += " --swrewiring "
                cmd += str(param_combination[8])

            cmd += '\n'

            fc = file_cycle.next()
            fc.write(cmd)


    for fh in file_list:
        fh.close()


if __name__ == "__main__":
    setup()
    main()


