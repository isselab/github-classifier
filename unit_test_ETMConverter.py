import unittest
from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes

class TestETMConv(unittest.TestCase):
    def test_etmconv(self):
        output_dir = 'D:/unit_test'
        repo = 'test/unit_test_repo/testRepo1'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, output_dir, repo, False)
        ecore_graph = graph.get_graph()