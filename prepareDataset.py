from Pipeline import prepare_dataset

'''this file is for preparing the dataset you want to train the tool with

    prepare_dataset: repository list is optional parameter, if you want to download the repositories automatically;
    output_directory is required when more than one repository is going to be converted,
    if there is only one repository the output of the converter is saved in return variables and can be
    piped into the gcn as input without needing to load the data from files'''

repository_directory = 'D:/new_15' #GitHub repositories
output_directory = 'D:/new_15_output'
repository_list = 'data/new_15.xlsx'

if __name__ == '__main__':
    
    #create the graph dataset of the repositories
    try:
        nodes, edges, edge_attributes = prepare_dataset(repository_directory, output_directory)
    except Exception as e:
        print(e)