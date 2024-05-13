from torch.utils.data import DataLoader, random_split
from CustomDataset import RepositoryDataset
from GCN import GCN
import torch
import torch.nn.functional as F

matrix_files = '../csv_files' #folder with csv_files

print("---convert dataset labels for training---")

#labeled repositories should have column headers 'Repository Names' and 'Repository Labels', and no empty lines in the columns
labels = '../test_repositories.ods' #input: labeled repositories for the dataset
RepositoryDataset.convert_labeled_graphs(labels, matrix_files)

print("--------------load dataset---------------")

try:
    dataset = RepositoryDataset(matrix_files)

except Exception as e:
        print(e)
        print("There is a problem with the dataset.") #maybe dataset cant be loaded?

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
print("Size of test dataset: ")
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
    #print(f"Train accuracy: {train_accuracy}, Test accuracy: {test_accuracy}, epoch: {epoch}")
    print("Test..?")
    