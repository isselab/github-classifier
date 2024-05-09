import os
from ASTToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet, URI
from EcoreToMatrixConverter import EcoreToMatrixConverter
from CustomDataset import RepositoryDataset
from torch.utils.data import DataLoader, random_split
from GCN import GCN

# repository_directory = '/mnt/volume1/mlexpmining/cloned_repos/'
# output_directory = '/mnt/volume1/mlexpmining/ecore_graphs/'
#repository_directory = '../unit_testing'
repository_directory = '../test_repository' #input repositories
output_directory = '../test_tool' #output of the entire tool pipeline

if __name__ == '__main__':
    if not os.path.exists(output_directory): 
        os.makedirs(output_directory)
    repositories = os.listdir(repository_directory)
    skip_counter = 0
    resource_set = ResourceSet()
    #for output of first converter
    ecore_files = '../ecore_test'
    if not os.path.exists(ecore_files):
        os.makedirs(ecore_files)
    for i,repository in enumerate(repositories):
        print(f"Progress: {i}/{len(repositories)}")
        current_directory = os.path.join(repository_directory, repository)
        print(current_directory)
        if os.path.isdir(current_directory):
            try:
                project_graph = ProjectEcoreGraph(current_directory, resource_set)
                #resource to serialize the metamodels
                resource = resource_set.create_resource(URI(f"{ecore_files}/{repository}.xmi"), use_uuid=True)
                resource.append(project_graph.get_graph())
                resource.save()
            except Exception as e:
                print(e)
                print(f"Problem with repository {repository}. Skipping.")
                skip_counter += 1
        else:
            skip_counter += 1

    print("------------------------------------")
    print(f"Skipped {skip_counter} of {len(repositories)}.")

    print("---------convert ecore graphs to matrix structure--------------")
    #load xmi instance
    skip_xmi = 0
    list_xmi_files = os.listdir(ecore_files) #get output from above
    #for output of second converter
    matrix_files = '../csv_files'
    if not os.path.exists(matrix_files):
        os.makedirs(matrix_files)
    rset = ResourceSet()
    resource = rset.get_resource(URI('Basic.ecore'))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root

    for x, xmi_file in enumerate(list_xmi_files):
        print(f"Progress: {x}/{len(list_xmi_files)}")
        current_xmi_file = os.path.join(ecore_files, xmi_file)
        print(current_xmi_file)
        resource = rset.get_resource(URI(f"{ecore_files}/{xmi_file}"))
        try:
            project_gcn_input = EcoreToMatrixConverter(resource)
            output_name = project_gcn_input.get_graph_name()
            output_node_matrix = project_gcn_input.get_encoded_node_matrix()
            output_adjacency_list = project_gcn_input.get_adjacency_list()

            #save matrices in two csv files
            new_resource_nodes = open(f"{matrix_files}/{output_name}_nodes.csv", "w+") 
            new_resource_edges = open(f"{matrix_files}/{output_name}_A.csv", "w+")

            for node in output_node_matrix:
                new_resource_nodes.write("%s" % node)
                new_resource_nodes.write("\n") #write next slice (node) in new line

            for edge in output_adjacency_list: #edge is array with two entries [node_id, node_id]
                edge_counter = 1
                for item in edge:
                    if edge_counter<len(edge):
                        new_resource_edges.write("%s, " % item)
                        edge_counter += 1
                    else:
                        new_resource_edges.write("%s" % item)
                new_resource_edges.write("\n")
            
            new_resource_nodes.close()
            new_resource_edges.close()
            
        except Exception as e:
            print(e)
            print(f"Problem with xmi file {xmi_file}. Skipping")
            skip_xmi += 1

    print("-----------------------------------")
    print(f"Skipped {skip_xmi} of {len(list_xmi_files)}")
    print("---------------load dataset-----------------")
    dataset = RepositoryDataset(matrix_files)
    print("Dataset size: ")
    print(dataset.__len__())
    #print(dataset[0])
    #split into train and testset, this is for training the tool, not using finished tool
    trainset, testset = random_split(dataset, [0.5, 0.5])
    loader = DataLoader(trainset, shuffle=True, batch_size=1)
    #print(loader)
    print(dataset.num_classes)
    #print(dataset[1][0])#this is only tupel node feature and edges
    #print(dataset[1][0][0]) #this is node feature tensor
    #model = GCN(dataset, hidden_channels=8)
    print(dataset.graph_names)
