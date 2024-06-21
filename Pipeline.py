import os
from pyecore.resources import ResourceSet, URI
from AstToEcoreConverter import ProjectEcoreGraph
from EcoreToMatrixConverter import EcoreToMatrixConverter
import pandas as pd
from DataformatUtils import convert_edge_dim, convert_list_to_floattensor, convert_list_to_longtensor
from multiprocessing import Pool

'''in this file are the pipeline components put into reusable functions'''

def create_output_folders(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    #create sub folders for converter output and dataset
    if not os.path.exists(f'{directory}/xmi_files'):
        os.makedirs(f'{directory}/xmi_files')
    if not os.path.exists(f'{directory}/csv_files'):
        os.makedirs(f'{directory}/csv_files')

def download_repositories(repository_directory, repository_list):
    working_directory = os.getcwd()

    #load labeled repository from excel/ods file
    #requirements for format: no empty rows in between and header name html_url
    resource = pd.read_excel(repository_list)

    #create directory for cloning if it does not exist and set it as current working directory
    if not os.path.exists(repository_directory):
        os.makedirs(repository_directory)
    os.chdir(repository_directory)

    #retrieve urls and clone repositories
    for row in resource.iterrows():
        object = row[1]
        url = object.get('html_url')
        os.system(f'git clone {url}')

    #change working directory back to github-classifier, otherwise cannot load resources from there
    os.chdir(working_directory)
    
def create_ecore_graphs(repository, write_in_file, output_directory=None):
    skip_counter = 0
    resource_set = ResourceSet()
    if os.path.isdir(repository):
        try:
            ecore_graph = ProjectEcoreGraph(resource_set, repository, write_in_file, output_directory)
        except Exception as e:
            print(e)
            if 'inconsistent use of tabs and spaces in indentation' in str(e):
                #format repository files using autopep8
                python_files = [os.path.join(root, file) for root, _, files in os.walk(
                                    repository) for file in files if file.endswith('.py')]
                for file_path in python_files:
                        os.system(f'autopep8 --in-place {file_path}')
                try:
                    ecore_graph = ProjectEcoreGraph(resource_set, repository, write_in_file, output_directory)
                except Exception as e:
                    print(e)
                    print(f'Problem with repository {repository}. Skipping.')
                    skip_counter += 1
            else:
                print(f'Problem with repository {repository}. Skipping.')
                skip_counter += 1
    else:
        print(f'Problem with repository {repository}. Skipping.')
        skip_counter += 1
    if write_in_file is False:
        return ecore_graph.get_graph()
    else:
        return None

def create_matrix_structure(write_in_file, xmi_file=None, ecore_graph=None, output_directory=None):
    skip_xmi = 0
    
    if write_in_file is True:
        rset = ResourceSet()
        resource = rset.get_resource(URI('Basic.ecore'))
        mm_root = resource.contents[0]
        rset.metamodel_registry[mm_root.nsURI] = mm_root

        resource = rset.get_resource(URI(f'{output_directory}/xmi_files/{xmi_file}'))
        try:
            EcoreToMatrixConverter(resource, write_in_file, f'{output_directory}/csv_files')
        except Exception as e:
            print(e)
            print(f'Problem with xmi file {xmi_file}. Skipping')
            skip_xmi += 1
    if write_in_file is False:
        try:
            matrix = EcoreToMatrixConverter(ecore_graph, write_in_file)
            node_features = matrix.get_encoded_node_matrix() #adjust this get all node features instead!
            adj_list = matrix.get_adjacency_list()
        except Exception as e:
            print(e)
        return node_features, adj_list
    else:
        return None, None
    
def parallel_processing(func, repository_list):
    pool = Pool() #number of processes: return of os.cpu_count()
    pool.starmap(func, repository_list)
    
def prepare_dataset(repository_directory, output_directory=None, repository_list=None):
    node_features = None
    adj_list = None

    #clone repositories for the dataset
    if repository_list is not None:
        download_repositories(repository_directory, repository_list)
    
    repositories = os.listdir(repository_directory)
    if len(repositories) == 1:
        write_in_file = False
    if len(repositories) > 1:
        write_in_file = True

    #create output directory
    if write_in_file is True:
        create_output_folders(output_directory)
        #create pool for multiprocessing/parallelisation
        repo_multiprocess = []
        for repository in repositories:
            current_directory = os.path.join(repository_directory, repository)
            repo_multiprocess.append((current_directory, write_in_file, output_directory))

    print('--convert repositories into ecore metamodels--')
    #convert repositories into ecore metamodels
    if write_in_file is True:
        parallel_processing(create_ecore_graphs, repo_multiprocess)
    else:
        single_directory = os.path.join(repository_directory, repositories[0])
        ecore_graph = create_ecore_graphs(single_directory, write_in_file)
    
    print('---convert ecore graphs to matrix structure---')
    #load xmi instance and convert them to a matrix structure for the gcn
    if write_in_file is True:
        list_xmi_files = os.listdir(f'{output_directory}/xmi_files')
        xmi_multiprocess = []
        for xmi_file in list_xmi_files:
            xmi_multiprocess.append((write_in_file, xmi_file, None, output_directory))
        parallel_processing(create_matrix_structure, xmi_multiprocess)
    else:
        node_features, adj_list = create_matrix_structure(write_in_file, None, ecore_graph)

    if node_features is not None and adj_list is not None:
        node_features = convert_list_to_floattensor(node_features)
        adj_list = convert_list_to_longtensor(adj_list)
        adj_list = convert_edge_dim(adj_list)

    return node_features, adj_list
