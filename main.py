from CustomDataset import RepositoryDataset
from PipelineUtils import prepare_dataset
import torch

'''repository list is optional parameter, if you want to download the repositories automatically;
    output_directory is required when more than one repository is going to be converted,
    if there is only one repository the output of the converter is saved in return variables and can be
    piped into the gcn as input without needing to load the data from files'''

repository_list = '../random_sample_icse_CO.xls'
repository_directory = 'D:/repos'
#repository_directory = 'D:/single'
output_directory = 'D:/pool_test'

if __name__ == '__main__':

    try:
        # create the graph dataset of the repositories
        nodes, edges = prepare_dataset(repository_directory, output_directory)
        if nodes is not None and edges is not None:
            #load trained graph convolutional network model
            model = torch.load('graph_classification_model.pt')
            print(model)
            print(nodes, nodes.size())
            print(edges, edges.size())
            output = model(nodes, edges, 1) #complains about missing batch
            print(output)
    except Exception as e:
        print(e)

    print('----------------load dataset------------------')
    try:
        dataset = RepositoryDataset(f'{output_directory}/csv_files')
        print('Dataset size: ')
        print(dataset.__len__())
        print('Number of classes: ')
        print(dataset.num_classes)
        model = torch.load('graph_classification_model.pt')
        for graph in dataset:
            output = model(graph.x, graph.edge_index, 1) #how to save output? --> necessary to save it?
            print(output) #maybe new func to get graph name?
    except Exception as e:
        print(e)
        print('The dataset cannot be loaded.')

