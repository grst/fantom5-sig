import networkx as nx


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
    """
    if maxdepth is not None:
        maxdepth -= 1
        if maxdepth <= 0:
            return graph
    for child in obo.child_terms(term):
        graph.add_edge(term, child.id)
        build_tree(obo, child.id, graph, maxdepth)
    return graph


def build_and_export_tree(obo, term, filename, maxdepth=None):
    """
    Wrapper for build_tree. Build a tree and export it to graphml.
    """
    graph = build_tree(obo, term, nx.Graph(), maxdepth)
    graph_ = relabel_nodes(obo, graph)
    print("The graph has {} nodes".format(len(graph_.nodes())))
    nx.write_graphml(graph_, filename)