import unittest
import sys
import os

# getting the name of the directory where this file is
current = os.path.dirname(os.path.realpath(__file__))

# getting the parent directory name where the current directory is
parent = os.path.dirname(current)

# adding the parent directory to the sys.path.
sys.path.append(parent)

from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from test_utils import check_path_exists

test_output_dir = 'test_results/minimal_examples'

class TestMinimalExamples(unittest.TestCase):

    def test_function_overwrite(self):
        """
        This test tests a Skript with 2 Functions with the same name.
        """
        repo = 'minimal_examples/function_overwrite'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, True, test_output_dir)
        ecore_graph = graph.get_graph()
