from pyecore.resources import ResourceSet, URI
from testUtils import Types

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
meth_def = 0

#check number of packages and their names
for p, pack in enumerate(typegraph.packages):
    if p == 0:
        if pack.tName == 'my_package':
            check = True
        else:
            check = False
            print('Package name not correct.')
    if p > 0:
        check = False 
        print('Number of packages not correct.')

#check number of modules and their names
for mo, mod in enumerate(typegraph.modules):
    if mo <= 2: #3 modules in repo
        mod_name = mod.location.split('/')[-1] #get name
        if mod_name == 'callFunc' or mod_name == 'testClass' or mod_name == 'testCall':
            check = True
        else:
            check == False 
            print('Module names not correct.')
        if hasattr(mod, 'contains'):
            for contained in mod.contains:
                if contained.eClass.name == Types.METHOD_DEFINITION.value:
                    meth_def += 1
                if contained.eClass.name == Types.CLASS.value:
                    if contained.tName == 'myTest':
                        check = True
                    else:
                        check = False
                        print('Class name is not correct.')
                    if hasattr(contained, 'defines'):
                        for obj in contained.defines:
                            if obj.eClass.name == Types.METHOD_DEFINITION.value:
                                meth_def += 1
                    else:
                        check = False
                        print('Class is missing its defined method')
    else:
        check == False 
        print('Number of modules not correct.')
    
#check methods
for me, meth in enumerate(typegraph.methods):
    if me <= 2:
        if meth.tName == 'greet_friend' or meth.tName == 'my_hello' or meth.tName == 'call_name':
            check == True
        else:
            check = False
            print('Method names not correct.')
    else:
        check = False
        print('Number of methods not correct.')

#check number of method definitions in total
if meth_def == 3:
    check = True
else:
    check = False
    print(meth_def)
    print('Number of method definitions not correct.')

#print result
if check == True:
    print('Test passed.')
else:
    print('Test failed.')