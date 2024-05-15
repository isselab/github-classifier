from CustomDataset import RepositoryDataset
from GCN import GCN
from PipelineUtils import create_output_folders, create_ecore_graphs, create_matrix_structure

# repository_directory = '/mnt/volume1/mlexpmining/cloned_repos/'
# output_directory = '/mnt/volume1/mlexpmining/ecore_graphs/'
#repository_directory = '../unit_testing'
repository_directory = '../test_repository' #input repositories
output_directory = '../test_tool' #output for the entire tool pipeline

if __name__ == '__main__':

    #create output directory
    create_output_folders(output_directory)
    
    print('--convert repositories into ecore metamodels--')
    #convert repositories into ecore metamodels
    create_ecore_graphs(repository_directory, output_directory)

    print('---convert ecore graphs to matrix structure---')
    #load xmi instance and convert them to a matrix structure for the gcn
    create_matrix_structure(output_directory)

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
