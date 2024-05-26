from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
from torch.utils.data import random_split

repository_directory = 'D:/dataset_repos'  # input repositories
output_directory = 'D:/tool_output'  
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
trainset, testset = random_split(dataset, [0.7, 0.3])
print(len(trainset), len(testset))

for graph in testset:
    #print(graph[1]) #these are the label tensors
    print(len(graph[0][0]))

print(testset[0][1]) #this is a label --> label of first graph of testset?!
print(testset[0][0][0]) #this is a node feature tensor --> of the first graph in the testset

'''i need to implement shuffling and iterating in batches over training set??'''
