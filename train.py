from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from GCN import GCN
import torch

#repository_directory = 'D:/dataset_repos'  # input repositories
#output_directory = 'D:/output'  
output_directory = 'D:/tool_output'
labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset

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
trainset, testset = random_split(dataset, [0.7, 0.3])
print(len(trainset), len(testset))

trainloader = DataLoader(trainset, batch_size=16, shuffle=True)
testloader = DataLoader(testset, batch_size=1, shuffle=False)
print(f'number of batches: {len(trainloader)}, {len(testloader)}')

for step, data in enumerate(trainloader):
    print(f'Step {step + 1}:')
    print('=======')
    print(f'Number of graphs in the current batch: {data.num_graphs}')
    print(data)
    print()
    print(len(data.x))

model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels=64)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

'''accuracy func not used right now, maybe never'''
def accuracy(output, labels):
    preds = output.max(1)[1].type_as(labels)
    correct = preds.eq(labels).double()
    correct = correct.sum()
    return correct / len(labels)

def train():
    model.train()
    
    for graph in trainloader: 
        output = model(graph.x, graph.edge_index, graph.batch)
        loss_train = criterion(output, graph.y) #graph.y is label
        #acc_train = accuracy(output, graph.y)
        loss_train.backward() #backward propagation to update weights? do this for entire batch for performance i think
        optimizer.step()
        optimizer.zero_grad()

def test(loader):
    model.eval()
    loss_test = 0
    correct = 0
    for graph in loader:
        output = model(graph.x, graph.edge_index, graph.batch)
        loss = criterion(output, graph.y)
        loss_test += loss.item()
        pred = output.argmax(dim=1)
        #correct = accuracy(output, graph.y)
        correct += int((pred == graph.y).sum())
    return correct/len(loader.dataset), loss_test/len(loader.dataset)

for epoch in range(1,20):
    train()
    train_acc, train_loss = test(trainloader) #this cause issues with shape/dimension
    test_acc, test_loss = test(testloader)
    print(f'training acc: {train_acc}, loss: {train_loss}')
    print(f'testing acc: {test_acc}, loss: {test_loss}')

#save trained model in file
torch.save(model, 'graph_classification_model.pt')