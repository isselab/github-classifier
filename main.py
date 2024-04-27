import os
from ASTToEcore import ProjectEcoreGraph
from pyecore.resources import ResourceSet, URI
from EcoreToMatrix import EcoreToMatrixConverter

# repository_directory = '/mnt/volume1/mlexpmining/cloned_repos/'
# output_directory = '/mnt/volume1/mlexpmining/ecore_graphs/'
#repository_directory = '../unit_testing'
repository_directory = '../test_repository'
output_directory = '../ecore_test'
xmi_file_directory = '../ecore_test' #i can now set this to ecore_test?!
gcn_input_directory = '../gcn_input'

if __name__ == '__main__':
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    repositories = os.listdir(repository_directory)
    skip_counter = 0
    resource_set = ResourceSet()
    for i,repository in enumerate(repositories):
        print(f"Progress: {i}/{len(repositories)}")
        current_directory = os.path.join(repository_directory, repository)
        print(current_directory)
        if os.path.isdir(current_directory):
            try:
                project_graph = ProjectEcoreGraph(current_directory, resource_set)
                #resource to serialize the metamodels
                resource = resource_set.create_resource(URI(f"{output_directory}/{repository}.xmi"), use_uuid=True)
                resource.append(project_graph.get_graph())
                resource.save()
            except Exception as e:
                print(e)
                print(f"Problem with repository {repository}. Skipping.")
                skip_counter += 1
        else:
            skip_counter += 1
            # repositories.remove(repository)
    print("------------------------------------")
    print(f"Skipped {skip_counter} of {len(repositories)}.")

    print("---------convert ecore graphs to matrix structure--------------")
    #load xmi instance
    skip_xmi = 0
    xmi_files = os.listdir(xmi_file_directory)
    if not os.path.exists(gcn_input_directory):
        os.makedirs(gcn_input_directory)
    rset = ResourceSet()
    resource = rset.get_resource(URI('Basic.ecore'))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root
    for x, xmi_file in enumerate(xmi_files):
        print(f"Progress: {x}/{len(xmi_files)}")
        current_xmi_file = os.path.join(xmi_file_directory, xmi_file)
        print(current_xmi_file)
        resource = rset.get_resource(URI(f"{xmi_file_directory}/{xmi_file}"))
        try:
            project_gcn_input = EcoreToMatrixConverter(resource)
            output_name = project_gcn_input.get_graph_name()
            output_node_matrix = project_gcn_input.get_node_matrix()
            output_adjacency_matrix = project_gcn_input.get_adjacency_matrix()

            #save matrices in two text files
            new_resource_nodes = open(f"{gcn_input_directory}/{output_name}_nxc.txt", "w+") 
            for node in output_node_matrix: #iterate over slices
                for item in node:
                    new_resource_nodes.write("%s " % item)
                new_resource_nodes.write("\n") #write next slice (node) in new line
            new_resource_nodes.close()
            new_resource_edges = open(f"{gcn_input_directory}/{output_name}_adjacency.txt", "w+")
            for edge in output_adjacency_matrix:
                for item in edge:
                    new_resource_edges.write("%s " % item)
                new_resource_edges.write("\n")
            new_resource_edges.close()
        except Exception as e:
            print(e)
            print(f"Problem with xmi file {xmi_file}. Skipping")
            skip_xmi += 1
    print("-----------------------------------")
    print(f"Skipped {skip_xmi} of {len(xmi_files)}")

