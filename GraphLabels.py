import pandas as pd
from sklearn.preprocessing import LabelEncoder  
from defined_graph_classes import graph_types      

labels = '../test_repositories.ods' #labeled repositories for the dataset
output_graph_labels = '../csv_files/graph_labels.csv' #for output: label encoded graph labels for the dataset

#load labeled repository from excel/ods file
resource = pd.read_excel(labels)

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
label_encoder = LabelEncoder()
label_encoder.fit(graph_types)
encoded_nodes = label_encoder.transform(graph_labels)
file = zip(graph_names, encoded_nodes)

#write encoded labels into a file for the dataset
for item in list(file):
    print(item)
    name = item[0]
    new_resource_nodes.write("%s, " % name)
    label = item[1]
    new_resource_nodes.write("%s" % label)
    new_resource_nodes.write("\n")
new_resource_nodes.close()