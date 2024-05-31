from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split
from torch_geometric.loader import DataLoader
from torch_geometric.data import Data
from GCN import GCN
import torch
from GCNUtils import prepare_input_data, normalize_matrix
#import torch.nn.functional as F

'''do not forget to save trained model in the end!!!'''

#repository_directory = 'D:/dataset_repos'  # input repositories
#output_directory = 'D:/output'  
output_directory = 'D:/tool_output'
labels = '../random_sample_icse_CO.xls' # labeled repositories for the training dataset

batch_size = 1
hidden_channels = 16

# create the graph dataset of the repositories
#try:
   # prepare_dataset(repository_directory, output_directory)
#except Exception as e:
   # print(e)

#print('---convert dataset labels for training---')
#try:
   # '''labeled repositories should have column headers 'html_url' and 'type', and no empty lines in the columns'''
   # RepositoryDataset.convert_labeled_graphs(labels, f'{output_directory}/csv_files')
#except Exception as e:
   # print(e)
   # print('There is a problem with the labeled dataset. Check format in excel file. Labeled repositories should have column headers html_url and type, and no empty lines in the columns!')

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files')
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')

# split into train and testset, this is for training the tool, not using finished tool
trainset, testset = random_split(dataset, [0.7, 0.3])
print(len(trainset), len(testset))

trainloader = DataLoader(trainset, batch_size=64, shuffle=True)
testloader = DataLoader(testset, batch_size=1, shuffle=False)
print(len(trainloader), len(testloader))

for step, data in enumerate(trainloader):
    print(f'Step {step + 1}:')
    print('=======')
   # print(f'Number of graphs in the current batch: {data.num_graphs}')
    print(data)
    print()
    print(len(data.x))

'''i need to implement shuffling and iterating in batches over training set??'''
#nodes = trainset[0][0][0]
#edges = trainset[0][0][1]
#print(f'{nodes.size()}, dimension 0: {nodes.size(dim=0)}, dimension 1: {nodes.size(dim=1)}')
#print(f'{edges.size()}, dimension 0: {edges.size(dim=0)}, dimension 1: {edges.size(dim=1)}')


'''wir kriege ich das in verbindung mit dem trainset? ---> in loop '''
#normalized_nodes, permuted_edges = prepare_input_data(nodes, edges) 


#print(f'{permuted_edges.size()}, dimension 0: {permuted_edges.size(dim=0)}, dimension 1: {permuted_edges.size(dim=1)}')

#print(permuted_edges)

#model = GCN(dataset.num_node_features, dataset.num_classes, hidden_channels, 6)

#optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

def train():
    model.train()
    optimizer.zero_grad()
    #for graph in trainset: 
       # output = model(graph[0][0], graph[0][1]) #graph[0][0] is node feature tensor, graph[0][1] is edge tensor
       # loss_train = criterion(output, graph[1]) #graph[1] is label
        #compute accuracy
        #loss_train.backward() #backward propagation to update weights? do this for entire batch for performance i think
       # optimizer.step()
    #for graph in trainset:
        #norm_nodes, perm_edges = prepare_input_data(graph[0][0], graph[0][1])
        #output = model(norm_nodes, perm_edges)
        #loss_train = criterion(output, graph[1])
        #compute accuracy
       # loss_train.backwards()
       # optimizer.step()
    output = model(normalized_nodes, permuted_edges)
    loss_train = criterion(output, trainset[0][1])
    loss_train.backwards()
    optimizer.step()

def test():
    model.eval()
    for graph in testset:
        output = model(graph[0][0], graph[0][1])
        loss = criterion(output, graph[1])
        #compute accuracy

#for epoch in range(1,5):
    #train()