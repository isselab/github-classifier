import ast
import os
from enum import Enum
from pyecore.resources import ResourceSet, URI

class ProjectEcoreGraph:
    def __init__(self, directory, resource_set: ResourceSet, output_directory, repository):
        if directory is None or directory == '':
            raise ValueError('Directory is required')

        self.root_directory = directory.replace('\\', '/')

        metamodel_resource = resource_set.get_resource(URI('Basic.ecore'))

        self.epackage = metamodel_resource.contents[0]
        self.graph = self.epackage.getEClassifier('TypeGraph')(tName=self.root_directory.split('/')[-1])

        #initialize internal structures
        self.package_list = [] # entry structure [package_node, name, parent]
        self.module_list = [] # entry structure [module_node, module_name]

        python_files = [os.path.join(root, file) for root, _, files in os.walk(
            self.root_directory) for file in files if file.endswith('.py')]

        for file_path in python_files:
            self.process_file(file_path)

        self.append_modules()
        self.write_xmi(resource_set, output_directory, repository)


    def get_epackage(self):
        return self.epackage

    def get_graph(self):
        return self.graph
    
    def create_ecore_instance(self, type):
        return self.epackage.getEClassifier(type.value)()
    
    #appends modules at the end of the typegraph/xmi file
    def append_modules(self):
        for module in self.module_list:
            self.graph.modules.append(module[0])

    '''this function parses the code of one source file into an ast and traverses it for conversion into a metamodel, 
    the modules are created here and connected to a package, one module per file'''
    def process_file(self, path):
        path = path.replace('\\', '/')
        
        current_package = self.get_package_by_path(path)

        #create module
        self.current_module = self.create_ecore_instance(self.Types.MODULE)
        self.current_module.location = path.removesuffix('.py')
        self.current_module.namespace = current_package
        path_split = self.current_module.location.replace(f"{self.root_directory}/", '').split('/')
        self.current_module_name = path_split[-1]
        self.module_list.append([self.current_module, self.current_module_name])

        # added errors='ignore' to fix encoding issues in some repositories ('charmap cannot decode byte..')
        with open(path, 'r', errors='ignore') as file:
            code = file.read()
        # added following to fix some invalid character and syntax errors
        code = code.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace("»", ">>").replace("—", "-").replace("¿", "_")
        tree = ast.parse(code)
        visitor = ASTVisitor(self)
        visitor.visit(tree)

    def get_package_by_path(self, path):
        package_hierarchy = path.replace(f"{self.root_directory}/", '').split('/')[:-1]
        parent_package = None
        package_node = None
        # first element is highest in package hierarchy
        for package_name in package_hierarchy:
            package_node = self.get_package_by_name_and_parent(package_name, parent_package)
            parent_package = package_node
        return package_node
    
    '''this function creates TPackage objects, one package per folder in the repository,
    and appends the package that is highest in hierarchy to the typegraph, the rest are subpackages'''
    def get_package_by_name_and_parent(self, name, parent):
        for package_node in self.graph.packages:
            return_package = self.get_package_recursive(package_node, name, parent)
            if return_package is not None:
                return return_package
        my_package = self.check_package_list(name, parent)  # checks if subpackage already exists
        if my_package is not None:
            return my_package
        package_node = self.create_ecore_instance(self.Types.PACKAGE)
        package_node.tName = name
        if parent is not None:
            package_node.parent = parent
        if parent is None:
            self.graph.packages.append(package_node)
        self.package_list.append([package_node, name, parent])
        return package_node
    
    def get_package_recursive(self, package_node, name, parent):
        if package_node.tName == name and package_node.parent == parent:
            return package_node
        for subpackage in package_node.subpackages:
            return self.get_package_recursive(subpackage, name, package_node)
        return None
    
    # this fixed the multiple subpackages
    def check_package_list(self, package_name, parent):
        for package in self.package_list:
            if package_name == package[1]:
                if parent is None and package[2] is None:
                    return package[0]
                if parent is not None and package[2] is not None:
                    if parent.tName == package[2].tName:
                        return package[0]
        return None

    def write_xmi(self, resource_set, output_directory, repository):
        resource = resource_set.create_resource(URI(f'{output_directory}/xmi_files/{repository}.xmi'), use_uuid=True)
        resource.append(self.graph)
        resource.save()

    # programm entities in metamodel
    class Types(Enum):
        CALL = "TCall"
        CLASS = "TClass"
        FIELD = "TField"
        MODULE = "TModule"
        METHOD = "TMethod"
        METHOD_SIGNATURE = "TMethodSignature"
        METHOD_DEFINITION = "TMethodDefinition"
        PACKAGE = "TPackage"
        PARAMETER = "TParameter"

'''class ASTVisitor defines the visits of the different node types of the ast
ASTVisitor calls the functions of ProjectEcoreGraph to create ecore instances'''

class ASTVisitor(ast.NodeVisitor):
    def __init__(self, graph_class):
        self.graph = graph_class.get_graph()
        self.graph_class = graph_class  # graph_class is the ecore graph instance
        self.current_method = None
        self.current_class = None
        self.current_indentation = 0
