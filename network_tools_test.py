from unittest import TestCase
from orangecontrib.bio.ontology import OBOOntology, OBOObject
import pandas as pd
import networkx as nx
from network_tools import *


class TestNetworkTools(TestCase):
    def test_add_superelements_to_graph(self):
        obo_corr = OBOOntology()
        obo_corr.load(open("testdata/ff-phase2-140729.obo"))
        col_vars = pd.read_csv("testdata/column_vars.processed.csv", index_col=0)

        # it should produce equal results if the superelements are applied sequencially
        # or ar using a set or delimtier nodes.
        graph1 = nx.Graph()
        graph2 = nx.Graph()
        for obo_id in col_vars.obo_id:
            graph1.add_node(obo_id)
            graph2.add_node(obo_id)
        delimiter_nodes = [
            "FF:0000002",  # in vivo cell sample
            "FF:0000004",  # tissue sample
            "FF:0000003",  # cell line sample
            "FF:0000210",  # human sample
        ]
        for node in graph1.nodes():
            add_superelements_to_graph(obo_corr, node, graph1, delimiter_nodes)
        for node in graph2.nodes():
            for delimiter_node in delimiter_nodes:
                add_superelements_to_graph(obo_corr, node, graph2, [delimiter_node])
        set1 = set(graph1.nodes())
        set2 = set(graph2.nodes())
        self.assertEqual(set1, set2)

