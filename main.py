import os
from ASTToEcore import ProjectEcoreGraph
from pyecore.resources import ResourceSet, URI

repository_directory = ''
output_directory = 'output'

if __name__ == '__main__':
    repositories = os.listdir(repository_directory)
    skip_counter = 0
    for repository in repositories:
        if os.path.isdir(repository):
            try:
                project_graph = ProjectEcoreGraph(repository)

                resource_set = ResourceSet()
                resource = resource_set.create_resource(URI(f"{output_directory}/{repository.split('/')[-1]}.xmi"))
                resource.append(project_graph.get_graph())
                resource.save()
            except:
                print(f"Problem with repository {repository.split('/')[-1]}. Skipping.")
                skip_counter += 1
        else:
            repositories.remove(repository)
    print("------------------------------------")
    print(f"Skipped {skip_counter} of {len(repositories)}.")
