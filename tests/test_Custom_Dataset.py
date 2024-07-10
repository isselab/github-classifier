import sys
import os
 
#getting the name of the directory where this file is
current = os.path.dirname(os.path.realpath(__file__))
 
#getting the parent directory name where the current directory is
parent = os.path.dirname(current)
 
#adding the parent directory to the sys.path.
sys.path.append(parent)

from CustomDataset import RepositoryDataset
import unittest

'''the dataset loaded here consists of the same unit tests as the other tests, but for the purpose 
of testing to load the dataset, the output of the converters were saved in files,
the tests checking the dimension of the graph components also ensure that they can be accessed at all'''

output_directory = 'testing' #path to directory containing xmi and csv files of the unit tests
labels = 'testing.xlsx' #exemplary labels to test loading

class TestCustomDataset(unittest.TestCase):

    def test_dataset_size(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)

        #the length is 26 because the graphs without any edges cannot be loaded, throws 'no columns to parse from file' error
        self.assertEqual(dataset.__len__(), 26, 'wrong number of graphs in the dataset')

    def test_number_of_nodefeatures(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)

        self.assertEqual(dataset.num_node_features, 11, 'wrong number of node features')

    def test_dimension_of_nodefeatures(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)

        for g, graph in enumerate(dataset):
            element = dataset.__getitem__(g)
            self.assertEqual(element.x.dim(), 2, 'node tensor has wrong dimension')

    def test_edge_dimension(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)

        for g, graph in enumerate(dataset):
            element = dataset.__getitem__(g)
            self.assertEqual(element.edge_index.dim(), 2, 'edge tensor has wrong dimension')

    def test_edge_attribute_dimension(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)

        for g, graph in enumerate(dataset):
            element = dataset.__getitem__(g)
            self.assertEqual(element.edge_attr.dim(), 2, 'edge attribute tensor has wrong dimension')

unittest.main()