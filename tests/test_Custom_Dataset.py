from CustomDataset import RepositoryDataset
import unittest

'''the dataset loaded here consists of the same unit tests as the other tests, but for the purpose 
of testing loading the dataset, the output of the converters were saved in files,
the tests checking the dimension of the graph components also ensure that they can be accessed at all,
since these tests are done with unit tests, there are no labels right now, might change later for more testing'''

output_directory = 'D:/testing'

class TestCustomDataset(unittest.TestCase):

    def test_dataset_size(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files')

        #the length is 26 because the graphs without any edges cannot be loaded, throws 'no columns to parse from file' error
        self.assertEqual(dataset.__len__(), 26, 'wrong number of graphs in the dataset')

    def test_number_of_nodefeatures(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files')

        self.assertEqual(dataset.num_node_features, 11, 'wrong number of node features')

    def test_dimension_of_nodefeatures(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files')

        for g, graph in enumerate(dataset):
            element = dataset.__getitem__(g)
            self.assertEqual(element.x.dim(), 2, 'node tensor has wrong dimension')

    def test_edge_dimension(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files')

        for g, graph in enumerate(dataset):
            element = dataset.__getitem__(g)
            self.assertEqual(element.edge_index.dim(), 2, 'edge tensor has wrong dimension')

    def test_edge_attribute_dimension(self):
        dataset = RepositoryDataset(f'{output_directory}/csv_files')

        for g, graph in enumerate(dataset):
            element = dataset.__getitem__(g)
            self.assertEqual(element.edge_attr.dim(), 2, 'edge attribute tensor has wrong dimension')

unittest.main()