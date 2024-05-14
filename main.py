import os
from ASTToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet, URI
from EcoreToMatrixConverter import EcoreToMatrixConverter
from CustomDataset import RepositoryDataset
from GCN import GCN

# repository_directory = '/mnt/volume1/mlexpmining/cloned_repos/'
# output_directory = '/mnt/volume1/mlexpmining/ecore_graphs/'
#repository_directory = '../unit_testing'
repository_directory = '../test_repository' #input repositories
output_directory = '../test_tool' #output for the entire tool pipeline

if __name__ == '__main__':
    #create output directory
    if not os.path.exists(output_directory): 
        os.makedirs(output_directory)
    #create sub folders for converter output and dataset
    if not os.path.exists(f'{output_directory}/xmi_files'):
        os.makedirs(f'{output_directory}/xmi_files')
    if not os.path.exists(f'{output_directory}/csv_files'):
        os.makedirs(f'{output_directory}/csv_files')   
    if not os.path.exists(f'{output_directory}/labeled_repositories'):
        os.makedirs(f'{output_directory}/labeled_repositories') 
    repositories = os.listdir(repository_directory)
    skip_counter = 0
    resource_set = ResourceSet()
    for i,repository in enumerate(repositories):
        print(f'Progress: {i}/{len(repositories)}')
        current_directory = os.path.join(repository_directory, repository)
        print(current_directory)
        if os.path.isdir(current_directory):
            try:
                project_graph = ProjectEcoreGraph(current_directory, resource_set)
                #resource to serialize the metamodels
                resource = resource_set.create_resource(URI(f'{output_directory}/xmi_files/{repository}.xmi'), use_uuid=True)
                resource.append(project_graph.get_graph())
                resource.save()
            except Exception as e:
                print(e)
                print(f'Problem with repository {repository}. Skipping.')
                skip_counter += 1
        else:
            skip_counter += 1

    print('----------------------------------------------')
    print(f'Skipped {skip_counter} of {len(repositories)}.')

    print('---convert ecore graphs to matrix structure---')
    #load xmi instance
    skip_xmi = 0
    list_xmi_files = os.listdir(f'{output_directory}/xmi_files') #get output from above
    rset = ResourceSet()
    resource = rset.get_resource(URI('Basic.ecore'))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root

    for x, xmi_file in enumerate(list_xmi_files):
        print(f'Progress: {x}/{len(list_xmi_files)}')
        current_xmi_file = os.path.join(f'{output_directory}/xmi_files', xmi_file)
        print(current_xmi_file)
        resource = rset.get_resource(URI(f'{output_directory}/xmi_files/{xmi_file}'))
        try:
            EcoreToMatrixConverter(resource, f'{output_directory}/csv_files')
        except Exception as e:
            print(e)
            print(f'Problem with xmi file {xmi_file}. Skipping')
            skip_xmi += 1

    print('----------------------------------------------')
    print(f'Skipped {skip_xmi} of {len(list_xmi_files)}')
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
