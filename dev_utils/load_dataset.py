from CustomDataset import RepositoryDataset
from Pipeline import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from GCN import GCN
#from GCN_ChebConv import GCN
import torch
import mlflow
import matplotlib.pylab as plt
from sklearn.model_selection import KFold

#repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/labeled_repos_first100'
labels = '../labeled_repos_first100.xlsx' # labeled repositories for the training dataset
#n_epoch = 5
#k_folds = 2
#figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'


try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
    print(dataset.__len__())
    count_label = 0
    count_features = 0
    count_edges = 0
    for graph in dataset:
        #print(graph.y)
        #print(type(graph))
        if isinstance(graph.y, torch.FloatTensor):
            count_label += 1
        if isinstance(graph.x, torch.FloatTensor):
            count_features += 1
        if isinstance(graph.edge_index, torch.LongTensor):
            count_edges += 1
    print(count_label)
    print(count_features)
    print(count_edges)
    graph0 = dataset.__getitem__(0)
    print(graph0.y)
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')

loader = DataLoader(dataset, batch_size=32, shuffle=True)

for graph in loader:
    size = int(len(graph.y)/5)
    re_label = torch.reshape(graph.y, (size, 5))
    print(re_label)