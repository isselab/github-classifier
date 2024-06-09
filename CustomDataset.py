from torch.utils.data import Dataset
from torch_geometric.data import Data
import os
import pandas as pd
import torch
import numpy as np
from DefinedGraphClasses import graph_types
from Encoder import label_encoding, one_hot_encoding
from DataformatUtils import convert_edge_dim, convert_list_to_floattensor, convert_list_to_longtensor, convert_list_to_inttensor

class RepositoryDataset(Dataset):
    def __init__(self, directory, label_list=None):
        if label_list is not None:
            try:
                self.encoded_labels = self.convert_labeled_graphs(label_list)
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
                # create list of graphs to load graph via index and look up name to load graph from file
                if self.node_name == self.edge_name and self.node_name not in self.graph_names:
                    self.graph_names.append(self.node_name)
            except Exception as e:
                print(e)
                print(f'There is a problem loading {graph}')
        # load labels for graphs in correct order and return them in tensor
        if hasattr(self, 'encoded_labels'):
            self.y = self.sort_labels()
            print(f'Number of Applications: {self.class_elements[0]}, Experiments: {self.class_elements[1]}, Frameworks: {self.class_elements[2]}, Libraries: {self.class_elements[3]}, Tutorials: {self.class_elements[4]}')

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
                    self.x = convert_list_to_floattensor(node_features)
                if f'{graph_name}_A' in graph:
                    adjacency = pd.read_csv(f'{self.directory}/{graph}', header=None)
                    edge_tensor = convert_list_to_longtensor(adjacency)
                    self.edge_index = convert_edge_dim(edge_tensor)
            except Exception as e:
                print(e)
        graph = Data(x=self.x, edge_index=self.edge_index)
        if hasattr(self, 'y'):
            label = self.y[index]
            graph.y = label
        return graph

    def sort_labels(self):
        label_list = list(self.encoded_labels)
        sorted = None
        for n, item in enumerate(self.graph_names):
            for i, name in enumerate(label_list):
                if item == name[0]:
                    label = name[1]
                    if sorted is None:
                        sorted = np.array(label)
                    else:
                        sorted = np.vstack((sorted, label)).astype(np.float16)
        y = torch.FloatTensor(sorted)
        return y
    
    '''takes two directory paths as input and converts the labeled dataset into 
        a csv file, it loads the dataset from excel/ods file,
        requirements for format: no empty rows in between and header names for columns'''
    def convert_labeled_graphs(self, labels):
        resource = pd.read_excel(labels)
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
        
        self.class_elements = self.count_class_elements(graph_labels) #count how many repos are in each class

        #encode labels
        encoded_nodes = one_hot_encoding(graph_types, graph_labels)
        file = zip(graph_names, encoded_nodes)
        return file
    
    def count_class_elements(self, labels):
        app = 0
        lib = 0
        frame = 0
        exp = 0
        tut = 0
        for element in labels:
            if 'Application' in element:
                app += 1
            if 'Library' in element:
                lib += 1
            if 'Framework' in element:
                frame += 1
            if 'Experiment' in element:
                exp += 1
            if 'Tutorial' in element:
                tut += 1
        counted_elements = [app, exp, frame, lib, tut]
        return counted_elements

    '''DEPRECATED, DELETE LATER, normalize to avoid bias with node types'''
    def normalize_matrix(self, matrix):
        norm = np.linalg.norm(matrix)
        normalized_matrix = matrix/norm
        return normalized_matrix
