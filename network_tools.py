import networkx as nx
import numpy as np

def tag2name(obo, obo_id):
    """Add name to obo_id for a more meaningful naming of network nodes"""
    return obo_id + ": " + obo.term(obo_id).name


def relabel_nodes(obo, graph):
    """
    Apply tag2name to all nodes in a graph

    Args:
        obo: OBOOntology for the id to name mapping
        graph: networkx graph
    """
    return nx.relabel_nodes(graph, dict([(name, tag2name(obo, name)) for name in graph.nodes()]))


def build_tree(obo, term, graph=nx.Graph(), maxdepth=None):
    """
    Recursively build a nxnetwork graph starting with 'term'.

    Builds the subgraph using an OBOOntology.

    Args:
        obo: OBOOntology to look up the child_terms
        term: the OBOOntology 'term' to start with
        graph: networkX graph to add the nodes to
        maxdepth: maximal recursion depth
    """
    if maxdepth is not None:
        maxdepth -= 1
        if maxdepth <= 0:
            return graph
    children = obo.child_terms(term)
    for child in children:
        graph.add_edge(term, child.id)
        build_tree(obo, child.id, graph, maxdepth)
    return graph


def build_and_export_tree(obo, term, filename, maxdepth=None, annotation_df=None, df_col='obo_id'):
    """
    Wrapper for build_tree. Build a tree and export it to graphml.
    """
    graph = build_tree(obo, term, nx.Graph(), maxdepth)
    if annotation_df is not None:
        graph = annotate_graph(graph, annotation_df, df_col=df_col)
    graph_ = relabel_nodes(obo, graph)
    print("The graph has {} nodes".format(len(graph_.nodes())))
    nx.write_graphml(graph_, filename)
    return graph_


def annotate_graph(graph, annotation_df, df_col='obo_id'):
    """Add annotation to a networkx graph"""
    for node in graph.nodes():
        row = annotation_df[annotation_df[df_col] == node]
        assert 0 <= len(row.index) <= 2     # 0 if the node is not a sample, 2 if there are technical replicates
        if len(row.index) > 0:
            for colname, value in zip(row.columns.values, row.iloc[0]):  # iloc 0 in case there are technical replicates
                if colname == "name":
                    continue  # dont overwrite native graph attributes
                graph.node[node][colname] = numpy_conv(value)
    return graph


def numpy_conv(var):
    """convert numpy datatype to python's standard data types"""
    if isinstance(var, np.generic):
        return np.asscalar(var)
    else:
        return var