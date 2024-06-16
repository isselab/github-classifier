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
import torch.nn.functional as nn
import numpy as np
from torch_geometric.datasets import TUDataset
from GraphClasses import defined_labels
from sklearn.metrics import f1_score

#repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/labeled_repos_first100'
#labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset
labels = '../labeled_repos_first100.xlsx'
n_epoch = 50
k_folds = 4
learning_rate = 0.001
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'

def train():
        model.train()
        
        num_classes = int(len(defined_labels))

        for graph in trainloader: 

            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            
            size = int(len(graph.y)/num_classes)
            graph.x = nn.normalize(graph.x, p=2.0)
            graph.y = torch.reshape(graph.y, (size, num_classes))
            output = model(graph.x, graph.edge_index, graph.batch)
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
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)

            size = int(len(graph.y)/num_classes)
            graph.y = torch.reshape(graph.y, (size, num_classes))
            output = model(graph.x, graph.edge_index, graph.batch)
            loss = criterion(output, graph.y)
            loss_test += loss.item()
            #pred = output.argmax(dim=1)
            #print(graph.y.size())
            #acc = (output.argmax(dim=0) == graph.y.argmax(dim=0)).float().mean()
            #print(acc)
            #correct += (output == graph.y).sum().item()
            total += len(loader.dataset)
            #results[f] = 100.0 * (correct / total)

            output = output.cpu().detach().numpy()
            graph.y = graph.y.cpu().detach().numpy()
            #print(output)
            prediction = np.argmax(output, axis=1)
            ground_truth = np.argmax(graph.y, axis=1)
            acc_train = (prediction == ground_truth).sum()
            #print(output)
            #correct = f1_score(graph.y, output, average=None, labels=graph_types)
            results[f] = 100.0 * (correct / total)
        
        #return correct/len(loader.dataset), loss_test/len(loader.dataset)
        #return results[f], loss_test/len(loader)
        return acc_train/total , loss_test/total


# create the graph dataset of the repositories
#try:
   # prepare_dataset(repository_directory, output_directory)
#except Exception as e:
   # print(e)

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
    #dataset_path = "data/TUDataset"
    #dataset = TUDataset(root=dataset_path, name='MUTAG')
    print(f'Dataset size: {dataset.__len__()}')
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')


device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=64) #in paper K=10

if device == 'cuda':
    model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), learning_rate) #, weight_decay=1e-3 with Adam, no change
#criterion = torch.nn.MSELoss() #loss function that can deal with multi-target
criterion = torch.nn.BCEWithLogitsLoss()

kfold = KFold(n_splits=k_folds, shuffle=True)

#fold results
results = {}

#initialize overall performance with negative infinity
best_acc = - np.inf

for f, fold in enumerate(kfold.split(dataset)):
    # split into train and testset, this is for training the tool, not using finished tool
    trainset, testset = random_split(dataset, [0.9, 0.1]) #more training data
    print(f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=1, shuffle=False)
    print(f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')

    #log model parameters
    params = {"lr": learning_rate}
    for name, param in model.named_parameters():
        if param.requires_grad:
            params[f"{name}"] = param.data

    with mlflow.start_run():
        plt_epoch = []
        plt_test_acc = []
        plt_test_loss = []
        mlflow.log_params(params)

        for epoch in range(1, n_epoch):
            print(f'Fold {f}, Epoch {epoch}')
            train()
            train_acc, train_loss= test(trainloader)
            test_acc, test_loss = test(testloader)
            
            metrics = {"training accuracy":train_acc, "training loss":train_loss, "test accuracy":test_acc, "test loss":test_loss}
            mlflow.log_metrics(metrics, step=epoch)

            plt_epoch.append(epoch)
            plt_test_acc.append(test_acc)
            plt_test_loss.append(test_loss)

            print(f'training acc: {train_acc}, training loss: {train_loss}')
            print(f'testing acc: {test_acc}, testing loss: {test_loss}')
            print('==============================================')

            #save trained model with best performance
            if test_acc > best_acc:
                best_acc = test_acc
                #save_path = f'./graph_classification_model_fold{f}.pt'
                torch.save(model, 'graph_classification_model.pt')
    
        #visualization of accuracy and loss from testing
        fig = plt.figure(f)
        plt.title(f"Fold {f}")
        p1 = plt.subplot(2, 1, 1)
        plt.plot(plt_epoch, plt_test_acc, 'b')
        plt.setp(p1.get_xticklabels(), visible=False)
        plt.ylabel('test accuracy')

        p2 = plt.subplot(2, 1, 2, sharex=p1)
        plt.plot(plt_epoch, plt_test_loss, 'r')
        plt.setp(p2.get_xticklabels())
        plt.xlabel('epoch')
        plt.ylabel('test loss')

        plt.savefig(f'{figure_output}/fig_{f}.pdf', bbox_inches='tight')

# Print fold results
print(f'K-FOLD CROSS VALIDATION RESULTS FOR {k_folds} FOLDS')
print('--------------------------------')
sum = 0.0
for key, value in results.items():
    print(f'Fold {key}: {value} %')
    sum += value
print(f'Average: {sum/len(results.items())} %') #check if computation is correct/matches my thingi
