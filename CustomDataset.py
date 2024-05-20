from torch.utils.data import Dataset
import os
import pandas as pd
import torch
import numpy as np
from DefinedGraphClasses import graph_types
from LabelEncoder import convert_labels

#custom dataset
class RepositoryDataset(Dataset):
    def __init__(self, directory):
        self.num_node_features = 1 #nodes only have its type as feature
        self.num_classes = len(graph_types)
        self.graph_list = []
        self.node_name = 'Test1'
        self.edge_name = 'Test2'
        self.graph_names = []
        graph_dir = os.listdir(directory)
        for g,graph in enumerate(graph_dir):
            try:
                if '_nodefeatures' in graph: 
                    #it may be necessary to use FloatTensor for different shape for x?? dont know
                    node_features = pd.read_csv(f'{directory}/{graph}', header=None) #load csv file
                    self.node_tensor = torch.LongTensor(np.array(node_features)) #convert DataFrame object
                    self.node_name = graph.removesuffix('_nodefeatures.csv')
                if '_A' in graph:
                    adjacency = pd.read_csv(f'{directory}/{graph}', header=None)
                    self.edge_tensor = torch.LongTensor(np.array(adjacency))
                    self.edge_name = graph.removesuffix('_A.csv')
                if 'graph_labels' in graph: 
                    graph_label = pd.read_csv(f'{directory}/{graph}', header=None)
                    self.gr_name = np.array(graph_label[0])
                    self.gr_label = np.array(graph_label[1])
                #create graph = tuple of edges and node features
                if self.node_name == self.edge_name and self.node_name not in self.graph_names:
                    loaded_graph = (self.node_tensor, self.edge_tensor)
                    self.graph_list.append(loaded_graph)
                    self.graph_names.append(self.node_name)
            except Exception as e:
                print(e)
                print(f'There is a problem loading {graph}')
        #load labels for graphs in correct order and return them in tensor
        if hasattr(self, 'gr_name'):
            self.graph_labels = self.sort_labels()

    #returns number of samples (graphs) in the dataset
    def __len__(self):
        size = len(self.graph_list)
        return size
    
    #fetches pair (sample, label) from the dataset at index position, indexing starts at 0
    def __getitem__(self, index):
        graph = self.graph_list[index] 
        label = self.graph_labels[index]
        return graph, label
    
    def sort_labels(self):
        sort = []
        for item in self.graph_names:
            for i, name in enumerate(self.gr_name):
                if item == name:
                    label = self.gr_label[i]
                    sort.append(label)
        sorted_labels = torch.LongTensor(np.array(sort))
        return sorted_labels
    
    #takes two folders as input
    def convert_labeled_graphs(labels, output_graph_labels):
        #load labeled repository from excel/ods file
        resource = pd.read_excel(labels) #requirements for format: no empty rows in between and header names for columns

        new_resource_nodes = open(f"{output_graph_labels}/graph_labels.csv", "w+")
        graph_labels = []
        graph_names = []

        #iterate over loaded file and retrieve labels
        for row in resource.iterrows():
            object = row[1]
            url = object.get('html_url') 
            repo_name = url.split('/')[-1] #last element is repository name
            graph_names.append(repo_name)
            type_label = object.get('type') 
            graph_labels.append(type_label)

        #encode labels numerically
        encoded_nodes = convert_labels(graph_types, graph_labels)
        file = zip(graph_names, encoded_nodes)

        #write encoded labels into a file for the dataset
        for item in list(file):
            name = item[0]
            new_resource_nodes.write("%s, " % name)
            label = item[1]
            new_resource_nodes.write("%s" % label)
            new_resource_nodes.write("\n")
        new_resource_nodes.close()
    
    #normalize to avoid bias, leave out for now
    def normalize_matrix(matrix):
        norm = np.linalg.norm(matrix)
        normalized_matrix = matrix/norm
        return normalized_matrix