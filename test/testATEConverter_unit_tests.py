from pyecore.resources import ResourceSet, URI
from testUtils import Types

'''This test checks if the small unit test repository in the test folder is converted correctly into an ecore metamodel.
It checks both the node types and the edges, which cannot be done for arbitrary repositories due to their size.
Use the tool by running main.py to create the files first.'''

output_directory = 'D:/test_output' #output of the tool

#load xmi file
rset = ResourceSet()
resource = rset.get_resource(URI('../Basic.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root
resource = rset.get_resource(URI(f'{output_directory}/xmi_files/testRepo1.xmi'))
typegraph = resource.contents[0]

#initialize check and node types without name attribute --> check by counting their number
check = False
meth_def = 0
meth_sig = 0
param = 0
call = 0

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
        #check edge between two modules and package
        if mod_name == 'callFunc' or mod_name == 'testClass':
            if mod.namespace.tName == 'my_package':
                check = True
            else:
                check = False
                print('Namespace of module should be the package. Error.')
        if hasattr(mod, 'contains'):
            for contained in mod.contains:
                if contained.eClass.name == Types.METHOD_DEFINITION.value:
                    meth_def += 1
                    #check call
                    if hasattr(contained, 'accessing'):
                        for ca in contained.accessing:
                            if ca.eClass.name == Types.CALL.value:
                                call += 1
                                if ca.target.signature.method.tName == 'my_hello':
                                    check = True
                                else:
                                    check = False
                                    print('call target not correct.')
                                if ca.source.signature.method.tName == 'greet_friend':
                                    check = True
                                else:
                                    check = False
                                    print('call source not correct.')
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
        if hasattr(meth, 'signatures'):
            for sig in meth.signatures:
                meth_sig += 1
                if hasattr(sig, 'parameters'):
                    for parameter in sig.parameters:
                        param += 1
        else:
            check = False
            print('Method signature is missing.')
    else:
        check = False
        print('Number of methods not correct.')

#check number of method definitions in total
if meth_def == 3:
    check = True
else:
    check = False
    print('Number of method definitions not correct.')

#check number of method signatures in total
if meth_sig == 3:
    check = True
else:
    check = False
    print('Number of method signatures not correct.')

#check number of parameters in total
if param == 1:
    check = True
else:
    check = False
    print('Number of parameters not correct.')

#check number of calls in total
if call == 1:
    check = True
else:
    check = False
    print('Number of calls not correct.')

#print result
if check == True:
    print('Test passed.')
else:
    print('Test failed.')