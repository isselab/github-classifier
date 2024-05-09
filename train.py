from torch.utils.data import DataLoader, random_split
from CustomDataset import RepositoryDataset


print("---convert dataset labels for training---")
#currently done manually by running LabelDatasetGraphs.py
print("--------------load dataset---------------")
try:
        matrix_files = '../csv_files'
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
        print(dataset.num_classes)
    #print(dataset[1][0])#this is only tupel node feature and edges
    #print(dataset[1][0][0]) #this is node feature tensor
    #model = GCN(dataset, hidden_channels=8)
        #print(dataset.graph_names)
        #print(dataset.gr_name)
        
except Exception as e:
        print(e)
        print("There is a problem with the dataset.") #maybe dataset cant be loaded?