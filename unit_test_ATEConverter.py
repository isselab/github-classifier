import unittest
from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes

class TestATEConv(unittest.TestCase):
    def test_ateconv(self):
        repo = 'test/unit_test_repo/testRepo1'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()

        #check number of obects in the graph
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        self.assertEqual(len(ecore_graph.modules), 3, 'wrong number of modules')
        self.assertEqual(len(ecore_graph.classes), 1, 'wrong number of classes')
        self.assertEqual(len(ecore_graph.methods), 3, 'wrong number of methods')

        #check package
        self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'wrong package type')
        self.assertEqual(ecore_graph.packages[0].tName, 'my_package', 'wrong package name')

        #check modules
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'test/unit_test_repo/testRepo1/testCall', 'module 1 wrong location')
        self.assertIsNone(ecore_graph.modules[0].namespace, 'module should not have package')
        self.assertEqual(ecore_graph.modules[1].eClass.name, NodeTypes.MODULE.value, 'module wrong type')
        self.assertEqual(ecore_graph.modules[1].location, 'test/unit_test_repo/testRepo1/my_package/callFunc', 'module 2 wrong location')
        self.assertEqual(ecore_graph.modules[1].namespace.tName, 'my_package', 'package of module wrong')
        self.assertEqual(ecore_graph.modules[2].eClass.name, NodeTypes.MODULE.value, 'module wrong type')
        self.assertEqual(ecore_graph.modules[2].location, 'test/unit_test_repo/testRepo1/my_package/testClass', 'module 3 wrong location')
        self.assertEqual(ecore_graph.modules[2].namespace.tName, 'my_package', 'package of module wrong')

        #check objects contained in modules
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'wrong object type')
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'call_name', 'wrong method in module')
        self.assertEqual(ecore_graph.modules[1].contains[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'wrong object type')
        self.assertEqual(ecore_graph.modules[1].contains[0].signature.method.tName, 'greet_friend', 'wrong method in module')
        self.assertEqual(ecore_graph.modules[2].contains[0].eClass.name, NodeTypes.CLASS.value, 'wrong object type')
        self.assertEqual(ecore_graph.modules[2].contains[0].tName, 'myTest', 'wrong class name')
        self.assertEqual(ecore_graph.modules[2].contains[0].defines[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'wrong object type')
        self.assertEqual(ecore_graph.modules[2].contains[0].defines[0].signature.method.tName, 'my_hello', 'wrong method in module')

        #check call
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is missing or wrong type')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].target.eClass.name, NodeTypes.METHOD_DEFINITION.value, 'target is not set')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].target.signature.method.tName, 'my_hello', 'wrong target')

        #check methods
        self.assertEqual(ecore_graph.methods[0].eClass.name, NodeTypes.METHOD.value, 'method wrong type')
        self.assertEqual(ecore_graph.methods[0].tName, 'call_name', 'wrong method name')
        self.assertEqual(ecore_graph.methods[1].eClass.name, NodeTypes.METHOD.value, 'method wrong type')
        self.assertEqual(ecore_graph.methods[1].tName, 'greet_friend', 'wrong method name')
        self.assertEqual(ecore_graph.methods[2].eClass.name, NodeTypes.METHOD.value, 'method wrong type')
        self.assertEqual(ecore_graph.methods[2].tName, 'my_hello', 'wrong method name')

        #check method signatures and parameters
        self.assertEqual(ecore_graph.methods[0].signatures[0].eClass.name, NodeTypes.METHOD_SIGNATURE.value, 'signature has wrong object type')
        self.assertEqual(len(ecore_graph.methods[0].signatures[0].parameters), 1, 'wrong number of parameters')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].eClass.name, NodeTypes.PARAMETER.value, 'parameter wrong type')
        self.assertEqual(ecore_graph.methods[1].signatures[0].eClass.name, NodeTypes.METHOD_SIGNATURE.value, 'signature has wrong object type')
        self.assertEqual(hasattr(ecore_graph.methods[1].signatures, 'parameters'), False, 'method should not have a parameter')
        self.assertEqual(ecore_graph.methods[2].signatures[0].eClass.name, NodeTypes.METHOD_SIGNATURE.value, 'signature has wrong object type')
        self.assertEqual(hasattr(ecore_graph.methods[2].signatures, 'parameters'), False, 'method should not have a parameter')


unittest.main()