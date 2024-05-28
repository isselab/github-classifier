from CustomDataset import RepositoryDataset
from GCN import GCN
from PipelineUtils import prepare_dataset, create_matrix_structure

repository_list = '../random_sample_icse_CO.xls'
repository_directory = 'D:/test_pipeline'
output_directory = 'D:/output_test'

if __name__ == '__main__':

    try:
        # create the graph dataset of the repositories
        '''repository list is optional parameter, if you want to download the repositories automatically
        output_directory is required when more than one repository is going to be converted,
        if there is only one repository the ouput of the converter is saved in return variables and can be
        piped into the gcn as input without needing to load the data from files'''
        nodes, edges = prepare_dataset(repository_directory, output_directory)
        #create_matrix_structure(output_directory)
        print(nodes)
        print(edges)
    except Exception as e:
        print(e)
        print('There is a problem with the input directory.')

    print('----------------load dataset------------------')
    try:
        dataset = RepositoryDataset(f'{output_directory}/csv_files')
        print('Dataset size: ')
        print(dataset.__len__())
        print('Number of classes: ')
        print(dataset.num_classes)
        # print(dataset.__getitem__(1)) #only works with sample pairs (graph, label), cannot load dataset without labels :( --> issue!!??
        # model = GCN(dataset, hidden_channels=8)
    except Exception as e:
        print(e)
       # print('The dataset cannot be loaded.')
