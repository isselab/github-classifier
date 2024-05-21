import pandas as pd
import numpy as np

'''This test checks for the small unit test repository in the test folder if the number of converted 
node types in the csv files are correct. It also checks if the edges were converted correctly. 
Use the tool by running main.py to create the files first.'''

output_directory = '../../output_tests' #path to the folder containing the csv files

check = True
count_package = 0
count_class = 0
count_method = 0
count_method_def = 0
count_method_sig = 0
count_call = 0
count_parameter = 0
count_module = 0

#load csv file
node_features = pd.read_csv(f'{output_directory}/csv_files/testRepo1_nodefeatures.csv', header=None) 
node_array = np.array(node_features)
edges = pd.read_csv(f'{output_directory}/csv_files/testRepo1_A.csv', header=None) 
edge_array = np.array(edges)

#count node types
for obj in node_array:
    if obj == 6:
        count_package += 1
    if obj == 1:
        count_class += 1
    if obj == 2:
        count_method += 1
    if obj == 3:
        count_method_def += 1
    if obj == 4:
        count_method_sig += 1
    if obj == 7:
        count_parameter += 1
    if obj == 0:
        count_call += 1
    if obj == 5:
        count_module += 1

#check edges, format [node_id, node_id]
for e, edg in enumerate(edge_array):
    if edg[0] == 0:
        if edg[1] == 3 or edg[1] == 6:
            check = True
        else:
            check = False
    if edg[0] == 1:
        if edg[1] == 2:
            check = True
        else:
            check = False
    if edg[0] == 3:
        if edg[1] == 0 or edg[1] == 4:
            check = True
        else:
            check = False
    if edg[0] == 4:
        if edg[1] == 5:
            check = True
        else:
            check = False
    if edg[0] == 5:
        if edg[1] == 8:
            check = True
        else:
            check = False
    if edg[0] == 6:
        if edg[1] == 0 or edg[1] == 7:
            check = True
        else:
            check = False
    if edg[0] == 7:
        if edg[1] == 8:
            check = True
        else:
            check = False
    if edg[0] == 8:
        if edg[1] == 5:
            check = True
        else:
            check = False
    if edg[0] == 9:
        if edg[1] == 10 or edg[1] == 2:
            check = True
        else:
            check = False
    if edg[0] == 10:
        if edg[1] == 11:
            check = True
        else:
            check = False
    if edg[0] == 12:
        if edg[1] == 13 or edg[1] == 4:
            check = True
        else:
            check = False
    if edg[0] == 14:
        if edg[1] == 15 or edg[1] == 8:
            check = True
        else:
            check = False
    if e > 18:
        check = False
        print('Too many edges!')

#check number of nodes according to their types
if count_package == 1:
    print('Number of packages correct, test passed')
else:
    print('Number of packages not correct, test failed')

if count_class == 1: 
    print('Number of classes correct, test passed')
else:
    print('Number of classes not correct, test failed')

if count_method == 3:
    print('Number of methods correct, test passed')
else:
    print('Number of methods not correct, test failed')

if count_method_def == 3:
    print('Number of method definitions correct, test passed')
else:
    print('Number of method definitions not correct, test failed')

if count_method_sig == 3:
    print('Number of method signatures correct, test passed')
else:
    print('Number of method signatures not correct, test failed')

if count_parameter == 1:
    print('Number of parameters correct, test passed')
else:
    print('Number of parameters not correct, test failed')

if count_call == 1:
    print('Number of calls correct, test passed')
else:
    print('Number of calls not correct, test failed')
        
if count_module == 3:
    print('Number of modules correct, test passed')
else:
    print('Number of modules not correct, test failed')

#print result
if check == True:
    print('All edges set correctly, test passed')
else:
    print('Edges not correct, test failes')
