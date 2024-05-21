from pyecore.resources import ResourceSet, URI

'''This test checks if the small sample repository in the test folder is converted correctly into an ecore metamodel.
It checks both the node types and the edges, which cannot be done for arbitrary repositories due to their size.
Use the tool by running main.py to create the files first.'''

output_directory = '../../output_tests' #output of the tool

#load xmi file
rset = ResourceSet()
resource = rset.get_resource(URI('../Basic.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root
resource = rset.get_resource(URI(f'{output_directory}/xmi_files/testRepo1.xmi'))
typegraph = resource.contents[0]

check = False

#check number of packages and their names
for p, pack in enumerate(typegraph.packages):
    if p == 0:
        if pack.tName == 'my_package':
            check = True
    if p > 0:
        check = False 

#check number of modules and their names
for m, mod in enumerate(typegraph.modules):
    if m <= 2: #3 modules in repo
        mod_name = mod.location.split('/')[-1] #get name
        if mod_name == 'callFunc' or mod_name == 'testClass' or mod_name == 'testCall':
            check = True
        else:
            check == False 
    else:
        check == False 
    


#print result
if check == True:
    print('Test passed.')
else:
    print('Test failed.')