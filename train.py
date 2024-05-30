from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split
from GCN import GCN
import torch
from GCNUtils import prepare_input_data
#import torch.nn.functional as F

#repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/output'  
labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset

# create the graph dataset of the repositories
#try:
   # prepare_dataset(repository_directory, output_directory)
#except Exception as e:
   # print(e)

print('---convert dataset labels for training---')
try:
    '''labeled repositories should have column headers 'html_url' and 'type', and no empty lines in the columns'''
    RepositoryDataset.convert_labeled_graphs(labels, f'{output_directory}/csv_files')
except Exception as e:
    print(e)
    print('There is a problem with the labeled dataset. Check format in excel file. Labeled repositories should have column headers html_url and type, and no empty lines in the columns!')

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files')
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')

# split into train and testset, this is for training the tool, not using finished tool
trainset, testset = random_split(dataset, [0.5, 0.5])
print(len(trainset), len(testset))

'''i need to implement shuffling and iterating in batches over training set??'''
nodes = trainset[0][0][0]
edges = trainset[0][0][1]
print(f'{nodes.size()}, dimension 0: {nodes.size(dim=0)}, dimension 1: {nodes.size(dim=1)}')
print(f'{edges.size()}, dimension 0: {edges.size(dim=0)}, dimension 1: {edges.size(dim=1)}')

permuted_edges = prepare_input_data(edges)

print(f'{permuted_edges.size()}, dimension 0: {permuted_edges.size(dim=0)}, dimension 1: {permuted_edges.size(dim=1)}')

model = GCN(num_node_features=dataset.num_node_features, num_classes= dataset.num_classes, hidden_channels=1)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

def train():
    model.train()
    optimizer.zero_grad()
    #for graph in trainset:
        #output = model(graph[0][0], graph[0][1]) #graph[0][0] is node feature tensor, graph[0][1] is edge tensor
        #loss_train = criterion(output, graph[1]) #graph[1] is label
        #compute accuracy
        #loss_train.backward() #backward propagation to update weights? do this for entire batch for performance i think
        #optimizer.step()
    output, nb_classes = model(nodes, permuted_edges)
    loss_train = criterion(output, trainset[0][1])
    loss_train.backwards()
    optimizer.step()

def test():
    model.eval()
    for graph in testset:
        output = model(graph[0][0], graph[0][1])
        loss = criterion(output, graph[1])
        #compute accuracy

for epoch in range(1,5):
    train()