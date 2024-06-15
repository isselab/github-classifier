import os
import shutil
import pandas as pd

labels = '../labeled_repos_first100.xlsx'
dest_directory = 'D:/labeled_repos_first100/csv_files/'
src_directory = 'D:/data_output/csv_files/'

resource = pd.read_excel(labels)
graph_dir = os.listdir(src_directory)

graph_names = []
for row in resource.iterrows():
    object = row[1]
    url = object.get('html_url') #column header containing repository url
    repo_name = url.split('/')[-1] 
    graph_names.append(repo_name)

os.chdir(src_directory)
for n, name in enumerate(graph_names):
    for g, graph in enumerate(graph_dir):
        if f'{name}_nodefeatures' in graph or f'{name}_A' in graph: 
            shutil.copy2(graph, dest_directory)



