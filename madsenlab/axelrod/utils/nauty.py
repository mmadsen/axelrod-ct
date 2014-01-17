#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Interfaces and methods for interoperating with Brendan McKay's nauty software, which performs
canonical labeling and graph automorphism computation for graphs and networks.

http://pallini.di.uniroma1.it/index.html

"""

import networkx as nx
import pprint as pp
import logging as log


def get_dreadnaught_for_graph(graph):
    """
    Constructs a representation of the adjacency structure of the graph in the format
    that dreadnaught/nauty understands.  This employs the networkx "adjlist" format but
    extends it slightly.

    Only adjacency information is preserved in this format -- no additional vertex or edge
    attributes, so "primary" storage of graphs should use the GraphML format.

    """
    n = graph.number_of_nodes()
    dn = "n="
    dn += str(n)
    dn += ' g\n'
    for line in nx.generate_adjlist(graph):
        #edges = line.split()
        #if len(edges) == 1:
        #    dn += ';\n'
        #    break
        #dn += " ".join(edges[1:])
        dn += line
        dn += ';\n'
    dn += 'x\n';
    return dn


