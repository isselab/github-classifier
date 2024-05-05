import pandas as pd
from sklearn.preprocessing import LabelEncoder        

labels = '../test_repositories.ods' #labeled repositories for the dataset
output_graph_labels = '../csv_files/graph_labels.csv' #for output: label encoded graph labels for the dataset

#load labeled repository from excel/ods file
resource = pd.read_excel(labels)
        
#define graph labels
graph_types = ['Application', 'Library', 'Framework', 'Experiment', 'Tutorial']

new_resource_nodes = open(f"{output_graph_labels}", "w+")
graph_labels = []

#iterate over loaded file and retrieve labels
for row in resource.iterrows():
    object = row[1]
    repo = object.get('Repository Label') 
    graph_labels.append(repo)

#encode labels numerically
label_encoder = LabelEncoder()
label_encoder.fit(graph_types)
encoded_nodes = label_encoder.transform(graph_labels)

#write encoded labels into a file for the dataset
for item in encoded_nodes:
    new_resource_nodes.write("%s" % item)
    new_resource_nodes.write("\n")
new_resource_nodes.close()