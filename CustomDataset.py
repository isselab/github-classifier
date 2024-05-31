from torch.utils.data import Dataset
from torch_geometric.data import Data
import os
import pandas as pd
import torch
import numpy as np
from DefinedGraphClasses import graph_types
from LabelEncoder import convert_labels

class RepositoryDataset(Dataset):
    def __init__(self, directory, label_list=None):
        if label_list is not None:
            try:
                self.convert_labeled_graphs(label_list, directory)
            except Exception as e:
                print(e)
        self.num_node_features = 1  # nodes only have its type as feature
        self.num_classes = len(graph_types)
        self.directory = directory
        self.node_name = 'Test1'
        self.edge_name = 'Test2'
        self.graph_names = []
        self.graph_dir = os.listdir(directory)
        for g, graph in enumerate(self.graph_dir):
            try:
                if '_nodefeatures' in graph:
                    self.node_name = graph.removesuffix('_nodefeatures.csv')
                if '_A' in graph:
                    self.edge_name = graph.removesuffix('_A.csv')
                if 'graph_labels' in graph:
                    graph_label = pd.read_csv(f'{directory}/{graph}', header=None)
                    self.gr_name = np.array(graph_label[0])
                    self.gr_label = np.array(graph_label[1])
                # create list of graphs to load graph via index and look up name to load graph from file
                if self.node_name == self.edge_name and self.node_name not in self.graph_names:
                    self.graph_names.append(self.node_name)
            except Exception as e:
                print(e)
                print(f'There is a problem loading {graph}')
        # load labels for graphs in correct order and return them in tensor
        if hasattr(self, 'gr_name'):
            self.y = self.sort_labels()

    # returns number of samples (graphs) in the dataset
    def __len__(self):
        size = len(self.graph_names)
        return size

    '''fetches pair (sample, label) from the dataset at index position, indexing starts at 0
    returns only graph in the dataset at index position, when dataset is not used for training and has no labels'''
    def __getitem__(self, index):
        graph_name = self.graph_names[index]
        for g,graph in enumerate(self.graph_dir):
            try:
                if f'{graph_name}_nodefeatures' in graph:
                    node_features = pd.read_csv(f'{self.directory}/{graph}', header=None)  # load csv file
                    x = torch.Tensor(np.array(node_features))  # convert DataFrame object
                    self.x = self.normalize_matrix(x)
                if f'{graph_name}_A' in graph:
                    adjacency = pd.read_csv(f'{self.directory}/{graph}', header=None)
                    edge_tensor = torch.LongTensor(np.array(adjacency))
                    self.edge_index = self.convert_edge_dim(edge_tensor)
            except Exception as e:
                print(e)
        graph = Data(x=self.x, edge_index=self.edge_index)
        if hasattr(self, 'y'):
            label = self.y[index]
            graph.y = label
        return graph

    def sort_labels(self):
        sort = []
        for item in self.graph_names:
            for i, name in enumerate(self.gr_name):
                if item == name:
                    label = self.gr_label[i]
                    sort.append(label)
        y = torch.Tensor(np.array(sort))
        return y
    
    '''this function takes two directory paths as input and converts the labeled dataset into 
        a csv file, it loads the dataset from excel/ods file,
        requirements for format: no empty rows in between and header names for columns'''
    def convert_labeled_graphs(self, labels, directory):
        resource = pd.read_excel(labels)
        new_resource_nodes = open(f"{directory}/graph_labels.csv", "w+")
        graph_labels = []
        graph_names = []

        # iterate over loaded file and retrieve labels
        for row in resource.iterrows():
            object = row[1]
            url = object.get('html_url')
            repo_name = url.split('/')[-1]  # last element is repository name
            graph_names.append(repo_name)
            type_label = object.get('type')
            graph_labels.append(type_label)

        # encode labels numerically
        encoded_nodes = convert_labels(graph_types, graph_labels)
        file = zip(graph_names, encoded_nodes)

        # write encoded labels into a file for the dataset
        for item in list(file):
            name = item[0]
            new_resource_nodes.write("%s, " % name)
            label = item[1]
            new_resource_nodes.write("%s" % label)
            new_resource_nodes.write("\n")
        new_resource_nodes.close()

    '''change the shape of the edge tensor to E=[2, number of edges]'''
    def convert_edge_dim(self, edge_tensor):
        edge_tensor = edge_tensor.permute(1,0)
        return edge_tensor
    
    '''normalize to avoid bias with node types'''
    def normalize_matrix(self, matrix):
        norm = np.linalg.norm(matrix)
        normalized_matrix = matrix/norm
        return normalized_matrix
