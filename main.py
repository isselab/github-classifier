from CustomDataset import RepositoryDataset
from Pipeline import prepare_dataset
import torch

'''prepare_dataset: repository list is optional parameter, if you want to download the repositories automatically;
    output_directory is required when more than one repository is going to be converted,
    if there is only one repository the output of the converter is saved in return variables and can be
    piped into the gcn as input without needing to load the data from files

    RepositoryDataset: repository list is needed when using the dataset for training, the labels for
    the graphs are loaded from that file, otherwise the graphs are loaded without labels
    
    if you want to train the gcn, please use train.py, this file is for using the trained tool'''

#repository_list = '../labeled_dataset_repos.xlsx'
#repository_directory = 'D:/labeled_dataset_repos'
#output_directory = 'D:/labeled_repos_output'
repository_list = 'data/new_15.xlsx'
repository_directory = 'D:/new_15' #path to directory containing the repositories you want to classify
output_directory = 'D:/new_15_output'
path_to_model = 'graph_classification_model.pt' #trained classification model

if __name__ == '__main__':
    
    #check if gpu is available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    #create the graph dataset of the repositories
    try:
        nodes, edges, edge_attributes = prepare_dataset(repository_directory, output_directory)
    except Exception as e:
        print(e)
    
    #load trained graph convolutional network model
    print('---load GCN model---')
    model = torch.load(path_to_model)
    model.eval()
    if device == 'cuda':
        model = model.to(device)
    
    #classify only one repository
    if nodes is not None and edges is not None and edge_attributes is not None:
            
            if device == 'cuda':
                nodes = nodes.to(device)
                edges = edges.to(device)
                edge_attributes = edge_attributes.to(device)

            output = model(nodes, edges, edge_attributes)
            output = output.cpu().detach().numpy()
            output = (output > 0.5) #threshold for when label is considered predicted, model is trained with threshold 0.5!
            print('Labels [Application, Framework, Library, Plugin]:')
            print(f'Prediction: {output}')
    
    #classify multiple repositories with custom dataset
    if nodes is None and edges is None and edge_attributes is None:
        print('----------------load dataset------------------')
        try:
            #load dataset
            dataset = RepositoryDataset(f'{output_directory}/csv_files')
            print('Dataset size: ')
            print(dataset.__len__())
            print('Number of classes: ')
            print(dataset.num_classes)
        except Exception as e:
            print(e)

        for i, item in enumerate(dataset.graph_names):
            graph = dataset.__getitem__(i)
            print(dataset.graph_names[i])
            if device == 'cuda':
                graph.x = graph.x.to(device)
                graph.edge_index = graph.edge_index.to(device)
                graph.edge_attr = graph.edge_attr.to(device)
            output = model(graph.x, graph.edge_index, graph.edge_attr)
            output = output.cpu().detach().numpy()
            output = (output > 0.5) #threshold for when label is considered predicted, model is trained with threshold 0.5!
            print('Labels [Application, Framework, Library, Plugin]:')
            print(f'Prediction: {output}')
