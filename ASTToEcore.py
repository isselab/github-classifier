import ast
import os
from enum import Enum
from pyecore.resources import ResourceSet, URI


class ProjectEcoreGraph:
    def __init__(self, directory, resource_set: ResourceSet):
        if directory is None or directory == '':
            raise ValueError('Directory is required')

        self.root_directory = directory.replace('\\', '/')

        metamodel_resource = resource_set.get_resource(URI('Basic.ecore'))

        self.epackage = metamodel_resource.contents[0]
        self.graph = self.epackage.getEClassifier('TypeGraph')(tName=self.root_directory.split('/')[-1])

        self.instances = []  #entry structure [instance_name, class_name]
        self.imports = []  #entry structure [module, alias]
        self.methods_without_signature = []
        self.classes_without_module = []
        self.current_module = None

        self.module_list = []
        self.call_list = []

        python_files = [os.path.join(root, file) for root, _, files in os.walk(self.root_directory) for file in files if file.endswith('.py')]

        for file_path in python_files:
            self.process_file(file_path)

        self.check_missing_calls()

    def check_missing_calls(self):
        for object in self.call_list:
            called_instance = object[0]
            #print(called_instance)
            caller_node = object[1]
            called_module = called_instance.split('.')[0]
            called_method = called_instance.split('.')[-1]
            module_node = self.get_module_by_name(called_module)
            #print(called_method)
            #print(module_node)
            if module_node is not None:
                method_node = self.get_method_in_module(called_method, module_node)
                #print(module_node.contains)
                #print(method_node)
                if method_node is not None:
                   # print(method_node)
                    call = self.create_ecore_instance(self.Types.CALL)
                    call.source = caller_node
                    call.target = method_node
                    #print(call.target)
                
                if method_node is None:
                    method_node = self.create_ecore_instance(self.Types.METHOD_DEFINITION) 
                    self.create_method_signature(method_node, called_method, [])
                    module_node.contains.append(method_node)
                    call = self.create_ecore_instance(self.Types.CALL)
                    call.source = caller_node
                    call.target = method_node
                    #print(call.target)
            if module_node is None:
                module = self.create_ecore_instance(self.Types.MODULE)
                method_node = self.create_ecore_instance(self.Types.METHOD_DEFINITION) #check existing methods again!
                self.create_method_signature(method_node, called_method, [])
                self.graph.modules.append(module)
                self.module_list.append([module, called_module])
                module.contains.append(method_node)
                call = self.create_ecore_instance(self.Types.CALL)
                call.source = caller_node
                call.target = method_node
        #maybe check here if module contains another module? for targets not set
                    

    def get_epackage(self):
        return self.epackage

    def get_graph(self):
        return self.graph

    def get_current_module(self):
        return self.current_module

    def add_import(self, module, alias):
        self.imports.append([module, alias])

    def add_instance(self, instance_name, class_name):
        reference, type = self.get_reference_by_name(class_name)
        if reference is not None and type == 0:
            classes = class_name.split('.')[1:]
            classes.insert(0, reference)
            class_name = ".".join(classes)
        self.instances.append([instance_name, class_name])

    def remove_instance(self, class_name):
        for instance in self.instances:
            if instance[1] == class_name:
                self.instances.remove(instance)

    def add_method_without_signature(self, method_node):
        self.methods_without_signature.append(method_node)

    #this function parses the code into an ast and traverses it for conversion into a metamodel, the modules are created here
    def process_file(self, path):
        path = path.replace('\\', '/')
        self.instances = []
        self.imports = []
        self.current_module = self.create_ecore_instance(self.Types.MODULE)
        self.current_module.location = path.removesuffix('.py')
        path_split = self.current_module.location.replace(f"{self.root_directory}/", '').split('/')
        self.current_module_name = path_split[-1]
        for class_object in self.classes_without_module:
            for index, path_part in enumerate(path_split):
                if class_object.tName == path_part:
                    if index == len(path_split) - 1:
                        for child in class_object.childClasses:
                            self.current_module.contains.append(child)
                    self.classes_without_module.remove(class_object)
                    class_object.delete()
        self.current_module.namespace = self.get_package_by_path(path)
        self.module_list.append([self.current_module, self.current_module_name])
        self.graph.modules.append(self.current_module)
        with open(path, 'r') as file:
            code = file.read()
        tree = ast.parse(code)
        visitor = ASTVisitor(self)
        visitor.visit(tree)

    def get_module_by_name(self, name):
        for module in self.module_list:
            if name == module[1]:
                return module[0]
        return None

    def get_reference_by_name(self, name):
        first_name = name.split('.')[0]
        for import_reference in self.imports:
            if import_reference[1] == first_name:
                return import_reference[0], 0
        for instance in self.instances:
            if instance[0] == name:
                for import_reference in self.imports:
                    if import_reference[1] == instance[1]:
                        return import_reference[0], 0
                return instance[1], 1
        return None, None

    def get_class_by_name(self, name, structure=None, create_if_not_found=True, module=None, move_to_module=True):
        if structure is None:
            structure = self.graph.classes
        for class_object in structure:
            if class_object.tName == name:
                return class_object
        for class_object in self.classes_without_module:
            if class_object.tName == name:
                if move_to_module and module is not None:
                    class_object.module = module
                    self.classes_without_module.remove(class_object)
                return class_object
        if create_if_not_found:
            class_node = self.create_ecore_instance(self.Types.CLASS)
            class_node.tName = name
            if module is not None:
                class_node.module = module
            else:
                self.classes_without_module.append(class_node)
            structure.append(class_node)
            return class_node
        return None

    def get_method_in_class(self, class_name, method_name):
        class_node = self.get_class_by_name(class_name)
        if class_node is None:
            return None
        return self.get_method_by_name(method_name, class_node)


    def get_method_by_name(self, name, structure):
        for method_object in structure.defines:
            if method_object.signature.method.tName == name:
                return method_object  #this is a TMethodDefinition object
        return None

    def get_module_by_location(self, location):
        for module in self.graph.modules:
            if module.location == location:
                return module
        return None

    def get_method_in_module(self, method_name, module):
        for object in module.contains:
            #maybe check here if module contains another module? for targets not set
            if object.eClass.name == self.Types.METHOD_DEFINITION.value:
                if object.signature.method.tName == method_name:
                    return object
            if object.eClass.name == self.Types.CLASS.value: #alternatively i could call get method by name here
                for meth in object.defines:
                    if meth.signature.method.tName == method_name:
                        return meth
        return None
    
    def get_package_by_path(self, path):
        package_hierarchy = path.replace(f"{self.root_directory}/", '').split('/')[:-1]
        parent_package = None
        package_node = None
        for package in package_hierarchy:
            package_node = self.get_package_by_name_and_parent(package, parent_package)
            parent_package = package_node
        return package_node

    def get_package_by_name_and_parent(self, name, parent):
        for package_node in self.graph.packages:
            return_package = self.get_package_recursive(package_node, name, parent)
            if return_package is not None:
                return return_package
        package_node = self.create_ecore_instance(self.Types.PACKAGE)
        package_node.tName = name
        package_node.parent = parent
        if parent is None:
            self.graph.packages.append(package_node)
        return package_node

    def get_package_recursive(self, package_node, name, parent):
        if package_node.tName == name and package_node.parent == parent:
            return package_node
        for subpackage in package_node.subpackages:
            return self.get_package_recursive(subpackage, name, package_node)
        return None

    def create_ecore_instance(self, type):
        return self.epackage.getEClassifier(type.value)()

    def create_method_signature(self, method_node, name, arguments):
        method_signature = self.create_ecore_instance(self.Types.METHOD_SIGNATURE)
        method = self.create_ecore_instance(self.Types.METHOD)
        method.tName = method_node.tName = name
        method.model = self.graph
        method_signature.method = method

        previous = None
        for _ in arguments:
            parameter = self.create_ecore_instance(self.Types.PARAMETER)
            if previous is not None:
                parameter.previous = previous
            previous = parameter
            method_signature.parameters.append(parameter)

        method_node.signature = method_signature
    
    #programm entities in metamodel
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

#class ASTVisitor defines the visits of the different node types of the ast
#ASTVisitor calls the functions of ProjectEcoreGraph to create ecore instances
class ASTVisitor(ast.NodeVisitor):
    def __init__(self, graph_class):
        self.graph = graph_class.get_graph()
        self.graph_class = graph_class  #graph_class is the ecore graph instance
        self.current_method = None
        self.current_class = None
        self.current_indentation = 0

    def visit_Import(self, node):
        for name in node.names:
            if name.asname is None:
                self.graph_class.add_import(name.name, name.name)
            else:
                self.graph_class.add_import(name.name, name.asname)

    def visit_ImportFrom(self, node):
        for name in node.names:
            if name.asname is None:
                self.graph_class.add_import(f"{node.module}.{name.name}", name.name)
            else:
                self.graph_class.add_import(f"{node.module}.{name.name}", name.asname)

    def create_inheritance_structure(self, node, child):
        base_node = None
        if isinstance(node, ast.Name):
            base_node, type = self.graph_class.get_reference_by_name(node.id)
            if base_node is None:
                base_node = self.graph_class.get_class_by_name(node.id, module=self.graph_class.get_current_module())
            elif isinstance(base_node, str) and type == 0:
                import_parent = None
                for import_class in base_node.split('.'):
                    import_node = self.graph_class.get_class_by_name(import_class)
                    if import_parent is not None:
                        import_parent.childClasses.append(import_node)
                    import_parent = import_node
                    base_node = import_node
            base_node.childClasses.append(child)
        elif isinstance(node, ast.Attribute):
            base_node = self.graph_class.get_class_by_name(node.attr)
            base_node.childClasses.append(child)
            self.create_inheritance_structure(node.value, base_node)
        return base_node

    def visit_ClassDef(self, node):
        class_name = node.name
        class_node = self.graph_class.get_class_by_name(class_name, module=self.graph_class.get_current_module())
        self.current_class = class_node

        for base in node.bases:
            self.create_inheritance_structure(base, class_node)

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.current_indentation = item.col_offset
                method_name = item.name
                method_node = self.graph_class.get_method_by_name(method_name, class_node)
                if method_node is None:
                    method_node = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
                    self.graph_class.create_method_signature(method_node, item.name, item.args.args)
                    class_node.defines.append(method_node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.current_method = None
        if self.current_class is not None:
            self.current_method = self.graph_class.get_method_by_name(node.name, self.current_class)
        if self.current_method is None:
            self.current_class = None
            self.current_method = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
            self.graph_class.create_method_signature(self.current_method, node.name, node.args.args)
            module_node = self.graph_class.get_current_module()
            module_node.contains.append(self.current_method)
        self.current_indentation = node.col_offset
        self.generic_visit(node)

    def get_dependency_nodes(self, structure):
        class_list = structure.split('.')[:-1]
        if len(class_list) == 0:
            class_list = [structure]
        root_class_name, type = self.graph_class.get_reference_by_name(class_list[0])
        if root_class_name is None:
            root_class_name = class_list[0]
        root_class = self.graph_class.get_class_by_name(root_class_name)

        current_node = root_class
        for class_name in class_list[1:]:
            current_node = self.graph_class.get_class_by_name(class_name, current_node.childClasses)
        return current_node

    def visit_Call(self, node):
        if node.col_offset <= self.current_indentation:
            self.current_method = None
            self.current_indentation = node.col_offset
        instance = ""
        instance_node = node.func

        #Call node can contain different node types
        while isinstance(instance_node, ast.Attribute):
            instance = f"{instance_node.attr}.{instance}"
            instance_node = instance_node.value
        if not isinstance(instance_node, ast.Name):
            self.generic_visit(node)
            return
        instance = f"{instance_node.id}.{instance}"
        if instance.endswith('.'):
            instance = instance[:-1]
        #print(instance.split('.')[-1])
        instance_from_graph, type = self.graph_class.get_reference_by_name(instance.replace(f".{instance.split('.')[-1]}", ''))
        if instance_from_graph is None:
            self.generic_visit(node)
            return
        instances = instance.split('.')
        #print(instances)
        instances[0] = instance_from_graph
        instance_name = ".".join(instances)
        #print(instance_name)
        method_name = instance_name.split('.')[-1]
        self.called_node = None
        self.instance_missing = None
        #if isinstance(instance_node, ast.Name) --> dann nur call machen bzw rest checken?
        called_module = instance_name.split('.')[0] 
        #print(called_module)
        called_method = instance_name.split('.')[-1]
        
        #check if called method is a constructor 
        if called_method[0].isupper():
            self.generic_visit(node)
            return

        #if e.g. os.os was imported
       # if called_module == called_method:
            #self.generic_visit(node)
            #return
        
        #set called_node
        #print(instance_from_graph, type)
        if type == 1: #instance from class being called
            self.graph_class.remove_instance(instance_name)
            instance_node = self.get_dependency_nodes(instance_name)
            called_node = self.graph_class.get_method_by_name(method_name, instance_node)
            self.called_node = called_node
        
            if self.called_node is None and instance_node is not None:
                called_node = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
                self.graph_class.create_method_signature(called_node, method_name, [])
                self.graph_class.add_method_without_signature(called_node)
                instance_node.defines.append(called_node)
                self.called_node = called_node

        if type == 0: #instance from module being called
            module = instance_name.split('.')[0]
            instance_node = self.graph_class.get_module_by_name(module)
            #print(instance_node)
            if instance_node is not None:
                called_node = self.graph_class.get_method_in_module(method_name, instance_node)
                #print(called_node)
                self.called_node = called_node
            if self.called_node is None and instance_node is not None:
                called_node = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
                self.graph_class.create_method_signature(called_node, method_name, [])
                self.graph_class.add_method_without_signature(called_node)
                instance_node.contains.append(called_node)
                self.called_node = called_node
            if instance_node is None:
                self.instance_missing = instance_name
                #print(self.instance_missing)

        #set caller_node
        if self.current_method is not None:
            caller_node = self.current_method
        else:
            module_node = self.graph_class.get_module_by_location(self.graph_class.get_current_module().location)
            caller_node = self.graph_class.get_method_in_module(self.graph_class.get_current_module().location, module_node)
            if caller_node is None:
                caller_node = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
                self.graph_class.create_method_signature(caller_node, self.graph_class.get_current_module().location, [])
                self.graph_class.add_method_without_signature(caller_node) #i added this
                module_node.contains.append(caller_node)
        for call_object in caller_node.accessing:
            if call_object.target == self.called_node:
                self.generic_visit(node)
                return
            
        #check after all the files are processed if modules and methods called exist then
        if self.instance_missing is not None:
            self.graph_class.call_list.append([self.instance_missing, caller_node])
        #if self.called_node is None:
            #self.graph_class.call_list.append([self.instance_missing, caller_node])
        
        #if self.instance_missing is None: #mmmhhh now no targets appear but calls exist at least some of them
            
            #self.generic_visit(node)
            #return
        #if self.called_node is not None: #i tried checking here if self.called_node is set, did not change a lot of targets not being set
       # else:

       #what calls do we want to appear in the files?!!! anscheinende werden in den test repos die definierten methoden nicht aufgerufen..nur paar importierte
       #--> dann müsste ich für die je ein tmodul objekt bauen mit den methoden um call mit target zu setzen

        if self.called_node is not None:
            call = self.graph_class.create_ecore_instance(self.graph_class.Types.CALL)
            call.source = caller_node
            call.target = self.called_node #set to Meth Def
            #print(call.target)

        self.generic_visit(node)

    def visit_Assign(self, node):
        if node.col_offset <= self.current_indentation:
            self.current_method = None
            self.current_indentation = node.col_offset
        if isinstance(node.value, ast.Call):
            current_node = node.value.func
            instance = ""
            while isinstance(current_node, ast.Attribute):
                instance = f"{current_node.attr}.{instance}"
                current_node = current_node.value
            if isinstance(current_node, ast.Name):
                instance = f"{current_node.id}.{instance}"
                for target in node.targets:
                    current_target = target
                    target_name = ""
                    while isinstance(current_target, ast.Attribute):
                        target_name = f"{current_target.attr}.{target_name}"
                        current_target = current_target.value
                    if isinstance(current_target, ast.Name):
                        target_name = f"{current_target.id}.{target_name}"
                        self.graph_class.add_instance(target_name[:-1], instance[:-1])
        self.generic_visit(node)
