from torch.utils.data import Dataset
from torch_geometric.data import Data
import os
import pandas as pd
import torch
import numpy as np
from GraphClasses import defined_labels
from Encoder import multi_hot_encoding
from DataformatUtils import convert_edge_dim, convert_list_to_floattensor, convert_list_to_longtensor, convert_hashed_names_to_float

class RepositoryDataset(Dataset):
    def __init__(self, directory, label_list=None):
        if label_list is not None:
            try:
                self.encoded_labels = self.convert_labeled_graphs(label_list)
            except Exception as e:
                print(e)
        self.num_node_features = 11  #nodes have 11 features, their one hot encoded node type, hashed name, and one hot encoded library flag
        self.num_classes = len(defined_labels)
        self.directory = directory
        self.graph_names = []
        self.graph_dir = os.listdir(directory)
        for g, graph in enumerate(self.graph_dir):
            if '_nodefeatures.csv' in graph:
                graph_name = graph.removesuffix('_nodefeatures.csv')
                if graph_name not in self.graph_names:
                    self.graph_names.append(graph_name)
        
        self.check_dataset() #check if every graph can be loaded

        #load labels for graphs in correct order and return them in tensor
        if hasattr(self, 'encoded_labels'):
            self.y = self.sort_labels()
            print(f'Number of Applications: {self.class_elements[0]}, Frameworks: {self.class_elements[1]}, Libraries: {self.class_elements[2]}, Plugins: {self.class_elements[3]}')

    #returns number of samples (graphs) in the dataset
    def __len__(self):
        size = len(self.graph_names)
        return size

    '''fetches pair (sample, label) from the dataset at index position, indexing starts at 0,
    when dataset is not used for training and has no labels only graph in the dataset at index position is returned'''
    def __getitem__(self, index):
        graph_name = self.graph_names[index]
        for g,graph in enumerate(self.graph_dir):
            try:
                if f'{graph_name}_nodefeatures.csv' == graph:
                    node_features = pd.read_csv(f'{self.directory}/{graph}', header=None)  #load csv file
                    self.x = convert_hashed_names_to_float(node_features)
                if f'{graph_name}_A.csv' == graph:
                    adjacency = pd.read_csv(f'{self.directory}/{graph}', header=None)
                    edge_tensor = convert_list_to_longtensor(adjacency)
                    self.edge_index = convert_edge_dim(edge_tensor)
                if f'{graph_name}_edge_attributes.csv' == graph:
                    edge_attributes = pd.read_csv(f'{self.directory}/{graph}', header=None)
                    self.edge_attr = convert_list_to_floattensor(edge_attributes)
            except Exception as e:
                print(graph, e)
        if hasattr(self, 'x') and hasattr(self, 'edge_index'):
            graph = Data(x=self.x, edge_index=self.edge_index)
        if hasattr(self, 'y'):
            label = self.y[index]
            graph.y = label
        if hasattr(self, 'edge_attr'):
            graph.edge_attr = self.edge_attr
        return graph
    
    '''sorts labels according to order of graphs, so the labels belonging to a graph share the same index position 
    as the graph'''
    def sort_labels(self):
        label_list = list(self.encoded_labels)
        sorted = None
        for n, item in enumerate(self.graph_names):
            for i, name in enumerate(label_list):
                if item == name[0]:
                    label = name[1]
                    if sorted is None:
                        sorted = np.array(label, dtype=np.float16)
                    else:
                        sorted = np.vstack((sorted, label)).astype(np.float16)
        y = torch.FloatTensor(sorted)
        return y
    
    '''takes directory path of excel file with labeled repositories as input and converts the 
        labeled dataset into a one hot encoded torch tensor/python list,
        requirements for format: no empty rows in between and header names 'html_url' for repo column
        and 'final type' for label column'''
    def convert_labeled_graphs(self, labels):
        resource = pd.read_excel(labels)
        graph_labels = []
        graph_names = []

        #iterate over loaded file and retrieve labels
        for row in resource.iterrows():
            object = row[1]
            url = object.get('html_url') #column header containing repository url
            repo_name = url.split('/')[-1]  #last element is repository name
            graph_names.append(repo_name)
            type_label = object.get('final type') #column header containing label
            graph_labels.append(type_label)
        
        self.class_elements = self.count_class_elements(graph_labels) #count how many repos are in each class

        #encode labels
        encoded_nodes = multi_hot_encoding(defined_labels, graph_labels)
        file = zip(graph_names, encoded_nodes)
        return file
    
    def count_class_elements(self, labels):
        app = 0
        frame = 0
        lib = 0
        plugin = 0
        try:
            for element in labels:
                if 'Application' in element:
                    app += 1
                if 'Framework' in element:
                    frame += 1
                if 'Library' in element:
                    lib += 1
                if 'Plugin' in element:
                    plugin += 1
        except Exception as e:
            print(e)
            print('Problem with the Labels')
        counted_elements = [app, frame, lib, plugin]
        return counted_elements
    
    '''checks if the graphs in the dataset can be loaded, if not, for example because a file is empty, 
    the graph is removed from the dataset'''
    def check_dataset(self):
        for i, item in enumerate(self.graph_names):
            graph_name = self.graph_names[i]
            for g,graph in enumerate(self.graph_dir):
                try:
                    if f'{graph_name}_nodefeatures.csv' == graph:
                        node_features = pd.read_csv(f'{self.directory}/{graph}', header=None)
                    if f'{graph_name}_A.csv' == graph:
                        adjacency = pd.read_csv(f'{self.directory}/{graph}', header=None)
                    if f'{graph_name}_edge_attributes.csv' == graph:
                        edge_attributes = pd.read_csv(f'{self.directory}/{graph}', header=None)
                except Exception as e:
                    if graph_name in self.graph_names:
                        self.graph_names.remove(graph_name)
                        print(f'{graph}, {e}, removing {graph_name} from dataset')
