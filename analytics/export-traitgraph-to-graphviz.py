#!/usr/bin/env python

# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

import ming

import logging as log
import argparse
import madsenlab.axelrod.utils as utils
import madsenlab.axelrod.data as data




## setup

def setup():
    global args, config, simconfig
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="provide name for experiment, to be used as prefix for database collections")
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--dbhost", help="database hostname, defaults to localhost", default="localhost")
    parser.add_argument("--dbport", help="database port, defaults to 27017", default="27017")
    parser.add_argument("--finalized", help="Only export runs which finalized after convergence", action="store_true")
    parser.add_argument("--action", choices=["sample", "single", "bulk"])
    parser.add_argument("--ssize", help="Sample size of graphs to export", default="100")
    parser.add_argument("--id", help="Export trait graphs with this object id")
    parser.add_argument("--idfile", help="Export trait graphs for ids in file")
    parser.add_argument("--directory", help="Directory to which DOT files are written")

    args = parser.parse_args()


    if args.debug == 1:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')


    #### main program ####
    log.info("EXPORT TRAIT GRAPHS AS DOT - Experiment: %s", args.experiment)
    data.set_experiment_name(args.experiment)
    data.set_database_hostname(args.dbhost)
    data.set_database_port(args.dbport)
    config = data.getMingConfiguration(data.modules)
    ming.configure(**config)



if __name__ == "__main__":
    setup()

    if args.action == "sample":
        ssize = int(args.ssize)
        log.info("Exporting random samples of trait graphs from %s records, finalization %s", ssize, args.finalized)

        utils.convert_random_traitgraphs_to_dot(ssize,args.directory,args.finalized)
    elif args.action == "single":
        utils.convert_single_traitgraph_to_dot(args.id,001,args.directory)
    elif args.action == "bulk":
        pass
    else:
        log.error("Should not happen - action must be a defined constant")


