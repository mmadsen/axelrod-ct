#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.



import networkx as nx
import pprint as pp
import logging as log
import subprocess
import math_functions as m
import re




class BalancedTreeAutomorphismStatistics(object):
    """
    Calculates statistics relating to the symmetries of a graph, by determination
    of the graph's automorphism group and orbit structure.  This class relies
    upon Brendan McKay and Adolfo Piperno's nauty and Traces package.

    http://pallini.di.uniroma1.it/index.html

    This class requires that the "dreadnaut" executable from nauty/Traces be
    available somewhere on the execution search path for the simulation process.  This
    code does not install nauty itself.

    The code takes graphs as NetworkX objects, and handles reformatting them for
    nauty internally.

    Statistics are returned in the form of a dict, as in this example:

    { 'orbits' : 5,
      'groupsize' : 2.079483819622e117,
      'graphorder' : 341
      'orbitcounts' : [1, 4, 16, 256]
      'remainingdensity' : 1.0
    }

    Most of these come from nauty output, but the "remainingdensity" statistic is
    the ratio of the measured vertex count, and the number of vertices in a single
    balanced tree of the original configured size.

    """

    # TODO: This code will require additional
    # work when we switch to general graphs for trait structures, because we'll need to be
    # able to identify an "original" graph for every sampled trait graph an individual
    # possesses, and identify them regardless of shape (perhaps with a graph attribute in networkx).


    def __init__(self, simconfig):
        self.simconfig = simconfig
        self.r = int(self.simconfig.branching_factor)
        self.h = int(self.simconfig.depth_factor)
        self.num_trees = self.simconfig.num_trees
        self.n_per_tree = m.num_nodes_balanced_tree(self.r, self.h)



    # EXAMPLE OUTPUT
    #
    # 5 orbits; grpsize=2.079483819622e117; 255 gens; 30388 nodes; maxlev=205
    # cpu time = 0.04 seconds
    #  0; 1:4 (4); 5:20 (16); 21:84 (64); 85:340 (256);

    def _parse_nauty_output(self, raw, graph):
        results = {}

        lines = raw.split('\n')
        numlines = len(lines)
        # orbit number is in the first line, as is grpsize
        onum_pat = re.compile('(\d+) orbit.*;')
        exp_pat = re.compile(r"grpsize=([\d|\.|e|E]+);")
        m = onum_pat.search(lines[0])
        num_orbits = None
        if m:
            num_orbits = int(m.group(1))
            #log.debug("num orbits: %s", num_orbits)
        else:
            log.error("Could not parse number of orbits from nauty output")
        results['orbits'] = num_orbits
        m2 = exp_pat.search(lines[0])
        groupsize = None
        if m2:
            groupsize = float(m2.group(1))
            #log.debug("groupsize: %s", groupsize)
        else:
            log.error("Could not parse groupsize from nauty output")
        results['groupsize'] = groupsize
        single_num = re.compile('\w*(\d+)$')
        multiple_num = re.compile('.*\((\d+)\).*')
        orbit_multiplicites = []
        for lineno in range(2, numlines):
            raw_orbits = lines[lineno].split(';')

            for o in raw_orbits:
                m = single_num.search(o)
                if m:
                    orbit_multiplicites.append(1)
                else:
                    m2 = multiple_num.search(o)
                    if m2:
                        mult = m2.group(1)
                        orbit_multiplicites.append(int(mult))

        #log.debug("multiplicites: %s", orbit_multiplicites)
        results['orbitcounts'] = orbit_multiplicites


        return results



    def calculate_graph_symmetries(self, graph):
        """
        Public API for calculating graph symmetries.  Takes a single networkx graph (usually
        representing a graph of traits and usually single component (although there's no particular
        reason why disconnected graphs will not work).  Returns a dict with symmetry statistics,
        in the format described in the class docstring.
        """

        # we reformat the vertex labels
        g = nx.convert_node_labels_to_integers(graph)

        dread_graph = self._get_dreadnaught_for_graph(g)
        num_vertices = g.number_of_nodes()
        #log.debug("dread: %s", dread_graph)
        raw = self._get_raw_nauty_output(dread_graph)
        #log.debug("raw: %s", raw)

        results = self._parse_nauty_output(raw, g)

        # TODO: Figure out how to handle density and radius for multi-component graphs
        results['remainingdensity'] = float(g.number_of_nodes()) / (float(self.n_per_tree) * float(self.num_trees))


        return results






    def _get_dreadnaught_for_graph(self,graph):
        """
        Constructs a representation of the adjacency structure of the graph in the format
        that dreadnaught/nauty understands.  This employs the networkx "adjlist" format but
        extends it slightly.

        Only adjacency information is preserved in this format -- no additional vertex or edge
        attributes, so "primary" storage of graphs should use the GraphML format.

        """
        linefeed = chr(10)
        n = graph.number_of_nodes()
        dn = "n="
        dn += str(n)
        dn += ' g'
        dn += linefeed
        for line in nx.generate_adjlist(graph):
            edges = line.split()
            #if len(edges) == 1:
            #    dn += ';\n'

            if len(edges) == 1:
                dn += ";"
                dn += linefeed
            else:
                dn += " ".join(edges[1:])
                dn += ";"
                dn += linefeed
        dn += 'x o';
        dn += linefeed
        return dn


    def _format_graph_as_nauty(self, graph):
        """
        Constructs a representation of the adjacency structure of the graph in the format
        that dreadnaught/nauty understands.  This employs the networkx "adjlist" format but
        extends it slightly.

        Only adjacency information is preserved in this format -- no additional vertex or edge
        attributes, so "primary" storage of graphs should use the GraphML format.

        """

        linefeed = chr(10)
        n = graph.number_of_nodes()
        dn = "n="
        dn += str(n)
        dn += ' g'
        dn += linefeed

        for i in range(0, n):
            nlist = graph.neighbors(i)

            # we want to list only vertices which are greater than our own index;
            # any vertices S less than our own index T would have resulted in (S,T)
            # being mentioned when S was processed.
            nlist_greater = [j for j in nlist if j > i]
            if len(nlist_greater) == 1:
                dn += str(i)
                dn += ": "
                dn += str(nlist_greater[0])
                dn += ";"
                dn += linefeed
            elif len(nlist_greater) > 1:
                dn += str(i)
                dn += ": "
                dn += " ".join(map(str,nlist_greater))
                dn += ";"
                dn += linefeed
            else:
                # we don't have to do anything
                pass
        dn += "."
        dn += linefeed
        dn += "x o"
        dn += linefeed
        return dn







    def _get_raw_nauty_output(self,formatted):
        """
        Uses Brendan McKay's nauty/traces package, and specifically the "dreadnaut" program,
        to calculate the raw orbits (and orbit multiplicities) a graph.  This information can
        then be post-processed for a variety of statistics.

        This method assumes that dreadnaut is on the path, and throws an error otherwise.

        """

        try:
            proc = subprocess.Popen(['dreadnaut', '-o', '-m -a'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            raw_output = proc.communicate(formatted)[0]

        except OSError:
            print "This program needs Brendan McKay's nauty program (dreadnaut, specifically) on the path"
            exit(1)

        return raw_output

