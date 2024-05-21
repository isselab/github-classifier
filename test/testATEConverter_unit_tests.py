'''This test checks if the small sample repository in the test folder is converted correctly into an ecore metamodel.
It checks both the node types and the edges, which cannot be done for arbitrary repositories due to their size.
Use the tool by running main.py to create the files first.'''

repository_directory = 'unit_tests' #path to the folder containing the test repository
output_directory = '../output_tests' #output of the tool