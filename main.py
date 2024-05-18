from CustomDataset import RepositoryDataset
from GCN import GCN
from PipelineUtils import prepare_dataset

# repository_directory = '/mnt/volume1/mlexpmining/cloned_repos/'
# output_directory = '/mnt/volume1/mlexpmining/ecore_graphs/'
#repository_directory = '../unit_testing'
#repository_directory = '../test_repository' #input repositories
#output_directory = '../test_tool' #output for the entire tool pipeline
repository_directory = 'D:/dataset_repos'
output_directory = 'D:/tool_output'

if __name__ == '__main__':

   # try:
        #create the graph dataset of the repositories
        #prepare_dataset(repository_directory, output_directory)
    #except Exception as e:
        #print(e)
       # print('There is a problem with the input directory.')

    print('----------------load dataset------------------')
    try:
        dataset = RepositoryDataset(f'{output_directory}/csv_files')
        print('Dataset size: ')
        print(dataset.__len__())
        print('Number of classes: ')
        print(dataset.num_classes)
        #model = GCN(dataset, hidden_channels=8)
    except Exception as e:
        print(e)
        print('The dataset cannot be loaded.')
