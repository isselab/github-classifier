import unittest
from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes
from EcoreToMatrixConverter import EcoreToMatrixConverter

class TestETMConv(unittest.TestCase):
    def test_etmconv(self):
        repo = 'test/unit_test_repo/testRepo1'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        #print(node_features, edges)


unittest.main()