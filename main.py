from CustomDataset import RepositoryDataset
from Pipeline import prepare_dataset
import torch

'''prepare_dataset: repository list is optional parameter, if you want to download the repositories automatically;
    output_directory is required when more than one repository is going to be converted,
    if there is only one repository the output of the converter is saved in return variables and can be
    piped into the gcn as input without needing to load the data from files

    RepositoryDataset: repository list is needed when using the dataset for training, the labels for
    the graphs are loaded from that file, otherwise the graphs are loaded without labels'''

repository_list = '../dataset_labeled.xlsx'
repository_directory = 'D:/dataset_repos'
output_directory = 'D:/data_output'
path_to_model = 'graph_classification_model.pt'

if __name__ == '__main__':

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    try:
        # create the graph dataset of the repositories
        nodes, edges = prepare_dataset(repository_directory, output_directory)
        #if nodes is not None and edges is not None:
            #load trained graph convolutional network model
            #model = torch.load(path_to_model)
           # model.eval() #in pytorch doc!!
           # print(model)
           # print(nodes, nodes.size())
           # print(edges, edges.size())
            #if device == 'cuda':
               # nodes.to(device)
                #edges.to(device)
            #output = model(nodes, edges) #complains about missing batch?
            #print(output)
    except Exception as e:
        print(e)

    print('----------------load dataset------------------')
    try:
        dataset = RepositoryDataset(f'{output_directory}/csv_files')
        print('Dataset size: ')
        print(dataset.__len__())
        print('Number of classes: ')
        print(dataset.num_classes)
       # model = torch.load(path_to_model)
        #model.eval()
        #for graph in dataset:
            #if device == 'cuda':
                #graph.x.to(device)
                #graph.edge_index.to(device)
            #output = model(graph.x, graph.edge_index) #how to save output? --> necessary to save it?
            #print(output) #maybe new func to get graph name?
    except Exception as e:
        print(e)
        print('The dataset cannot be loaded.')

