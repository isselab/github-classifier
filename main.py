from CustomDataset import RepositoryDataset
from GCN import GCN
from PipelineUtils import prepare_dataset, create_matrix_structure
import traceback
import inspect

# repository_directory = '/mnt/volume1/mlexpmining/cloned_repos/'
# output_directory = '/mnt/volume1/mlexpmining/ecore_graphs/'

#repository_directory = 'D:/repo_no_compile'
#output_directory = 'D:/nocompile_output'

repository_directory = 'D:/dataset_repos'
output_directory = 'D:/tool_output'

#repository_directory = 'D:/str_issue'
#output_directory = 'D:/str_output'

#repository_directory = 'test/unit_tests'
#output_directory = '../output_tests'

if __name__ == '__main__':

    try:
        #create the graph dataset of the repositories
        prepare_dataset(repository_directory, output_directory)
        #create_matrix_structure(output_directory)
    except Exception as e:
        print(e)
        #print(type(e).__name__)
       # print(traceback.extract_tb()[-1])
        #print(inspect.trace()[-1][3])
        print('There is a problem with the input directory.')

    print('----------------load dataset------------------')
    try:
        dataset = RepositoryDataset(f'{output_directory}/csv_files')
        print('Dataset size: ')
        print(dataset.__len__())
        print('Number of classes: ')
        print(dataset.num_classes)
        #print(dataset.__getitem__(1)) #only works with sample pairs (graph, label)
        #model = GCN(dataset, hidden_channels=8)
    except Exception as e:
        print(e)
        print('The dataset cannot be loaded.')
