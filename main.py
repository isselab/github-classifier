import os
from ASTToEcore import ProjectEcoreGraph
from pyecore.resources import ResourceSet, URI

repository_directory = '/mnt/volume1/mlexpmining/systems_dataset/'
output_directory = '/mnt/volume1/mlexpmining/systems_ecore/'

if __name__ == '__main__':
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    repositories = os.listdir(repository_directory)
    skip_counter = 0
    for i,repository in enumerate(repositories):
        print(f"Progress: {i}/{len(repositories)}")
        current_directory = os.path.join(repository_directory, repository)
        print(current_directory)
        if os.path.isdir(current_directory):
            try:
                project_graph = ProjectEcoreGraph(current_directory)

                resource_set = ResourceSet()
                resource = resource_set.create_resource(URI(f"{output_directory}/{repository}.xmi"))
                resource.append(project_graph.get_graph())
                resource.save()
            except:
                print(f"Problem with repository {repository}. Skipping.")
                skip_counter += 1
        else:
            skip_counter += 1
            # repositories.remove(repository)
    print("------------------------------------")
    print(f"Skipped {skip_counter} of {len(repositories)}.")
