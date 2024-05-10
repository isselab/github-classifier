from torch.utils.data import DataLoader, random_split
from CustomDataset import RepositoryDataset
from LabelDatasetGraphs import LabelDatasetGraphs
from GCN import GCN
import torch
import torch.nn.functional as F

print("---convert dataset labels for training---")

#labeled repositories should have column headers 'Repository Names' and 'Repository Labels', and no empty lines in the columns
labels = '../test_repositories.ods' #input: labeled repositories for the dataset
output_graph_labels = '../csv_files/graph_labels.csv' #for output
LabelDatasetGraphs(labels, output_graph_labels)

print("--------------load dataset---------------")

try:
    matrix_files = '../csv_files' #folder with csv_files
    dataset = RepositoryDataset(matrix_files)

except Exception as e:
        print(e)
        print("There is a problem with the dataset.") #maybe dataset cant be loaded?


def train(): 
    model.train() 
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
    model.eval()

    for graph, label in loader: 
        prediction = model(graph[0], graph[1]) #in example additionally batch is passed here? what batch
        loss_test = F.nll_loss(prediction, label) #predict loss with predicted labels from trained model and defined labels of testset
        if prediction == label: acc_test += 1 #count correctly predicted labels
    #this func is not complete

#split into train and testset, this is for training the tool, not using finished tool
trainset, testset = random_split(dataset, [0.5, 0.5])

#uses index to access (sample,label) pairs
trainloader = DataLoader(trainset, shuffle=True, batch_size=1)
testloader = DataLoader(trainset, shuffle=False, batch_size=1)
    
#print(dataset[1][0])#this is only tupel node feature and edges
#print(dataset[1][0][0]) #this is node feature tensor, both of graph with index 1

for graph, label in trainloader:
    print(graph[1]) #print tensor with edges

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
    #print results...
    print("Test..?")
    