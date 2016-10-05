import networkx as nx
from orangecontrib.bio.ontology import OBOOntology
import numpy as np
import re
import itertools


def is_sample_id(obo_id):
    """
    Return true, if the obo_id is the id of a sample, i.e. a leaf of the network.

    The network also contains a lot of 'meta' nodes (i.e. inner nodes) that do not represent a sample,
    but an annotation.
    Samples have an ID FF:?????-?????.
    """
    return re.match(r'FF:(.{5})-(.{5})', obo_id) is not None


def intersects(a, b):
    """Return true if there is an intersection between a and b"""
    return any([i in a for i in b])


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


def build_tree(obo, term, graph=nx.Graph(), maxdepth=None, filter_fun=lambda x: True):
    """
    Recursively build a nxnetwork graph starting with 'term' (top-down).

    Builds the subgraph using an OBOOntology.

    Args:
        obo: OBOOntology to look up the child_terms
        term: the OBOOntology 'term' to start with
        graph: networkX graph to add the nodes to
        maxdepth: maximal recursion depth
        filter_fun: call back function on term.id, return True to include the element, False to exclude.
    """
    if maxdepth is not None:
        maxdepth -= 1
        if maxdepth <= 0:
            return graph
    children = obo.child_terms(term)
    for child in children:
        if filter_fun(child.id):
            graph.add_edge(term, child.id)
            build_tree(obo, child.id, graph, maxdepth)
    return graph


def build_and_export_tree(obo, term, filename, maxdepth=None, annotation_df=None, df_col='obo_id', filter_fun=lambda x: True):
    """
    Wrapper for build_tree. Build a tree and export it to graphml.
    """
    graph = build_tree(obo, term, nx.Graph(), maxdepth, filter_fun=filter_fun)
    if annotation_df is not None:
        graph = annotate_graph(graph, annotation_df, df_col=df_col)
    graph_ = relabel_nodes(obo, graph)
    print("The graph has {} nodes".format(len(graph_.nodes())))
    nx.write_graphml(graph_, filename)
    return graph_


def add_superelements_to_graph(obo, term, graph, delimiter_nodes, inclusive=False):
    """
    Add all elements from ontology that are superelements of term and children of `delimiter_nodes`.

    see build_tree_bottom_up_with_delimiters for more detailed explanation.

    Args:
        obo: OBOOntology
        term: obo id, add the superelements of this term
        graph: networkx graph to add the elements to. Nodes must be named with obo-ids
        delimiter_nodes: list of nodes that serve as stopping criterion.
    """
    parent_ids = [t.id for t in obo.parent_terms(term)]
    super_term_ids = {parent_id: [t.id for t in obo.super_terms(parent_id)] for parent_id in parent_ids}
    if inclusive:
        for parent_id in super_term_ids:
            # add parent to list of 'potential superelements'.
            # recursion will no be aborted when parent element is reached, but it will also be added
            super_term_ids[parent_id].append(parent_id)
    if intersects(delimiter_nodes, parent_ids):
        # is there are other delimiter nodes closer to the root we must continue, since
        # we want to include these as well
        if not intersects(delimiter_nodes, itertools.chain(*super_term_ids.values())):
            return graph
    for parent_id in parent_ids:
        if intersects(delimiter_nodes, super_term_ids[parent_id]):
            graph.add_edge(term, parent_id)
            add_superelements_to_graph(obo, parent_id, graph, delimiter_nodes, inclusive)
    return graph


def build_tree_bottom_up(obo, term, graph, max_depth=None, filter_fun=lambda x: True):
    """Add all parents of term to the graph with respect to max_depth and filter_fun"""
    parent_ids = [t.id for t in obo.parent_terms(term)]
    if max_depth is None or max_depth > 0:
        for parent_id in parent_ids:
            if filter_fun(parent_id):
                graph.add_edge(term, parent_id)
                build_tree_bottom_up(obo, parent_id, graph, max_depth=None if max_depth is None else max_depth-1, filter_fun=filter_fun)
    return graph


def build_tree_bottom_up_with_delimiters(obo, term, graph, delimiter_nodes):
    """
    Add all elements from ontology that are superelements of term and children
    of all delimiter nodes on the same branch.

    This is essentially the same as add_superelements_to_graph, except that that
    function considers children of *any* delimiter node.

    Example:
         ---------- A ---------
        |                      |
        B[delim]               E
        |                      |
        C                      F[delim]
        |
        D[delim]

    This method will add only A and E, as B and F are delimiter nodes and excluded.
    add_superelements_to_graph will add A, B, C, E.

    Args:
        obo: OBOOntology
        term: obo id, add the superelements of this term
        graph: networkx graph to add the elements to. Nodes must be named with obo-ids
        delimiter_nodes: list of nodes that serve as stopping criterion.

    >>> obo = OBOOntology()
    >>> obo.load(open("test/testdata/dummy_ontology.obo"))
    >>> graph = nx.Graph()
    >>> graph = build_tree_bottom_up_with_delimiters(obo, "A", graph, ["B", "D", "F"])
    >>> sorted(graph.nodes())
    ['A', 'E']
    >>> graph = nx.Graph()
    >>> graph = add_superelements_to_graph(obo, "A", graph, ["B", "D", "F"])
    >>> sorted(graph.nodes())
    ['A', 'B', 'C', 'E']
    >>> graph = nx.Graph()
    >>> graph = add_superelements_to_graph(obo, "A", graph, ["B", "D", "F"], inclusive=True)
    >>> sorted(graph.nodes())
    ['A', 'B', 'C', 'D', 'E', 'F']
    >>> graph = nx.Graph()
    >>> graph = build_tree_bottom_up(obo, "A", graph, max_depth=2)
    >>> sorted(graph.nodes())
    ['A', 'B', 'C', 'E', 'F']
    """
    parent_ids = [t.id for t in obo.parent_terms(term)]
    for parent_id in parent_ids:
        # if a parent is in delimiter_nodes we discard that branch.
        if parent_id not in delimiter_nodes:
            graph.add_edge(term, parent_id)
            build_tree_bottom_up_with_delimiters(obo, parent_id, graph, delimiter_nodes)
    return graph

