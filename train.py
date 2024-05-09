from torch.utils.data import DataLoader, random_split
from CustomDataset import RepositoryDataset
from LabelDatasetGraphs import LabelDatasetGraphs
from GCN import GCN
import torch

print("---convert dataset labels for training---")

#labeled repositories should have column headers 'Repository Names' and 'Repository Labels', and no empty lines in the columns
labels = '../test_repositories.ods' #input: labeled repositories for the dataset
output_graph_labels = '../csv_files/graph_labels.csv' #for output
LabelDatasetGraphs(labels, output_graph_labels)

print("--------------load dataset---------------")

try:
    matrix_files = '../csv_files' #folder with csv_files
    dataset = RepositoryDataset(matrix_files)

    #split into train and testset, this is for training the tool, not using finished tool
    trainset, testset = random_split(dataset, [0.5, 0.5])

    #uses index to access (sample,label) pairs
    loader = DataLoader(trainset, shuffle=True, batch_size=1)

    #print(dataset[1][0])#this is only tupel node feature and edges
    #print(dataset[1][0][0]) #this is node feature tensor

    #graphs, graph_label = next(iter(loader)) #better than for loop

except Exception as e:
        print(e)
        print("There is a problem with the dataset.") #maybe dataset cant be loaded?

#model = GCN(dataset, hidden_channels=8)
#print(model)

#these parameters are set by us for training
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
criterion = torch.nn.CrossEntropyLoss()

def train(idx): #idx is graph from the batch, or should be?
    model.train()
    optimizer.zero_grad()
    out = model(loader[idx][0][0], loader[idx][0][1]) #(loader.x, loader.edge_index)
    loss = criterion()
    loss.backward()
    optimizer.step()
    return loss

def test(): #i dont know whats happening here, example from github load_data
    model.eval()
    output = model(features, adj)
    loss_test = F.nll_loss(output[idx_test], labels[idx_test])
    acc_test = accuracy(output[idx_test], labels[idx_test])
    print("Test set results:",
          "loss= {:.4f}".format(loss_test.item()),
          "accuracy= {:.4f}".format(acc_test.item()))
    
epoch_time = 200
#for epoch in epoch_time:
     #train(epoch) #this does not match func above with idx!!
    
#example
#def train():
   # model.train()
    #optimizer.zero_grad()
   # out = model(data.x, data.edge_index) 
   # loss = criterion(out[data.train_mask], data.y[data.train_mask])
   # loss.backward()
    #optimizer.step()
   # return loss

#def test():
    #model.eval()
    #output = model(features, adj)
    #loss_test = F.nll_loss(output[idx_test], labels[idx_test])
   # acc_test = accuracy(output[idx_test], labels[idx_test])
   # print("Test set results:",
         # "loss= {:.4f}".format(loss_test.item()),
          #"accuracy= {:.4f}".format(acc_test.item()))

#for test_graph, test_label in loader:
        #sample_edges = test_graph[1] #[0] is feature vector
        #sample_label = test_label[0]