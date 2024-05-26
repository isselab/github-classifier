import os
from pyecore.resources import ResourceSet, URI
from ASTToEcoreConverter import ProjectEcoreGraph
from EcoreToMatrixConverter import EcoreToMatrixConverter
import pandas as pd

'''in this file are the pipeline components put into reusable functions'''

def create_output_folders(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    # create sub folders for converter output and dataset
    if not os.path.exists(f'{directory}/xmi_files'):
        os.makedirs(f'{directory}/xmi_files')
    if not os.path.exists(f'{directory}/csv_files'):
        os.makedirs(f'{directory}/csv_files')
    if not os.path.exists(f'{directory}/labeled_repositories'):
        os.makedirs(f'{directory}/labeled_repositories')


def download_repositories(repository_directory, repository_list):
    working_directory = os.getcwd()

    # load labeled repository from excel/ods file
    # requirements for format: no empty rows in between and header name html_url
    resource = pd.read_excel(repository_list)

    # create directory for cloning if it does not exist and set it as current working directory
    if not os.path.exists(repository_directory):
        os.makedirs(repository_directory)
    os.chdir(repository_directory)

    # retrieve urls and clone repositories
    for row in resource.iterrows():
        object = row[1]
        url = object.get('html_url')
        os.system(f'git clone {url}')

    # change working directory back to github-classifier, otherwise cannot load resources from there
    os.chdir(working_directory)


def create_ecore_graphs(repository_directory, output_directory):
    repositories = os.listdir(repository_directory)
    skip_counter = 0
    resource_set = ResourceSet()
    for i, repository in enumerate(repositories):
        print(f'Progress: {i}/{len(repositories)}')
        current_directory = os.path.join(repository_directory, repository)
        print(current_directory)
        if os.path.isdir(current_directory):
            try:
                ProjectEcoreGraph(current_directory, resource_set, output_directory, repository)
            except Exception as e:
                print(e)
                if 'inconsistent use of tabs and spaces in indentation' in str(e):
                    # format repository files using autopep8
                    python_files = [os.path.join(root, file) for root, _, files in os.walk(
                                    current_directory) for file in files if file.endswith('.py')]
                    for file_path in python_files:
                        os.system(f'autopep8 --in-place {file_path}')
                    try:
                        ProjectEcoreGraph(current_directory, resource_set, output_directory, repository)
                    except Exception as e:
                        print(e)
                        print(f'Problem with repository {repository}. Skipping.')
                        skip_counter += 1
                else:
                    print(f'Problem with repository {repository}. Skipping.')
                    skip_counter += 1
        else:
            skip_counter += 1
    print('----------------------------------------------')
    print(f'Skipped {skip_counter} of {len(repositories)}.')


def create_matrix_structure(output_directory):
    skip_xmi = 0
    list_xmi_files = os.listdir(f'{output_directory}/xmi_files')
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


def prepare_dataset(repository_directory, output_directory, repository_list=None):
    # clone repositories for the dataset
    if repository_list is not None:
        download_repositories(repository_directory, repository_list)

    # create output directory
    create_output_folders(output_directory)

    print('--convert repositories into ecore metamodels--')
    # convert repositories into ecore metamodels
    create_ecore_graphs(repository_directory, output_directory)

    print('---convert ecore graphs to matrix structure---')
    # load xmi instance and convert them to a matrix structure for the gcn
    create_matrix_structure(output_directory)
