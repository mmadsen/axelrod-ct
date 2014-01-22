#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.


import networkx as nx
import argparse
import logging as log
import pprint as pp
import madsenlab.axelrod.analysis as analysis
import madsenlab.axelrod.utils as utils


def setup():
    global args, simconfig

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="turn on debugging output")
    parser.add_argument("--configuration", help="Configuration file for experiment", required=True)

    args = parser.parse_args()

    simconfig = utils.TreeStructuredConfiguration(args.configuration)

    if args.debug == '1':
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    else:
        log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s: %(message)s')



def main():
    simconfig.branching_factor = 4
    simconfig.depth_factor = 4
    stats = analysis.BalancedTreeAutomorphismStatistics(simconfig)

    g2 = nx.balanced_tree(simconfig.branching_factor, simconfig.depth_factor)
    r2 = stats.calculate_graph_symmetries(g2)
    log.info("results: %s", r2)



if __name__ == "__main__":
    setup()
    main()
