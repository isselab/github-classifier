from torch.utils.data import DataLoader, random_split
from CustomDataset import RepositoryDataset
from LabelDatasetGraphs import LabelDatasetGraphs

print("---convert dataset labels for training---")
#labeled repositories should have column headers 'Repository Names' and 'Repository Labels', and no empty lines in the columns
labels = '../test_repositories.ods' #input: labeled repositories for the dataset
output_graph_labels = '../csv_files/graph_labels.csv' #for output
LabelDatasetGraphs(labels, output_graph_labels)
print("--------------load dataset---------------")
try:
    matrix_files = '../csv_files' #folder with csv_files
    dataset = RepositoryDataset(matrix_files)
    print("Dataset size: ")
    print(dataset.__len__())
    #print(dataset[0])
    #split into train and testset, this is for training the tool, not using finished tool
    trainset, testset = random_split(dataset, [0.5, 0.5])
    #print(trainset)
        #uses index to access (sample,label) pairs
    loader = DataLoader(trainset, shuffle=True, batch_size=1)
    #print(loader)
    print("Number of classes: ")
    print(dataset.num_classes)
    #print(dataset[1][0])#this is only tupel node feature and edges
    #print(dataset[1][0][0]) #this is node feature tensor
    #model = GCN(dataset, hidden_channels=8)
        #print(dataset.graph_names)
        #print(dataset.gr_name)

except Exception as e:
        print(e)
        print("There is a problem with the dataset.") #maybe dataset cant be loaded?