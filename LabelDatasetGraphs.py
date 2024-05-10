import pandas as pd
from DefinedGraphClasses import graph_types   
from LabelEncoder import convert_labels

class LabelDatasetGraphs:
    def __init__(self, labels, output_graph_labels):
        #load labeled repository from excel/ods file
        resource = pd.read_excel(labels) #requirements for format: no empty rows in between and header names for columns

        new_resource_nodes = open(f"{output_graph_labels}", "w+")
        graph_labels = []
        graph_names = []

        #iterate over loaded file and retrieve labels
        for row in resource.iterrows():
            object = row[1]
            repo = object.get('Repository Label') 
            graph_labels.append(repo)
            name = row[1]
            repo_name = name.get('Repository Name')
            graph_names.append(repo_name)

        #encode labels numerically
        encoded_nodes = convert_labels(graph_types, graph_labels)
        file = zip(graph_names, encoded_nodes)

        #write encoded labels into a file for the dataset
        for item in list(file):
            name = item[0]
            new_resource_nodes.write("%s, " % name)
            label = item[1]
            new_resource_nodes.write("%s" % label)
            new_resource_nodes.write("\n")
        new_resource_nodes.close()