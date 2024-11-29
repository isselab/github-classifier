from Pipeline import prepare_dataset
from settings import CONFIG

'''this file is for preparing the dataset you want to train the tool with

    prepare_dataset: repository list is optional parameter, if you want to download the repositories automatically;
    output_directory is required when more than one repository is going to be converted,
    if there is only one repository the output of the converter is saved in return variables and can be
    piped into the gcn as input without needing to load the data from files'''

# GitHub repositories
repository_directory = CONFIG['dataset_preparation']['repository_directory']
output_directory = CONFIG['dataset_preparation']['output_directory']
repository_list = CONFIG['dataset_preparation']['repository_list_file']
download_from_repository_list = CONFIG['dataset_preparation']['download_from_repository_list']

if __name__ == '__main__':

    # create the graph dataset of the repositories
    try:
        if download_from_repository_list:
            nodes, edges, edge_attributes = prepare_dataset(
                repository_directory, output_directory, repository_list)
        else:
            nodes, edges, edge_attributes = prepare_dataset(
                repository_directory, output_directory)
    except Exception as e:
        print(e)
        exit('unable to create graph dataset of the repositories')
