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
import torch.nn.functional as nn

repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/tool_output'
labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset
n_epoch = 50
k_folds = 2
figure_output = 'C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'

def train():
        model.train()
    
        for graph in trainloader: 
            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            graph.x = nn.normalize(graph.x, p=2.0)
            #graph.edge_index = nn.normalize(graph.edge_index, p=2.0)
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
        for graph in loader:
            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                graph.y = graph.y.to(device)
                graph.batch = graph.batch.to(device)
            output = model(graph.x, graph.edge_index, graph.batch)
            loss = criterion(output, graph.y)
            loss_test += loss.item()
            pred = output.argmax(dim=1)
            #print(graph.y.size())
            #acc = (output.argmax(dim=1) == graph.y.argmax(dim=0)).float().mean()
            correct += int((pred == graph.y).sum())  
            total += graph.y.size(0)  
            results[f] = 100.0 * (correct / total)
        
        return correct/len(loader.dataset), loss_test/len(loader.dataset)


# create the graph dataset of the repositories
#try:
   # prepare_dataset(repository_directory, output_directory)
#except Exception as e:
   # print(e)

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files', labels)
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')


device = 'cuda' if torch.cuda.is_available() else 'cpu'

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=64) #in paper K=10

if device == 'cuda':
    model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001) #, weight_decay=1e-3 with Adam, no change
criterion = torch.nn.NLLLoss() #CrossEntropyLoss

kfold = KFold(n_splits=k_folds, shuffle=True)

# For fold results
results = {}

for f, fold in enumerate(kfold.split(dataset)):
    # split into train and testset, this is for training the tool, not using finished tool
    trainset, testset = random_split(dataset, [0.9, 0.1]) #more training data
    print(f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

    trainloader = DataLoader(trainset, batch_size=64, shuffle=True)
    testloader = DataLoader(testset, batch_size=1, shuffle=False)
    print(f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')

#mlflow.autolog() #only added this for logging (and plotting)
#exp_id = mlflow.create_experiment('Test')

    with mlflow.start_run():
        plt_epoch = []
        plt_test_acc = []
        plt_test_loss = []
        for epoch in range(1, n_epoch):
            print(f'Fold {f}, Epoch {epoch}')
            train()
            train_acc, train_loss= test(trainloader)
            test_acc, test_loss = test(testloader)

            #mlflow.log_params(model.parameters())
            mlflow.log_metric("accuracy", test_acc, step=epoch)
            mlflow.log_metric("loss", test_loss, step=epoch)
            plt_epoch.append(epoch)
            plt_test_acc.append(test_acc)
            plt_test_loss.append(test_loss)

            print(f'training acc: {train_acc}, training loss: {train_loss}')
            print(f'testing acc: {test_acc}, testing loss: {test_loss}')
            print('==============================================')
    
        #plot visualization of accuracy and loss from testing in figure also for entire folds?
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

        #plt.show() #save instead of showing
        plt.savefig(f'{figure_output}/fig_{f}.pdf', bbox_inches='tight')

        #save trained model in file
        save_path = f'./graph_classification_model_fold{f}.pt'
        torch.save(model, save_path)


# Print fold results
print(f'K-FOLD CROSS VALIDATION RESULTS FOR {k_folds} FOLDS')
print('--------------------------------')
sum = 0.0
for key, value in results.items():
    print(f'Fold {key}: {value} %')
    sum += value
print(f'Average: {sum/len(results.items())} %') #check if computation is correct/matches my thingi
