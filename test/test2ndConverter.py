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
        count_meth = 0
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
        #print(count_package)

        #count number of classes
        for tclass in typegraph_root.classes:
                count_class += 1
                if hasattr(tclass, 'childClasses'): #cannot check this recursively without exceeding max number of recursion
                    for child in tclass.childClasses:
                        count_class += 1
                        #if hasattr(child, 'childClasses'):
                           # for kid in child.childClasses:
                               # count_class += 1
                               # if hasattr(kid, 'childClasses'):
                                    #print('there are more child classes')
        #print(count_class)

        for tmeth in typegraph_root.methods:
             count_meth += 1

        graph_name = typegraph_root.tName
        #load csv file
        node_features = pd.read_csv(f'{output_directory}/csv_files/{graph_name}_nodefeatures.csv', header=None) 
        node_array = np.array(node_features)
        edges = pd.read_csv(f'{output_directory}/csv_files/{graph_name}_A.csv', header=None) 
        edge_array = np.array(edges)
        count_pack = 0
        count_cl = 0
        count_methods = 0
        #count packages
        for obj in node_array:
            if obj == 6:
                count_pack += 1
            if obj == 1:
                count_cl += 1
            if obj == 2:
                 count_methods += 1
        print(count_cl)
        print(count_class)
        print(count_methods, count_meth)
        #compare xmi files with csv files
        if count_pack == count_package:
            print('Number of packages correct, test passed')
        else:
            print('Number of packages not correct, test failed')

        if count_cl == count_class: #more classes in typegraph than in csv file
            print('Number of classes correct, test passed')
        else:
            print('Number of classes not correct, test failed')

        if count_meth == count_methods:
            print('Number of methods correct, test passed')
        else:
            print('Number of methods not correct, test failed')
