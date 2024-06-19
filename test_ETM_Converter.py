import unittest
from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes
from EcoreToMatrixConverter import EcoreToMatrixConverter

'''(hashed) name not a feature right now, therefore it is missing in tests, 
might chage later'''

class TestETMConv(unittest.TestCase):

    def test_package(self):
        repo = 'tests/unit_tests/test_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 1, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(len(edges), 0, 'single package should not have edge')
        self.assertEqual(len(enc_node_features), 1, 'wrong number of encoded nodes')
        self.assertEqual(len(enc_node_features[0]), 8, 'error in ohe encoding, total number of node types wrong')
        self.assertEqual(enc_node_features[0][6], 1.0, 'package node not set in encoding')
        self.assertEqual(enc_node_features[0][0], 0.0, 'call node set in encoding')
        self.assertEqual(enc_node_features[0][1], 0.0, 'class node set in encoding')
        self.assertEqual(enc_node_features[0][2], 0.0, 'method node set in encoding')
        self.assertEqual(enc_node_features[0][3], 0.0, 'method definition node set in encoding')
        self.assertEqual(enc_node_features[0][4], 0.0, 'method signature node set in encoding')
        self.assertEqual(enc_node_features[0][5], 0.0, 'module node set in encoding')
        self.assertEqual(enc_node_features[0][7], 0.0, 'parameter node set in encoding')

    def test_subpackage(self):
        repo = 'tests/unit_tests/test_subpackage'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(len(edges), 1, 'single package should not have edge')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')
        self.assertEqual(edges[0], [0, 1], 'edge between package and subpackage wrong')

    def test_module(self):
        repo = 'tests/unit_tests/test_module'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 1, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(len(edges), 0, 'single module should not have edge')
        self.assertEqual(len(enc_node_features), 1, 'wrong number of encoded nodes')
        self.assertEqual(len(enc_node_features[0]), 8, 'error in ohe encoding, total number of node types wrong')
        self.assertEqual(enc_node_features[0][6], 0.0, 'package node set in encoding')
        self.assertEqual(enc_node_features[0][0], 0.0, 'call node set in encoding')
        self.assertEqual(enc_node_features[0][1], 0.0, 'class node set in encoding')
        self.assertEqual(enc_node_features[0][2], 0.0, 'method node set in encoding')
        self.assertEqual(enc_node_features[0][3], 0.0, 'method definition node set in encoding')
        self.assertEqual(enc_node_features[0][4], 0.0, 'method signature node set in encoding')
        self.assertEqual(enc_node_features[0][5], 1.0, 'module node not set in encoding')
        self.assertEqual(enc_node_features[0][7], 0.0, 'parameter node set in encoding')

    def test_multiple_modules(self):
        repo = 'tests/unit_tests/test_multiple_modules'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(len(edges), 0, 'module should not have edge to another module')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')

unittest.main()