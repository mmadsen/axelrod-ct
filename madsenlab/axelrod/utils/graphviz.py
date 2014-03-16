#!/usr/bin/env python
# Copyright (c) 2013.  Mark E. Madsen <mark@madsenlab.org>
#
# This work is licensed under the terms of the Apache Software License, Version 2.0.  See the file LICENSE for details.

"""
Description here

"""
from networkx.utils import open_file, make_str
import networkx as nx
import re
import madsenlab.axelrod.data as data
import logging as log
import random
import math
from bson.objectid import ObjectId


# god help us if there are more than 999,999 frames in a video of graphs...
FORMAT_STRING_MAP = {
    0 : "%01d",
    1 : "%01d",
    2 : "%02d",
    3 : "%03d",
    4 : "%04d",
    5 : "%05d",
    6 : "%06d"
}



def convert_single_traitgraph_to_dot(record_id, rec_num, directory):
    format_string = FORMAT_STRING_MAP[1]
    convert_traitgraph_to_dot(record_id,1,format_string,directory)



def convert_traitgraph_to_dot(record_id, rec_num, format_string, directory):
    query = dict()
    query['_id'] = ObjectId(record_id)
    res = data.AxelrodStatsTreestructured.m.find(query)

    for result in res:
        graph_list = result['culture_graphml_repr']
        graphs = []
        for g in graph_list:
            g_c = g['content']
            graph = nx.parse_graphml(g_c)
            graphs.append(graph)

        for i in range(0, len(graphs)):
            fname = directory
            fname += "/sample-"
            fname += format_string % rec_num
            fname += "-"
            fname += str(record_id)
            fname += ".dot"
            write_ordered_dot(graphs[i], fname, str(record_id))





def convert_random_traitgraphs_to_dot(ssize, directory, finalize=True):
    id_list = []
    query = dict()
    if finalize == True:
        query['run_finalized'] = 1

    id_cursor = data.AxelrodStatsTreestructured.m.find(query)
    for entry in id_cursor:
        id_list.append(entry._id)

    log.info("id_list len: %s", len(id_list))

    l = math.log10(ssize)
    key = int(math.ceil(l))
    format_string = FORMAT_STRING_MAP[key]

    rec = 0
    selected_ids = random.sample(id_list, ssize)
    for id in selected_ids:
        convert_traitgraph_to_dot(id, rec, format_string, directory)
        rec += 1





@open_file(1,mode='w')
def write_ordered_dot(N,path,name=None):
    """Write NetworkX graph G to Graphviz dot format on path.

    Path can be a string or a file handle.
    """
    try:
        import pydot
    except ImportError:
        raise ImportError("write_dot() requires pydot",
                          "http://code.google.com/p/pydot/")
    P=generate_ordered_dot(N, name)

    title_string = "\nlabelloc=\'t\';label=\'%s\';}\n" % name

    p = P.to_string();
    # p2 = re.sub("\n\}\n", "", p)
    # p2 += "\nlabelloc=\"t\";\n"
    # p2 += "label=\"%s\";\n}\n" % name
    path.write(p)
    return




def generate_ordered_dot(N, name=None):
    """
    The networkx write_dot() function generates
    """
    try:
        import pydot
    except ImportError:
        raise ImportError('to_pydot() requires pydot: '
                          'http://code.google.com/p/pydot/')

    # set Graphviz graph type
    if N.is_directed():
        graph_type='digraph'
    else:
        graph_type='graph'
    strict=N.number_of_selfloops()==0 and not N.is_multigraph()

    node_attrs = dict()
    node_attrs["shape"] = "circle"
    node_attrs["width"] = "0.1"
    node_attrs["height"] = "0.1"
    node_attrs["fixedsize"] = "true"
    node_attrs["label"] = ""

    graph_defaults=N.graph.get('graph',{})
    graph_defaults["ratio"] = "auto"
    graph_defaults["labelloc"] = "t"
    graph_defaults["label"] = name
    graph_defaults["pad"] = "1.0"


    if name is None:
        P = pydot.Dot(graph_type=graph_type,strict=strict,**graph_defaults)
    else:
        P = pydot.Dot('"%s"'%name,graph_type=graph_type,strict=strict,
                      **graph_defaults)
    try:
        P.set_node_defaults(**node_attrs)
    except KeyError:
        pass
    try:
        P.set_edge_defaults(**N.graph['edge'])
    except KeyError:
        pass

    for n,nodedata in sorted(N.nodes_iter(data=True), key=lambda n: int(n[0])):
        str_nodedata=dict((k,make_str(v)) for k,v in nodedata.items())
        p=pydot.Node(make_str(n),**str_nodedata)
        P.add_node(p)

    if N.is_multigraph():
        for u,v,key,edgedata in N.edges_iter(data=True,keys=True):
            str_edgedata=dict((k,make_str(v)) for k,v in edgedata.items())
            edge=pydot.Edge(make_str(u),make_str(v),key=make_str(key),**str_edgedata)
            P.add_edge(edge)

    else:



        for u,v,edgedata in sorted(N.edges_iter(data=True), key=lambda u: int(u[0]) ):
            str_edgedata=dict((k,make_str(v)) for k,v in edgedata.items())
            if int(v) < int(u):
                edge = pydot.Edge(make_str(v),make_str(u),**str_edgedata)
            else:
                edge=pydot.Edge(make_str(u),make_str(v),**str_edgedata)
            P.add_edge(edge)
    return P


