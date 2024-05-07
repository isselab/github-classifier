from torch.utils.data import Dataset
import os
import pandas as pd
import torch
import numpy as np

class RepositoryDataset(Dataset):
    def __init__(self, directory):
        self.graph_list = []
        self.node_name = 'Test1'
        self.edge_name = 'Test2'
        self.graph_names = []
        graph_dir = os.listdir(directory)
        for g,graph in enumerate(graph_dir):
            if '_nodes' in graph:
                node_features = pd.read_csv(f"{directory}/{graph}", header=None) #load csv file
                self.node_tensor = torch.LongTensor(np.array(node_features)) #convert DataFrame object
                self.node_name = graph.removesuffix('_nodes.csv')
            if '_A' in graph:
                adjacency = pd.read_csv(f"{directory}/{graph}", header=None)
                self.edge_tensor = torch.LongTensor(np.array(adjacency))
                self.edge_name = graph.removesuffix('_A.csv')
            if 'graph_labels' in graph:
                graph_label = pd.read_csv(f"{directory}/{graph}", header=None)
                self.graph_labels = torch.LongTensor(np.array(graph_label))
            if self.node_name == self.edge_name and self.node_name not in self.graph_names:
                loaded_graph = (self.node_tensor, self.edge_tensor)
                self.graph_list.append(loaded_graph)
                self.graph_names.append(self.node_name)

    def __len__(self):
        size = len(self.graph_list)
        return size
    
    def __getitem__(self, index):
        graph = self.graph_list[index]
        label = self.graph_labels[index]
        return graph, label