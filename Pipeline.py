import os
from multiprocessing import Pool

import pandas as pd
from pyecore.resources import ResourceSet, URI

from AstToEcoreConverter import ProjectEcoreGraph
from DataformatUtils import convert_edge_dim, convert_list_to_floattensor, convert_list_to_longtensor, \
    convert_hashed_names_to_float
from EcoreToMatrixConverter import EcoreToMatrixConverter

'''in this file are the pipeline components put into reusable functions'''


def create_output_folders(directory):
    """
       Create a directory structure for output files.

       Ensures the main directory exists and creates subdirectories `xmi_files`
       and `csv_files` for organizing output files.

       Args:
           directory (str): Path to the main output directory.

       Raises:
           OSError: If the directory cannot be created.
       """
    if not os.path.exists(directory):
        os.makedirs(directory)
    # create sub folders for converter output and dataset
    if not os.path.exists(f'{directory}/xmi_files'):
        os.makedirs(f'{directory}/xmi_files')
    if not os.path.exists(f'{directory}/csv_files'):
        os.makedirs(f'{directory}/csv_files')


def download_repositories(repository_directory, repository_list):
    """
    Clone Git repositories listed in an Excel/ODS file into a specified directory.

    Args:
        repository_directory: Directory where repositories will be cloned.
        repository_list: Path to the Excel/ODS file containing repository URLs
                         with a header named 'html_url'.

    Raises:
        ValueError: If the 'html_url' header is missing in the input file.
        OSError: If the directory cannot be created or if cloning fails.
    """
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

    # change working directory back to github-classifier, otherwise cannot load resources from there and run tool
    os.chdir(working_directory)


def create_ecore_graphs(repository, write_in_file, output_directory=None):
    """
      Convert a repository into an Ecore graph.

      This function attempts to create an Ecore graph from the specified repository.
      If the repository contains inconsistent indentation (mixing tabs and spaces),
      it will automatically format the Python files using `autopep8` and retry the graph creation.

      Args:
          repository: The path to the repository to be converted into an Ecore graph.
          write_in_file: A boolean indicating whether to write the graph to a file.
          output_directory: Optional; the directory where the output file will be written.

      Returns:
          The generated Ecore graph if `write_in_file` is False; otherwise, returns None.

      Raises:
          Exception: Any exceptions raised during the graph creation process will be printed,
                      and the function will skip the problematic repository.
      """
    global ecore_graph
    skip_counter = 0
    resource_set = ResourceSet()
    if os.path.isdir(repository):
        try:
            ecore_graph = ProjectEcoreGraph(
                resource_set, repository, write_in_file, output_directory)
        except Exception as e:
            print(e)
            if 'inconsistent use of tabs and spaces in indentation' in str(e):
                # format repository files using autopep8
                python_files = [os.path.join(root, file) for root, _, files in os.walk(
                    repository) for file in files if file.endswith('.py')]
                for file_path in python_files:
                    os.system(f'autopep8 --in-place {file_path}')
                try:
                    ecore_graph = ProjectEcoreGraph(
                        resource_set, repository, write_in_file, output_directory)
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
    """
    Convert an Ecore graph or XMI file into three matrices: node features, adjacency list,
    and edge attributes.

    This function can either write the matrices to files or return them as output.
    If writing to files, it expects an XMI file to be provided; otherwise, it will
    use the provided Ecore graph.

    Args:
        write_in_file: A boolean indicating whether to write the matrices to files.
        xmi_file: Optional; the name of the XMI file to be processed.
        ecore_graph: Optional; the Ecore graph to be converted into matrices.
        output_directory: The directory where output files will be written.

    Returns:
        A tuple containing:
            - node features (if `write_in_file` is False)
            - adjacency list (if `write_in_file` is False)
            - edge attributes (if `write_in_file` is False)
        If `write_in_file` is True, returns (None, None, None).

    Raises:
        Exception: Any exceptions raised during the conversion process will be printed,
                    and the function will skip the problematic XMI file if applicable.
    """
    global node_features, adj_list, edge_attr
    skip_xmi = 0

    if write_in_file is True:
        rset = ResourceSet()
        resource = rset.get_resource(URI('Basic.ecore'))
        mm_root = resource.contents[0]
        rset.metamodel_registry[mm_root.nsURI] = mm_root

        resource = rset.get_resource(
            URI(f'{output_directory}/xmi_files/{xmi_file}'))
        try:
            EcoreToMatrixConverter(
                resource, write_in_file, f'{output_directory}/csv_files')
        except Exception as e:
            print(e)
            print(f'Problem with xmi file {xmi_file}. Skipping')
            skip_xmi += 1
    if write_in_file is False:
        try:
            matrix = EcoreToMatrixConverter(ecore_graph, write_in_file)
            node_features = matrix.get_node_features()
            adj_list = matrix.get_adjacency_list()
            edge_attr = matrix.get_encoded_edge_attributes()
        except Exception as e:
            print(e)
        return node_features, adj_list, edge_attr
    else:
        return None, None, None


def parallel_processing(func, repository_list):
    """
    Execute a function in parallel across a list of repositories.

    This function utilizes multiprocessing to apply the given function to each
    repository in the repository list concurrently.

    Args:
        func: The function to be executed in parallel. It should accept a
              variable number of arguments.
        repository_list: A list of tuples, where each tuple contains the arguments
                         to be passed to the function.

    Raises:
        Exception: Any exceptions raised during the execution of the function
                    will be propagated.
    """
    pool = Pool()  # number of processes is return value of os.cpu_count()
    pool.starmap(func, repository_list)


def prepare_dataset(repository_directory, output_directory=None, repository_list=None):
    """
        Prepare a dataset by processing repositories into type graphs and converting
        those graphs into matrices suitable for a Graph Convolutional Network (GCN).

        This function clones repositories, creates necessary output directories,
        and handles parallel processing to convert repositories and their
        corresponding type graphs into matrices.

        Args:
            repository_directory: The path to the directory containing the repositories.
            output_directory: The path where output files will be saved.
            Required if multiple repositories are processed.
            repository_list: A list of repositories to clone. If provided,
            these repositories will be downloaded.

        Returns:
            tuple: A tuple containing:
                - node_features: Features of the nodes in the graph.
                - adj_list: Adjacency list representation of the graph.
                - edge_attr: Attributes of the edges in the graph.

        Raises:
            Exception: If no repositories are found or if the output directory is missing
                        when processing multiple repositories.
        """
    global repo_multiprocess, ecore_graph
    node_features = None
    adj_list = None
    edge_attr = None

    # clone repositories for the dataset
    if repository_list is not None:
        download_repositories(repository_directory, repository_list)

    repositories = os.listdir(repository_directory)
    if len(repositories) == 1:
        write_in_file = False
    elif len(repositories) > 1:
        write_in_file = True
    else:
        raise Exception("No repositories found")

    # create output directory
    if write_in_file is True:
        try:
            create_output_folders(output_directory)
        except Exception as e:
            print(e)
            # exit program because of missing output directory
            exit('output directory is required!')
        # create pool for multiprocessing/parallelisation
        repo_multiprocess = []
        for repository in repositories:
            current_directory = os.path.join(repository_directory, repository)
            repo_multiprocess.append(
                (current_directory, write_in_file, output_directory))

    print('---convert repositories into type graphs---')
    # convert repositories into type graphs
    if write_in_file is True:
        parallel_processing(create_ecore_graphs, repo_multiprocess)
    else:
        single_directory = os.path.join(repository_directory, repositories[0])
        ecore_graph = create_ecore_graphs(single_directory, write_in_file)

    print('---convert type graphs into three matrices---')
    # load xmi instance and convert them to a matrix structure for the gcn
    if write_in_file is True:
        list_xmi_files = os.listdir(f'{output_directory}/xmi_files')
        xmi_multiprocess = []
        for xmi_file in list_xmi_files:
            xmi_multiprocess.append(
                (write_in_file, xmi_file, None, output_directory))
        parallel_processing(create_matrix_structure, xmi_multiprocess)
    else:
        node_features, adj_list, edge_attr = create_matrix_structure(
            write_in_file, None, ecore_graph)

    # if only one repository is converted for classification, adjust data format needed by the gcn
    if node_features is not None and adj_list is not None and edge_attr is not None:
        node_features = convert_hashed_names_to_float(node_features)
        adj_list = convert_list_to_longtensor(adj_list)
        adj_list = convert_edge_dim(adj_list)
        edge_attr = convert_list_to_floattensor(edge_attr)

    return node_features, adj_list, edge_attr
