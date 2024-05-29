from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split
from GCN import GCN
import torch
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

#for graph in testset:
    #print(graph[1]) #these are the label tensors
    #print(len(graph[0][0]))

#print(trainset[0][1]) #this is a label --> label of first graph of testset?!
#print(trainset[0][0][0]) #this is a node feature tensor --> of the first graph in the testset
#print(trainset[0][0][1])

'''i need to implement shuffling and iterating in batches over training set??'''
nodes = trainset[0][0][0]
edges = trainset[0][0][1]
print(f'{nodes.size()}, dimension 0: {nodes.size(dim=0)}, dimension 1: {nodes.size(dim=1)}')
print(f'{edges.size()}, dimension 0: {edges.size(dim=0)}, dimension 1: {edges.size(dim=1)}')

'''tensors connected, gradient propagated to the cloned tensor also propagate to the original tensor, 
use detach() if not wanted'''
#unsq_nodes = torch.unsqueeze(nodes, 0)
#unsq_edges = torch.unsqueeze(edges, 0)
#perm_edges = edges.permute(1, 0)
#perm_nodes = nodes.permute(1, 0)
#node_pad = nodes.clone()
#padding = len(edges)-len(nodes)
#node_pad = torch.zeros((padding, 1))
#padded_node_features = torch.nn.functional.pad(nodes, node_pad, mode='constant', value=int) #node_pad must be tupel of ints, not tensor
#padded_node_features = torch.cat((nodes, node_pad), 1) #concatenate in dimension 0
#print(padded_node_features)
#N = len(nodes)
#sliced_nodes = nodes[:N, 0]
#print(sliced_nodes)
m_edges = torch.movedim(edges, 1, 0)
print(m_edges)
#slice_edges = edges[:N, 0]
print(f'{nodes.size()}, dimension 0: {nodes.size(dim=0)}, dimension 1: {nodes.size(dim=1)}')
print(f'{m_edges.size()}, dimension 0: {m_edges.size(dim=0)},dimension 1: {m_edges.size(dim=1)}')

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
    output, nb_classes = model(nodes, m_edges)
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