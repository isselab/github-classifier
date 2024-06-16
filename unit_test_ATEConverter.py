import unittest
from ASTToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes

class TestATEConv(unittest.TestCase):
    def test_ateconv(self):
        output_dir = 'D:/unit_test'
        repo = 'test/unit_test_repo/testRepo1'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, output_dir, repo, False)
        ecore_graph = graph.get_graph()
        #print(ecore_graph.packages)
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        self.assertEqual(len(ecore_graph.modules), 3, 'wrong number of modules')
        self.assertEqual(len(ecore_graph.classes), 1, 'wrong number of classes')
        #self.assertEqual(len(ecore_graph.methods), 3, 'wrong number of methods')
        #print(ecore_graph.methods[3].tName)
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'wrong object type')
        self.assertEqual(ecore_graph.modules[0].location, 'test/unit_test_repo/testRepo1/testCall', 'module 1 wrong location')
        self.assertEqual(ecore_graph.modules[1].location, 'test/unit_test_repo/testRepo1/my_package/callFunc', 'module 2 wrong location')
        self.assertEqual(ecore_graph.modules[2].location, 'test/unit_test_repo/testRepo1/my_package/testClass', 'module 3 wrong location')


unittest.main()