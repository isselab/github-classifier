import unittest
import sys
import os
 
#getting the name of the directory where this file is
current = os.path.dirname(os.path.realpath(__file__))
 
#getting the parent directory name where the current directory is
parent = os.path.dirname(current)
 
#adding the parent directory to the sys.path.
sys.path.append(parent)

from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes
from EcoreToMatrixConverter import EcoreToMatrixConverter
from EdgeAttributes import EdgeTypes
from test_utils import check_path_exists

'''the tests for the second converter are the same as for the first,
the hashed node names have their own test, and edge attributes are added and tested'''

class TestETMConv(unittest.TestCase):

    #missing file
    def test_package(self):
        repo = 'unit_tests/test_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 1, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(len(edges), 0, 'single package should not have edge')
        self.assertEqual(len(edge_attributes), 0, 'wrong number of edge attributes')
        self.assertEqual(len(enc_node_features), 1, 'wrong number of encoded nodes')
        self.assertEqual(len(enc_node_features[0]), 8, 'error in ohe encoding, total number of node types wrong')

        #test ohe encoding for node type package
        self.assertEqual(enc_node_features[0][6], 1.0, 'package node not set in encoding')
        self.assertEqual(enc_node_features[0][0], 0.0, 'call node set in encoding')
        self.assertEqual(enc_node_features[0][1], 0.0, 'class node set in encoding')
        self.assertEqual(enc_node_features[0][2], 0.0, 'method node set in encoding')
        self.assertEqual(enc_node_features[0][3], 0.0, 'method definition node set in encoding')
        self.assertEqual(enc_node_features[0][4], 0.0, 'method signature node set in encoding')
        self.assertEqual(enc_node_features[0][5], 0.0, 'module node set in encoding')
        self.assertEqual(enc_node_features[0][7], 0.0, 'parameter node set in encoding')

    def test_subpackage(self):
        """
        Unit test recovered by hand.
        in Dir 'test_subpackage' is a Dir named 'parent' is a Dir named 'child'
        I do not know why she named it this way :(
        """
        repo = 'unit_tests/test_subpackage'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(len(edges), 2, 'package should have edge to subpackage and vice versa')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')
        self.assertEqual(edges[0], [0, 1], 'edge between package and subpackage wrong')
        self.assertEqual(edges[1], [1, 0], 'edge between subpackage and parent package wrong')
        self.assertEqual(len(edge_attributes), 2, 'wrong number of edge attributes')
        self.assertEqual(edge_attributes[0], EdgeTypes.SUBPACKAGE.value, 'subpackage attribute is missing/wrong')
        self.assertEqual(edge_attributes[1], EdgeTypes.PARENT.value, 'parent package attribute is missing/wrong')

    def test_module(self):
        repo = 'unit_tests/test_module'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 1, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(len(edges), 0, 'single module should not have edge')
        self.assertEqual(len(enc_node_features), 1, 'wrong number of encoded nodes')
        self.assertEqual(len(edge_attributes), 0, 'wrong number of edge attributes')

        #test ohe encoding for node type module
        self.assertEqual(enc_node_features[0][6], 0.0, 'package node set in encoding')
        self.assertEqual(enc_node_features[0][0], 0.0, 'call node set in encoding')
        self.assertEqual(enc_node_features[0][1], 0.0, 'class node set in encoding')
        self.assertEqual(enc_node_features[0][2], 0.0, 'method node set in encoding')
        self.assertEqual(enc_node_features[0][3], 0.0, 'method definition node set in encoding')
        self.assertEqual(enc_node_features[0][4], 0.0, 'method signature node set in encoding')
        self.assertEqual(enc_node_features[0][5], 1.0, 'module node not set in encoding')
        self.assertEqual(enc_node_features[0][7], 0.0, 'parameter node set in encoding')

    def test_multiple_modules(self):
        repo = 'unit_tests/test_multiple_modules'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(len(edges), 0, 'module should not have edge to another module')
        self.assertEqual(len(edge_attributes), 0, 'wrong number of edge attributes')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')

    def test_module_in_package(self):
        repo = 'unit_tests/test_module_in_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(len(edges), 2, 'module should have edge to package and vice versa')
        self.assertEqual(len(edge_attributes), 2, 'wrong number of edge attributes')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')
        self.assertEqual(edges[0], [0, 1], 'error with edge package to module')
        self.assertEqual(edges[1], [1, 0], 'error with edge module to package')
        self.assertEqual(edge_attributes[0], EdgeTypes.MODULES.value, 'attribute for edge package to module is wrong')
        self.assertEqual(edge_attributes[1], EdgeTypes.NAMESPACE.value, 'attribute for edge module to package is wrong')

    def test_class(self):
        repo = 'unit_tests/test_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(len(edges), 1, 'module should have edge to class')
        self.assertEqual(len(edge_attributes), 1, 'wrong number of edge attributes')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')
        self.assertEqual(edges[0], [0, 1], 'error with edge module to class')
        self.assertEqual(edge_attributes[0], EdgeTypes.CONTAINS.value, 'attribute for edge module to class is wrong')

        #test ohe encoding for node type class
        self.assertEqual(enc_node_features[1][6], 0.0, 'package node set in encoding')
        self.assertEqual(enc_node_features[1][0], 0.0, 'call node set in encoding')
        self.assertEqual(enc_node_features[1][1], 1.0, 'class node not set in encoding')
        self.assertEqual(enc_node_features[1][2], 0.0, 'method node set in encoding')
        self.assertEqual(enc_node_features[1][3], 0.0, 'method definition node set in encoding')
        self.assertEqual(enc_node_features[1][4], 0.0, 'method signature node set in encoding')
        self.assertEqual(enc_node_features[1][5], 0.0, 'module node set in encoding')
        self.assertEqual(enc_node_features[1][7], 0.0, 'parameter node set in encoding')

    def test_child_class(self):
        repo = 'unit_tests/test_child_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 3, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(len(edges), 3, 'class should have edge to child class')
        self.assertEqual(len(edge_attributes), 3, 'wrong number of edge attributes')
        self.assertEqual(len(enc_node_features), 3, 'wrong number of encoded nodes')
        self.assertEqual(edges[1], [1, 2], 'error with edge class to child class')
        self.assertEqual(edges[2], [2, 1], 'error with edge child class to parent class')
        self.assertEqual(edge_attributes[1], EdgeTypes.CHILDCLASSES.value, 'attribute for edge class to child class is wrong')
        self.assertEqual(edge_attributes[2], EdgeTypes.PARENTCLASSES.value, 'attribute for edge child class to parent class is wrong')

    def test_method(self):
        repo = 'unit_tests/test_method'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 4, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[1], NodeTypes.METHOD_DEFINITION.value, 'method definition is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD.value, 'method is wrong node type')
        self.assertEqual(node_features[3], NodeTypes.METHOD_SIGNATURE.value, 'method signature is wrong node type')

        #test ohe encoding for node type method, method definition and method signature
        self.assertEqual(enc_node_features[2][2], 1.0, 'method node not set in encoding')
        self.assertEqual(enc_node_features[1][3], 1.0, 'method definition node not set in encoding')
        self.assertEqual(enc_node_features[3][4], 1.0, 'method signature node not set in encoding')

        self.assertEqual(len(edges), 3, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 3, 'wrong number of edge attributes')
        self.assertEqual(edges[0], [0, 1], 'module should have edge to method definition')
        self.assertEqual(edges[1], [2, 1], 'method should have edge to method definition')
        self.assertEqual(edges[2], [2, 3], 'method should have edge to method signature')
        self.assertEqual(edge_attributes[0], EdgeTypes.CONTAINS.value, 'attribute for edge module to method definition is wrong')
        self.assertEqual(edge_attributes[1], EdgeTypes.DEFINITIONS.value, 'attribute for edge method to method definition is wrong')
        self.assertEqual(edge_attributes[2], EdgeTypes.SIGNATURES.value, 'attribute for edge method to method signature is wrong')

    #test defining a method inside a class
    def test_method_in_class(self):
        repo = 'unit_tests/test_method_in_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 5, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(len(enc_node_features), 5, 'wrong number of encoded nodes')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is wrong node type')
        self.assertEqual(len(edges), 4, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 4, 'wrong number of edge attributes')
        self.assertEqual(edges[1], [1, 2], 'class should have edge to method definition')
        self.assertEqual(edge_attributes[1], EdgeTypes.DEFINES.value, 'attribute for edge class to method definition is wrong')

    #test defining multiple methods inside a class
    def test_multiple_methods_in_class(self):
        repo = 'unit_tests/test_multiple_methods_in_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 8, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(len(enc_node_features), 8, 'wrong number of encoded nodes')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'first method definition is wrong node type')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'second method definition is wrong node type')
        self.assertEqual(len(edges), 7, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 7, 'wrong number of edge attributes')
        self.assertEqual(edges[1], [1, 2], 'class should have edge to first method definition')
        self.assertEqual(edges[2], [1, 3], 'class should have edge to second method definition')
        
    def test_parameter(self):
        repo = 'unit_tests/test_parameter'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 5, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[4], NodeTypes.PARAMETER.value, 'parameter is wrong node type')
        self.assertEqual(len(edges), 4, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 4, 'wrong number of edge attributes')
        self.assertEqual(edges[3], [3, 4], 'method signature should have edge to parameter')
        self.assertEqual(edge_attributes[3], EdgeTypes.PARAMETERS.value, 'attribute for edge method signature to parameter is wrong')

        #test ohe encoding for node type parameter
        self.assertEqual(enc_node_features[4][6], 0.0, 'package node set in encoding')
        self.assertEqual(enc_node_features[4][0], 0.0, 'call node set in encoding')
        self.assertEqual(enc_node_features[4][1], 0.0, 'class node set in encoding')
        self.assertEqual(enc_node_features[4][2], 0.0, 'method node set in encoding')
        self.assertEqual(enc_node_features[4][3], 0.0, 'method definition node set in encoding')
        self.assertEqual(enc_node_features[4][4], 0.0, 'method signature node set in encoding')
        self.assertEqual(enc_node_features[4][5], 0.0, 'module node set in encoding')
        self.assertEqual(enc_node_features[4][7], 1.0, 'parameter node not set in encoding')

    def test_multiple_parameter(self):
        repo = 'unit_tests/test_multiple_parameter'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 6, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[5], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[5], NodeTypes.PARAMETER.value, 'parameter is wrong node type')
        self.assertEqual(len(edges), 7, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 7, 'wrong number of edge attributes')
        
        self.assertEqual(edges[6], [3, 5], 'method signature should have edge to second parameter')
        self.assertEqual(edges[4], [4, 5], 'parameter should have edge to second parameter')
        self.assertEqual(edges[5], [5, 4], 'second parameter should have edge to parameter')
        self.assertEqual(edge_attributes[4], EdgeTypes.NEXT.value, 'attribute for edge parameter to second parameter is wrong')
        self.assertEqual(edge_attributes[5], EdgeTypes.PREVIOUS.value, 'attribute for edge second parameter to parameter is wrong')
        self.assertEqual(edge_attributes[6], EdgeTypes.PARAMETERS.value, 'attribute for edge method signature to second parameter is wrong')

    #test call of method by another method, both in same module
    def test_module_internal_method_call(self):
        repo = 'unit_tests/test_module_internal_method_call'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 9, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[1], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[2], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [1, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [3, 1], 'call should have edge to method definition, target')
        self.assertEqual(edge_attributes[2], EdgeTypes.ACCESSING.value, 'attribute for edge method definition to call is wrong')
        self.assertEqual(edge_attributes[3], EdgeTypes.SOURCE.value, 'attribute for edge call to method definition is wrong')
        self.assertEqual(edge_attributes[4], EdgeTypes.ACCESSEDBY.value, 'attribute for edge method definition to call is wrong')
        self.assertEqual(edge_attributes[5], EdgeTypes.TARGET.value, 'attribute for edge call to method definition is wrong')
 
    #test importing a method from another module in the repo
    def test_internal_method_imports(self):
        repo = 'unit_tests/test_internal_method_imports'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 9, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(len(enc_node_features), 9, 'wrong number of encoded nodes')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[1], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(len(edges), 10, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 10, 'wrong number of edge attributes')
        self.assertEqual(edges[2], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [1, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [4, 1], 'call should have edge to method definition, target')
    
    #test importing a method from a class in another module in the repo
    def test_internal_class_imports(self):
        repo = 'unit_tests/test_internal_class_imports'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), 10, 'wrong number of nodes')
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(len(enc_node_features), 10, 'wrong number of encoded nodes')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[5], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[4], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is missing')

        self.assertEqual(len(edges), 11, 'wrong number of edges')
        self.assertEqual(len(edge_attributes), 11, 'wrong number of edge attributes')
        self.assertEqual(edges[3], [4, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [5, 4], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [2, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [5, 2], 'call should have edge to method definition, target')
    
    #test calling a function from an imported module from another package
    def test_internal_method_imports_package(self):
        repo = 'unit_tests/test_internal_method_imports_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[5], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[1], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[2], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[3], [5, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[4], [3, 5], 'call should have edge to method definition, target')
    
    #test calling a function from an imported class from another package
    def test_internal_method_class_imports_package(self):
        repo = 'unit_tests/test_internal_method_class_imports_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[5], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[6], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.CLASS.value, 'class is missing')
        self.assertEqual(node_features[6], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[1], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[2], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[3], [6, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[4], [3, 6], 'call should have edge to method definition, target')
    
    #test call of method in a class by another method not in the class, both in same module
    def test_module_internal_class_call(self):
        repo = 'unit_tests/test_module_internal_class_call'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[3], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [2, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [4, 2], 'call should have edge to method definition, target')
    
    #test call of method in a class by another method, both in same class
    def test_class_internal_method_call(self):
        repo = 'unit_tests/test_class_internal_method_call'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[3], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [2, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [4, 2], 'call should have edge to method definition, target')

    #test call for method in multiple packages(subpackage)
    def test_internal_method_imports_multiple_packages(self):
        repo = 'unit_tests/test_internal_method_imports_multiple_packages'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[7], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'subpackage is missing')
        self.assertEqual(node_features[2], NodeTypes.MODULE.value, 'module is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[7], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[3], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [7, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [4, 7], 'call should have edge to method definition, target')

    #test call for method in class in multiple packages(subpackage)
    def test_internal_method_class_imports_multiple_packages(self):
        repo = 'unit_tests/test_internal_method_class_imports_multiple_packages'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[0], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[1], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[2], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[3], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[4], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[7], 'false', 'library flag for internal object is wrong')
        self.assertEqual(lib_flags[8], 'false', 'library flag for internal object is wrong')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'subpackage is missing')
        self.assertEqual(node_features[2], NodeTypes.MODULE.value, 'module is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[7], NodeTypes.CLASS.value, 'class is missing')
        self.assertEqual(node_features[8], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[3], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [8, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [4, 8], 'call should have edge to method definition, target')

    #test importing external library, one module, one method   
    def test_call_external_library(self):
        repo = 'unit_tests/test_call_external_library'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[0], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[3], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[4], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[5], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[2], 'false', 'flag for import is wrong') #source of call, not imported

        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'imported package is missing')
        self.assertEqual(node_features[4], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')

        self.assertEqual(edges[1], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[2], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[3], [5, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[4], [3, 5], 'call should have edge to method definition, target')

    #test importing multiple packages/subpackages from external library
    def test_call_external_library_submodule(self):
        repo = 'unit_tests/test_call_external_library_submodule'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[4], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[1], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[8], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[5], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[6], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[9], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[0], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[3], 'false', 'flag for import is wrong') #source of call, not imported
        self.assertEqual(lib_flags[7], 'true', 'flag for import is wrong')

        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'imported package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'imported second package is missing')
        self.assertEqual(node_features[6], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[8], NodeTypes.MODULE.value, 'imported second module is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[7], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')
        self.assertEqual(node_features[9], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')

        #for call of first package
        self.assertEqual(edges[1], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[2], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[3], [7, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[4], [4, 7], 'call should have edge to method definition, target')

        #for call of second package with submodule
        self.assertEqual(edges[5], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[6], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[7], [9, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[8], [5, 9], 'call should have edge to method definition, target')

    #test importing class with a method (external libraries)
    def test_call_external_library_class(self):
        repo = 'unit_tests/test_call_external_library_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(len(lib_flags), len(node_features), 'wrong number of ext. library flags')
        self.assertEqual(lib_flags[0], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[1], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[8], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[5], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[6], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[9], 'true', 'flag for import is wrong')

        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'imported package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'imported subpackage is missing')
        self.assertEqual(node_features[6], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[8], NodeTypes.CLASS.value, 'imported class is missing')
        self.assertEqual(node_features[9], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')

        self.assertEqual(edges[7], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[8], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[9], [9, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[10], [5, 9], 'call should have edge to method definition, target')

    #test importing class with multiple methods (external libraries)
    def test_call_external_library_class_multiple_methods(self):
        repo = 'unit_tests/test_call_external_library_class_multiple_methods'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[9], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[10], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[11], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[5], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[6], 'true', 'flag for import is wrong')

        self.assertEqual(node_features[9], NodeTypes.CLASS.value, 'imported class is missing')
        self.assertEqual(node_features[10], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')
        self.assertEqual(node_features[11], NodeTypes.METHOD_DEFINITION.value, 'imported second method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[6], NodeTypes.CALL.value, 'call is missing')
        
        #edges for call of first method in class
        self.assertEqual(edges[7], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[8], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[9], [10, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[10], [5, 10], 'call should have edge to method definition, target')
        
        #edges for call of second method in class
        self.assertEqual(edges[11], [3, 6], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[12], [6, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[13], [11, 6], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[14], [6, 11], 'call should have edge to method definition, target')

    #test importing multiple methods in one module (external libraries)
    def test_call_external_library_multiple_methods(self):
        repo = 'unit_tests/test_call_external_library_multiple_methods'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(lib_flags[7], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[3], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[4], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[5], 'true', 'flag for import is wrong')
        self.assertEqual(lib_flags[6], 'true', 'flag for import is wrong')

        self.assertEqual(node_features[5], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[6], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')
        self.assertEqual(node_features[7], NodeTypes.METHOD_DEFINITION.value, 'imported second method definition is missing')
        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        
        #edges for call of first method in module
        self.assertEqual(edges[1], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[2], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[3], [6, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[4], [3, 6], 'call should have edge to method definition, target')
        
        #edges for call of second method in module
        self.assertEqual(edges[5], [2, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[6], [4, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[7], [7, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[8], [4, 7], 'call should have edge to method definition, target')

    #test imported packages (and subpackages) with multiple modules (external libraries)
    def test_call_external_library_multiple_modules_same_package(self):
        repo = 'unit_tests/test_call_external_library_multiple_modules_same_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[1], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[4], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[5], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[6], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[7], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[8], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[9], 'true', 'library flag for imported object is wrong')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'imported subpackage is missing')
        self.assertEqual(node_features[6], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[8], NodeTypes.MODULE.value, 'imported second module is missing')
        self.assertEqual(node_features[7], NodeTypes.METHOD_DEFINITION.value, 'imported method definition of first module is missing')
        self.assertEqual(node_features[9], NodeTypes.METHOD_DEFINITION.value, 'imported method definition of second module is missing')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')

        #modules share same subpackage as namespace
        self.assertEqual(edges[11], [1, 6], 'error with edge subpackage to first imported module')
        self.assertEqual(edges[12], [6, 1], 'error with edge first imported module to subpackage')
        self.assertEqual(edges[14], [1, 8], 'error with edge subpackage to second imported module')
        self.assertEqual(edges[15], [8, 1], 'error with edge second imported module to subpackage')

        #edges for call of method in first module
        self.assertEqual(edges[3], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [7, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [4, 7], 'call should have edge to method definition, target')
        
        #edges for call of method in second module
        self.assertEqual(edges[7], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[8], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[9], [9, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[10], [5, 9], 'call should have edge to method definition, target')

    #test imported packages with multiple subpackages (external libraries)
    def test_call_external_library_multiple_subpackages(self):
        repo = 'unit_tests/test_call_external_library_multiple_subpackages'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()
        
        self.assertEqual(lib_flags[0], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[1], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[2], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[7], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[9], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[8], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[10], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[5], 'true', 'library flag for imported object is wrong')
        self.assertEqual(lib_flags[6], 'true', 'library flag for imported object is wrong')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'imported parent package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'imported first subpackage is missing')
        self.assertEqual(node_features[2], NodeTypes.PACKAGE.value, 'imported second subpackage is missing')
        self.assertEqual(node_features[7], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[9], NodeTypes.MODULE.value, 'imported second module is missing')
        self.assertEqual(node_features[8], NodeTypes.METHOD_DEFINITION.value, 'imported method definition of first module is missing')
        self.assertEqual(node_features[10], NodeTypes.METHOD_DEFINITION.value, 'imported method definition of second module is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[6], NodeTypes.CALL.value, 'call is missing')

        #two imported subpackages share same parent package
        self.assertEqual(edges[0], [0, 1], 'error with edge parent package to first subpackage')
        self.assertEqual(edges[1], [1, 0], 'error with edge first subpackage to parent package')
        self.assertEqual(edges[2], [0, 2], 'error with edge parent package to second subpackage')
        self.assertEqual(edges[3], [2, 0], 'error with edge second subpackage to parent package')

        #modules have different subpackages as namespace
        self.assertEqual(edges[13], [1, 7], 'error with edge subpackage to first imported module')
        self.assertEqual(edges[14], [7, 1], 'error with edge first imported module to subpackage')
        self.assertEqual(edges[16], [2, 9], 'error with edge subpackage to second imported module')
        self.assertEqual(edges[17], [9, 2], 'error with edge second imported module to subpackage')

        #edges for call of method in first module
        self.assertEqual(edges[5], [4, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[6], [5, 4], 'call should have edge to method definition, source')
        self.assertEqual(edges[7], [8, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[8], [5, 8], 'call should have edge to method definition, target')
        
        #edges for call of method in second module
        self.assertEqual(edges[9], [4, 6], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[10], [6, 4], 'call should have edge to method definition, source')
        self.assertEqual(edges[11], [10, 6], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[12], [6, 10], 'call should have edge to method definition, target')

    #test if hashed node names exist, are the right number, and are zipped with node type into one array
    def test_hashed_names(self):
        repo = 'unit_tests/test_hashed_names'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        full_features = matrix.get_node_features()
        edges = matrix.get_adjacency_list()
        edge_attributes = matrix.get_edge_attributes()
        lib_flags = matrix.get_external_library_flags()

        self.assertEqual(len(node_features), len(full_features), 'number of nodes in type and type+hash is not equal')
        for item in full_features:
            self.assertEqual(len(item), 11, 'number of node features is wrong')

if __name__ == "__main__":
    unittest.main()