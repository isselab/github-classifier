import os
from pyecore.resources import ResourceSet, URI
import pandas as pd
import numpy as np
from testUtils import count_packages, Types, count_calls

'''This test checks for arbitrary repositories if the number of converted node types matches in the xmi and csv files,
meaning it tests whether all nodes were converted by counting the types.
Use the tool by running main.py to create the files first.'''

output_directory = 'D:/nocompile_output' #path to the folder containing the xmi and csv files

list_xmi_files = os.listdir(f'{output_directory}/xmi_files') 
rset = ResourceSet()
resource = rset.get_resource(URI('../Basic.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root

for x, xmi_file in enumerate(list_xmi_files):
        count_package = 0
        count_class = 0
        count_method = 0
        count_method_def = 0
        count_method_sig = 0
        count_call = 0
        count_parameter = 0
        count_module = 0

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

        #count number of classes
        '''has only one attribute childclasses checking recursively will result 
        in potential endless loop, without these child classes existing in the xmi file'''
        for tclass in typegraph_root.classes:
                count_class += 1
                if hasattr(tclass, 'childClasses'): 
                    for child in tclass.childClasses:
                        count_class += 1
                        if hasattr(child, 'defines'):
                            for tmeth_def in child.defines:
                                count_method_def += 1
                                if hasattr(tmeth_def, 'accessing'):
                                    count_call = count_calls(tmeth_def, count_call)
                if hasattr(tclass, 'defines'):
                    for meth_def in tclass.defines: #do i need to check the type here?
                        count_method_def += 1
                        #check the calls here
                        if hasattr(meth_def, 'accessing'):
                            count_call = count_calls(meth_def, count_call)

        for tmeth in typegraph_root.methods:
            count_method += 1
            for tsig in tmeth.signatures:
                count_method_sig += 1
                if hasattr(tsig, 'parameters'):
                    for p in tsig.parameters:
                        count_parameter += 1

        for tmod in typegraph_root.modules: #i think checking classes here is not necessary, are all part of typegraph.classes
            count_module += 1
            if hasattr(tmod, 'contains'):
                #check if contained object is a method definition
                for tobj in tmod.contains:
                    if tobj.eClass.name == Types.METHOD_DEFINITION.value:
                        count_method_def += 1
                        if hasattr(tobj, 'accessing'):
                            count_call = count_calls(tobj, count_call)

        graph_name = typegraph_root.tName

        #load csv file
        try:
            node_features = pd.read_csv(f'{output_directory}/csv_files/{graph_name}_nodefeatures.csv', header=None) 
            node_array = np.array(node_features)
            edges = pd.read_csv(f'{output_directory}/csv_files/{graph_name}_A.csv', header=None) 
            edge_array = np.array(edges)
        except Exception as e:
            print(e)

        count_pack = 0
        count_cl = 0
        count_meth = 0
        count_meth_def = 0
        count_meth_sig = 0
        count_ca = 0
        count_param = 0
        count_mod = 0

        try:
            #count node types
            for obj in node_array:
                if obj == 6:
                    count_pack += 1
                if obj == 1:
                    count_cl += 1
                if obj == 2:
                    count_meth += 1
                if obj == 3:
                    count_meth_def += 1
                if obj == 4:
                    count_meth_sig += 1
                if obj == 7:
                    count_param += 1
                if obj == 0:
                    count_ca += 1
                if obj == 5:
                    count_mod += 1
        except Exception as e:
            print(e)

        #compare xmi files with csv files
        if count_pack == count_package:
            print('Number of packages correct, test passed')
        else:
            print('Number of packages not correct, test failed')

        if count_cl == count_class: 
            print('Number of classes correct, test passed')
        else:
            print('Number of classes not correct, test failed')

        if count_meth == count_method:
            print('Number of methods correct, test passed')
        else:
            print('Number of methods not correct, test failed')

        if count_meth_def == count_method_def:
            print('Number of method definitions correct, test passed')
        else:
            print('Number of method definitions not correct, test failed')

        if count_meth_sig == count_method_sig:
            print('Number of method signatures correct, test passed')
        else:
            print('Number of method signatures not correct, test failed')

        if count_param == count_parameter:
            print('Number of parameters correct, test passed')
        else:
            print('Number of parameters not correct, test failed')

        if count_ca == count_call:
            print('Number of calls correct, test passed')
        else:
            print('Number of calls not correct, test failed')
        
        if count_mod == count_module:
            print('Number of modules correct, test passed')
        else:
            print('Number of modules not correct, test failed')       

        if count_method_def == count_method:
            print('Number of method and method defs in xmi file matches, test passed')
        else:
            print('Number of method and method defs in xmi file does not match, test failed')

        if count_method == count_method_sig:
            print('Number of methods and method sigs in xmi file matches, test passed')
        else:
            print('Number of methods and method sigs in xmi file does not match, test failed')


