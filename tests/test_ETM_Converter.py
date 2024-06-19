import unittest
from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes
from EcoreToMatrixConverter import EcoreToMatrixConverter

'''(hashed) name not a feature right now, therefore it is missing in tests, 
might chage later,
the tests for the second converter are the same as for the first'''

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

    def test_module_in_package(self):
        repo = 'tests/unit_tests/test_module_in_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(len(edges), 2, 'module should have edge to package and vice versa')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')
        self.assertEqual(edges[0], [0, 1], 'error with edge package to module')
        self.assertEqual(edges[1], [1, 0], 'error with edge module to package')

    def test_class(self):
        repo = 'tests/unit_tests/test_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 2, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(len(edges), 1, 'module should have edge to class')
        self.assertEqual(len(enc_node_features), 2, 'wrong number of encoded nodes')
        self.assertEqual(edges[0], [0, 1], 'error with edge module to class')

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
        repo = 'tests/unit_tests/test_child_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 3, 'wrong number of nodes')
        self.assertEqual(node_features[0], NodeTypes.MODULE.value, 'module is wrong node type')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(len(edges), 2, 'class should have edge to child class')
        self.assertEqual(len(enc_node_features), 3, 'wrong number of encoded nodes')
        self.assertEqual(edges[1], [1, 2], 'error with edge class to child class')

    def test_method(self):
        repo = 'tests/unit_tests/test_method'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 4, 'wrong number of nodes')
        self.assertEqual(node_features[1], NodeTypes.METHOD_DEFINITION.value, 'method definition is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD.value, 'method is wrong node type')
        self.assertEqual(node_features[3], NodeTypes.METHOD_SIGNATURE.value, 'method signature is wrong node type')

        #test ohe encoding for node type method, method definition and method signature
        self.assertEqual(enc_node_features[2][2], 1.0, 'method node not set in encoding')
        self.assertEqual(enc_node_features[1][3], 1.0, 'method definition node not set in encoding')
        self.assertEqual(enc_node_features[3][4], 1.0, 'method signature node not set in encoding')

        self.assertEqual(len(edges), 3, 'wrong number of edges')
        self.assertEqual(edges[0], [0, 1], 'module should have edge to method definition')
        self.assertEqual(edges[1], [2, 1], 'method should have edge to method definition')
        self.assertEqual(edges[2], [2, 3], 'method should have edge to method signature')

    #test defining a method inside a class
    def test_method_in_class(self):
        repo = 'tests/unit_tests/test_method_in_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 5, 'wrong number of nodes')
        self.assertEqual(len(enc_node_features), 5, 'wrong number of encoded nodes')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is wrong node type')
        self.assertEqual(len(edges), 4, 'wrong number of edges')
        self.assertEqual(edges[1], [1, 2], 'class should have edge to method definition')

    #test defining multiple methods inside a class
    def test_multiple_methods_in_class(self):
        repo = 'tests/unit_tests/test_multiple_methods_in_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 8, 'wrong number of nodes')
        self.assertEqual(len(enc_node_features), 8, 'wrong number of encoded nodes')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'first method definition is wrong node type')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'second method definition is wrong node type')
        self.assertEqual(len(edges), 7, 'wrong number of edges')
        self.assertEqual(edges[1], [1, 2], 'class should have edge to first method definition')
        self.assertEqual(edges[2], [1, 3], 'class should have edge to second method definition')
        
    def test_parameter(self):
        repo = 'tests/unit_tests/test_parameter'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 5, 'wrong number of nodes')
        self.assertEqual(node_features[4], NodeTypes.PARAMETER.value, 'parameter is wrong node type')
        self.assertEqual(len(edges), 4, 'wrong number of edges')
        self.assertEqual(edges[3], [3, 4], 'method signature should have edge to parameter')

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
        repo = 'tests/unit_tests/test_multiple_parameter'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 6, 'wrong number of nodes')
        self.assertEqual(node_features[5], NodeTypes.PARAMETER.value, 'parameter is wrong node type')
        self.assertEqual(len(edges), 7, 'wrong number of edges')
        
        self.assertEqual(edges[6], [3, 5], 'method signature should have edge to second parameter')
        self.assertEqual(edges[4], [4, 5], 'parameter should have edge to second parameter')
        self.assertEqual(edges[5], [5, 4], 'second parameter should have edge to parameter')

    #test call of method by another method, both in same module
    def test_module_internal_method_call(self):
        repo = 'tests/unit_tests/test_module_internal_method_call'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 9, 'wrong number of nodes')
        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is wrong node type')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[1], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[2], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [1, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [3, 1], 'call should have edge to method definition, target')
 
    #test importing a method from another module in the repo
    def test_internal_method_imports(self):
        repo = 'tests/unit_tests/test_internal_method_imports'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 9, 'wrong number of nodes')
        self.assertEqual(len(enc_node_features), 9, 'wrong number of encoded nodes')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[1], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(len(edges), 10, 'wrong number of edges')
        self.assertEqual(edges[2], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [1, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [4, 1], 'call should have edge to method definition, target')
    
    #test importing a method from a class in another module in the repo
    def test_internal_class_imports(self):
        repo = 'tests/unit_tests/test_internal_class_imports'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(len(node_features), 10, 'wrong number of nodes')
        self.assertEqual(len(enc_node_features), 10, 'wrong number of encoded nodes')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[4], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[1], NodeTypes.CLASS.value, 'class is missing')

        self.assertEqual(len(edges), 11, 'wrong number of edges')
        self.assertEqual(edges[3], [4, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [5, 4], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [2, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [5, 2], 'call should have edge to method definition, target')
    
    #test calling a function from an imported module from another package
    def test_internal_method_imports_package(self):
        repo = 'tests/unit_tests/test_internal_method_imports_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(node_features[3], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[2], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[1], [2, 3], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[2], [3, 2], 'call should have edge to method definition, source')
        self.assertEqual(edges[3], [5, 3], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[4], [3, 5], 'call should have edge to method definition, target')
    
    #test calling a function from an imported class from another package
    def test_internal_method_class_imports_package(self):
        repo = 'tests/unit_tests/test_internal_method_class_imports_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

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
        repo = 'tests/unit_tests/test_module_internal_class_call'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

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
        repo = 'tests/unit_tests/test_class_internal_method_call'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

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
        repo = 'tests/unit_tests/test_internal_method_imports_multiple_packages'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'subpackage is missing')
        self.assertEqual(node_features[2], NodeTypes.MODULE.value, 'module is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[7], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[2], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [7, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [4, 7], 'call should have edge to method definition, target')

    #test call for method in class in multiple packages(subpackage)
    def test_internal_method_class_imports_multiple_packages(self):
        repo = 'tests/unit_tests/test_internal_method_class_imports_multiple_packages'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'subpackage is missing')
        self.assertEqual(node_features[2], NodeTypes.MODULE.value, 'module is missing')
        self.assertEqual(node_features[3], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')
        self.assertEqual(node_features[7], NodeTypes.CLASS.value, 'class is missing')
        self.assertEqual(node_features[8], NodeTypes.METHOD_DEFINITION.value, 'method definition is missing')

        self.assertEqual(edges[2], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [8, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [4, 8], 'call should have edge to method definition, target')

    #test importing external library, one module, one method   
    def test_call_external_library(self):
        repo = 'tests/unit_tests/test_call_external_library'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

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
        repo = 'tests/unit_tests/test_call_external_library_submodule'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

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
        repo = 'tests/unit_tests/test_call_external_library_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(node_features[0], NodeTypes.PACKAGE.value, 'imported package is missing')
        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'imported subpackage is missing')
        self.assertEqual(node_features[6], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[8], NodeTypes.CLASS.value, 'imported class is missing')
        self.assertEqual(node_features[9], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')

        self.assertEqual(edges[6], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[7], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[8], [9, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[9], [5, 9], 'call should have edge to method definition, target')

    #test importing class with multiple methods (external libraries)
    def test_call_external_library_class_multiple_methods(self):
        repo = 'tests/unit_tests/test_call_external_library_class_multiple_methods'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(node_features[9], NodeTypes.CLASS.value, 'imported class is missing')
        self.assertEqual(node_features[10], NodeTypes.METHOD_DEFINITION.value, 'imported method definition is missing')
        self.assertEqual(node_features[11], NodeTypes.METHOD_DEFINITION.value, 'imported second method definition is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[6], NodeTypes.CALL.value, 'call is missing')
        
        #edges for call of first method in class
        self.assertEqual(edges[6], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[7], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[8], [10, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[9], [5, 10], 'call should have edge to method definition, target')
        
        #edges for call of second method in class
        self.assertEqual(edges[10], [3, 6], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[11], [6, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[12], [11, 6], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[13], [6, 11], 'call should have edge to method definition, target')

    #test importing multiple methods in one module (external libraries)
    def test_call_external_library_multiple_methods(self):
        repo = 'tests/unit_tests/test_call_external_library_multiple_methods'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

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
        repo = 'tests/unit_tests/test_call_external_library_multiple_modules_same_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()

        self.assertEqual(node_features[1], NodeTypes.PACKAGE.value, 'imported subpackage is missing')
        self.assertEqual(node_features[6], NodeTypes.MODULE.value, 'imported module is missing')
        self.assertEqual(node_features[8], NodeTypes.MODULE.value, 'imported second module is missing')
        self.assertEqual(node_features[7], NodeTypes.METHOD_DEFINITION.value, 'imported method definition of first module is missing')
        self.assertEqual(node_features[9], NodeTypes.METHOD_DEFINITION.value, 'imported method definition of second module is missing')
        self.assertEqual(node_features[4], NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(node_features[5], NodeTypes.CALL.value, 'call is missing')

        #modules share same subpackage as namespace
        self.assertEqual(edges[10], [1, 6], 'error with edge subpackage to first imported module')
        self.assertEqual(edges[11], [6, 1], 'error with edge first imported module to subpackage')
        self.assertEqual(edges[13], [1, 8], 'error with edge subpackage to second imported module')
        self.assertEqual(edges[14], [8, 1], 'error with edge second imported module to subpackage')

        #edges for call of method in first module
        self.assertEqual(edges[2], [3, 4], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[3], [4, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[4], [7, 4], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[5], [4, 7], 'call should have edge to method definition, target')
        
        #edges for call of method in second module
        self.assertEqual(edges[6], [3, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[7], [5, 3], 'call should have edge to method definition, source')
        self.assertEqual(edges[8], [9, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[9], [5, 9], 'call should have edge to method definition, target')

    #test imported packages with multiple subpackages (external libraries)
    def test_call_external_library_multiple_subpackages(self):
        repo = 'tests/unit_tests/test_call_external_library_multiple_subpackages'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        matrix = EcoreToMatrixConverter(ecore_graph, False)
        node_features = matrix.get_node_matrix()
        enc_node_features = matrix.get_encoded_node_matrix()
        edges = matrix.get_adjacency_list()
        
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
        self.assertEqual(edges[1], [0, 2], 'error with edge parent package to second subpackage')

        #modules have different subpackages as namespace
        self.assertEqual(edges[11], [1, 7], 'error with edge subpackage to first imported module')
        self.assertEqual(edges[12], [7, 1], 'error with edge first imported module to subpackage')
        self.assertEqual(edges[14], [2, 9], 'error with edge subpackage to second imported module')
        self.assertEqual(edges[15], [9, 2], 'error with edge second imported module to subpackage')

        #edges for call of method in first module
        self.assertEqual(edges[3], [4, 5], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[4], [5, 4], 'call should have edge to method definition, source')
        self.assertEqual(edges[5], [8, 5], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[6], [5, 8], 'call should have edge to method definition, target')
        
        #edges for call of method in second module
        self.assertEqual(edges[7], [4, 6], 'method definition should have edge to call, accessing')
        self.assertEqual(edges[8], [6, 4], 'call should have edge to method definition, source')
        self.assertEqual(edges[9], [10, 6], 'method definition should have edge to call, accessedBy')
        self.assertEqual(edges[10], [6, 10], 'call should have edge to method definition, target')

unittest.main()