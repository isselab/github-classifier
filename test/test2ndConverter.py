import os
from pyecore.resources import ResourceSet, URI
import pandas as pd
import numpy as np
from testUtils import count_packages

output_directory = 'D:/tool_output'

list_csv_files = os.listdir(f'{output_directory}/csv_files')
list_xmi_files = os.listdir(f'{output_directory}/xmi_files') #get output from above
rset = ResourceSet()
resource = rset.get_resource(URI('../Basic.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root

for x, xmi_file in enumerate(list_xmi_files):
        count_package = 0
        count_class = 0
        print(f'Progress: {x}/{len(list_xmi_files)}')
        current_xmi_file = os.path.join(f'{output_directory}/xmi_files', xmi_file)
        print(current_xmi_file)
        resource = rset.get_resource(URI(f'{output_directory}/xmi_files/{xmi_file}'))
        typegraph_root = resource.contents[0]

        #count number of packages
        for tpackage in typegraph_root.packages:
                count_package += 1
                if hasattr(tpackage, 'subpackages'):
                        count_package = count_packages(tpackage, count_package)
        print(count_package)

        #count number of classes
        for tclass in typegraph_root.classes:
                count_class += 1
                if hasattr(tclass, 'childClasses'): #cannot check this recursively without exceeding max number of recursion
                    for child in tclass.childClasses:
                        count_class += 1
        print(count_class)

        graph_name = typegraph_root.tName
        #load csv file
        node_features = pd.read_csv(f'{output_directory}/csv_files/{graph_name}_nodefeatures.csv', header=None) 
        node_array = np.array(node_features)
        edges = pd.read_csv(f'{output_directory}/csv_files/{graph_name}_A.csv', header=None) 
        edge_array = np.array(edges)
        count_pack = 0
        #count packages
        for obj in node_array:
               if obj == 6:
                    count_pack += 1
        
        if count_pack == count_package:
               print('Test passed')
