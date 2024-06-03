from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
#from GCN import GCN
from GCN_ChebConv import GCN
import torch
import mlflow

repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/tool_output'
labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset
n_epoch = 5

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

# split into train and testset, this is for training the tool, not using finished tool
trainset, testset = random_split(dataset, [0.9, 0.1]) #more training data
print(f'size of train dataset: {len(trainset)}, test dataset: {len(testset)}')

trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
testloader = DataLoader(testset, batch_size=1, shuffle=False)
print(f'number of batches in train dataset: {len(trainloader)}, test dataset: {len(testloader)}')

#mlflow.autolog() #only added this for logging (and plotting)
#exp_id = mlflow.create_experiment('Test')

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=64, K=6) #in paper K=10

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

def train():
    model.train()
    
    for graph in trainloader: 
        output = model(graph.x, graph.edge_index, graph.batch)
        loss_train = criterion(output, graph.y) #graph.y is label
        loss_train.backward() #backward propagation to update weights? do this for entire batch for performance i think
        optimizer.step()
        optimizer.zero_grad()

def test(loader):
    model.eval()

    correct = 0
    for graph in loader:
        output = model(graph.x, graph.edge_index, graph.batch)
        pred = output.argmax(dim=1)
        correct += int((pred == graph.y).sum())
    return correct/len(loader.dataset)

with mlflow.start_run():

  for epoch in range(1, n_epoch):
    print(f'Epoch {epoch}')
    train()
    train_acc = test(trainloader)
    test_acc = test(testloader)

    #mlflow.log_params(model.parameters())
    mlflow.log_metric("accuracy", test_acc, step=epoch)

    print(f'training acc: {train_acc}')
    print(f'testing acc: {test_acc}')
    print('==============================================')

#save trained model in file
torch.save(model, 'graph_classification_model.pt') #alt.: state dict