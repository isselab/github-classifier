from CustomDataset import RepositoryDataset
from Pipeline import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from GCN import GCN
#from GCN_ChebConv import GCN
import torch
import mlflow
import matplotlib.pylab as plt
from sklearn.model_selection import RepeatedKFold
import torch.nn.functional as nn
import numpy as np
from GraphClasses import defined_labels
#from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import multilabel_confusion_matrix

#repository_directory = 'D:/dataset_repos'  # input repositories
#output_directory = 'D:/testing'
output_directory = 'D:/labeled_repos_first100'
#labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset
labels = '../labeled_repos_first100.xlsx'
#labels = 'D:/testing.xlsx'
n_epoch = 2
k_folds = 4
learning_rate = 0.001
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'

def train():
        model.train()
        
        num_classes = int(len(defined_labels))

        for graph in trainloader: 
            #print(graph.x)
            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                #graph.edge_attr = graph.edge_attr.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            #prepare input
            size = int(len(graph.y)/num_classes)
            graph.x = nn.normalize(graph.x, p=0.5)
            #print(graph.x)
            #for item in graph.x:
                #print(item)
            #graph.edge_attr = nn.normalize(graph.edge_attr, p=2.0)
            graph.y = torch.reshape(graph.y, (size, num_classes))
            #print(graph.y.size())
            
            output = model(graph.x, graph.edge_index, graph.batch)
            #print(output.size())
            loss_train = criterion(output, graph.y) #graph.y is label

            #backpropagation
            optimizer.zero_grad()
            loss_train.backward()

            #update weights
            optimizer.step()

def test(loader):
        model.eval()
        loss_test = 0
        correct, total = 0, 0
        num_classes = int(len(defined_labels))

        for graph in loader:

            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                #graph.edge_attr = graph.edge_attr.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            #prepare input
            size = int(len(graph.y)/num_classes)
            graph.y = torch.reshape(graph.y, (size, num_classes))

            #evaluate model
            output = model(graph.x, graph.edge_index, graph.batch)
            loss = criterion(output, graph.y)
            loss_test += loss.item()
            total += len(loader)

            output = output.cpu().detach().numpy()
            graph.y = graph.y.cpu().detach().numpy()
            #print(output)
            #acc = 0
            output = (output > 0.5) #bad in my case
            #maybe do this with for loop? to get matrix with either 1 if above threshold or 0 if below? maybe important?
            #output = np.argmax(output, axis=1)
            print(output)
            graph.y = (graph.y > 0.5)
            #graph.y = np.argmax(graph.y, axis=1)
            print(graph.y)
            acc = accuracy_score(graph.y, output)
            confusion_matrix = multilabel_confusion_matrix(graph.y, output)

        return acc, loss_test/total, confusion_matrix


# create the graph dataset of the repositories, already done
#try:
   # prepare_dataset(repository_directory, output_directory)
#except Exception as e:
   # print(e)

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
    print(f'Dataset size: {dataset.__len__()}')
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')

device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=32) #in paper K=10

if device == 'cuda':
    model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), learning_rate)
criterion = torch.nn.MultiLabelSoftMarginLoss()
#criterion = torch.nn.BCEWithLogitsLoss() #loss function that can deal with multilabel

#repeated k fold runs k_folds*n_epoch times
kfold = RepeatedKFold(n_splits=k_folds, n_repeats=n_epoch, random_state=1)

#fold results
results = []
#results = {}

#initialize overall model performance with negative infinity
best_acc = - np.inf

#training loop
for f, fold in enumerate(kfold.split(dataset)):
    # split into train and testset, this is for training the tool, not using finished tool
    trainset, testset = random_split(dataset, [0.9, 0.1]) #more training data
    print(f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=1, shuffle=False)
    print(f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')
    
    print(f'Fold: {f}')
    #train model, do i need the pochs here? or is that covered by repeated kfold?
    train()
    train_acc, train_loss, train_conf = test(trainloader)
    test_acc, test_loss, test_conf = test(testloader)

    #print results
    print('training accuracy:')
    print('%.3f' % train_acc)
    #results.append(train_acc)
    print(train_conf)

    print('testing accuracy:')
    print('%.3f' % test_acc)
    print(test_conf)
    results.append(test_acc)
