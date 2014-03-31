#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
import madsenlab.axelrod.analysis as stats
import networkx as nx

def generate_forest_balanced_trees(r, h, n):
    graphs = []
    roots = []
    num_nodes = stats.num_nodes_balanced_tree(r, h)
    starting_num = 0
    for i in range(0, n):
        #log.debug("building tree with starting root: %s", starting_num)
        g = nx.balanced_tree(r, h)
        g = nx.convert_node_labels_to_integers(g, first_label=starting_num)

        #log.debug("nodes: %s", pp.pformat(g.nodes()))

        graphs.append(g)
        roots.append(starting_num)
        starting_num += num_nodes
    trees = nx.union_all(graphs)
    return (trees, roots)
