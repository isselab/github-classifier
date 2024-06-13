from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from GCN import GCN
#from GCN_ChebConv import GCN
import torch
import mlflow
import matplotlib.pylab as plt
from sklearn.model_selection import KFold

repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/tool_output'
labels = '../test_notexclusive.xls' # labeled repositories for the training dataset
n_epoch = 200
k_folds = 2
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'


try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')