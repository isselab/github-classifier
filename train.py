from torch.utils.data import DataLoader, random_split
from CustomDataset import RepositoryDataset
from GCN import GCN
import torch
import torch.nn.functional as F
from PipelineUtils import create_output_folders, create_ecore_graphs, create_matrix_structure


repository_directory = '../test_repository' #input repositories
output_directory = '../test_tool' #output for the entire tool pipeline

labels = '../test_repositories.ods' #input: labeled repositories for the dataset

#create output directory
create_output_folders(output_directory)
    
print('--convert repositories into ecore metamodels--')
#convert repositories into ecore metamodels
create_ecore_graphs(repository_directory, output_directory)

print('---convert ecore graphs to matrix structure---')
#load xmi instance and convert them to a matrix structure for the gcn
create_matrix_structure(output_directory)

print('---convert dataset labels for training---')
try:
    #labeled repositories should have column headers 'Repository Names' and 'Repository Labels', and no empty lines in the columns
    RepositoryDataset.convert_labeled_graphs(labels, f'{output_directory}/csv_files')
except Exception as e:
    print(e)
    print('There is a problem with the labeled dataset. Check format in excel file. Labeled repositories should have column headers Repository Names and Repository Labels, and no empty lines in the columns!')

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files')
except Exception as e:
        print(e)
        print('Dataset cannot be loaded.')

#cant i put these funtions in gcn file to its class?
#.train and .eval functions switch on or off certain layers of the model for us when needed
def train(): 
    model.train() #tells model we are training
    #iterate in batches over the training dataset
    for graph, label in trainloader: 
        #perform single forward pass
        prediction = model(graph[0], graph[1]) #graph[0] is feature vector, graph[1] is edge_index
        #compute loss from prediction made by model and the actual label from the dataset
        loss = criterion(prediction, label) 
        loss.backward() #derive gradients
        optimizer.step() #update parameters based on gradients
        optimizer.zero_grad() #clear gradients

def test(loader):
    model.eval() #tells model we are evaluating
    #where to put no_grad? in articles always coupled with eval
    #torch.no_grad() #turns off parameters set in training for faster computation during inference
    acc_test = 0
    for graph, label in loader: 
        #check if output is only prediction, check what it looks like for access
        prediction = model(graph[0], graph[1]) #in example additionally batch is passed here? what batch
        #a lot of examples don't compute loss in test, some do
        if prediction == label: acc_test += 1 #count correctly predicted labels
    return acc_test/len(loader) 

#split into train and testset, this is for training the tool, not using finished tool
trainset, testset = random_split(dataset, [0.5, 0.5])

#uses index to access (sample,label) pairs
trainloader = DataLoader(trainset, shuffle=True, batch_size=1)
testloader = DataLoader(trainset, shuffle=False, batch_size=1)
    
#print(dataset[1][0])#this is only tupel node feature and edges
#print(dataset[1][0][0]) #this is node feature tensor, both of graph with index 1

for graph, label in trainloader:
    print(graph[1]) #print tensor with edges
print('Size of test dataset: ')
print(len(testloader))
#model = GCN(trainloader, hidden_channels=8)
#print(model)

#initialize functions for training
#optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = torch.nn.CrossEntropyLoss()

#train model
n_epochs = 10
for epoch in range(n_epochs):
    #train() #in examples training set is not passed as argument, just used inside func
    #train_accuracy = test(trainloader)
    #test_accuracy = test(testloader)
    #print results
    #print(f'Train accuracy: {train_accuracy}, Test accuracy: {test_accuracy}, epoch: {epoch}')
    print('Test..?')
    