import ast
import os
from pyecore.resources import ResourceSet, URI
from NodeFeatures import NodeTypes

class ProjectEcoreGraph:
    def __init__(self, resource_set: ResourceSet, repository, write_in_file, output_directory=None):
        if repository is None or repository == '':
            raise ValueError('Directory is required')

        self.root_directory = repository.replace('\\', '/')

        metamodel_resource = resource_set.get_resource(URI('Basic.ecore'))

        self.epackage = metamodel_resource.contents[0]
        self.graph = self.epackage.getEClassifier('TypeGraph')(tName=self.root_directory.split('/')[-1])

        #initialize internal structures
        self.package_list = [] # entries [package_node, name, parent]
        self.module_list = [] # entries [module_node, module_name]
        self.current_module = None
        self.instances = []  # entries [instance_name, class_name]
        self.imports = []  # entries [module, alias]
        self.class_list = []  # entries [class_node, name, module/None]
        self.classes_without_module = []
        self.method_list = []  # entries [method_node, name, module_node]
        self.call_list = []
        self.check_list = [] # entries: class_node

        python_files = [os.path.join(root, file) for root, _, files in os.walk(
            self.root_directory) for file in files if file.endswith('.py')]
        
        #check for empty directories
        empty_dir = []
        for root, dirs, files in os.walk(self.root_directory):
            if not len(dirs) and not len(files):
                empty_dir.append(root)

        skipped_files = 0

        #create empty package structure
        if len(python_files)==0 and len(empty_dir)>0:
            for dir_path in empty_dir:
                dir_path = dir_path.split('\\')
                del dir_path[0]
                parent = None
                for item in dir_path:
                    if parent is None:
                        package_node = self.create_ecore_instance(NodeTypes.PACKAGE)
                        package_node.tName = item
                        self.graph.packages.append(package_node)
                        parent = package_node
                    else:
                        package_node = self.create_ecore_instance(NodeTypes.PACKAGE)
                        package_node.tName = item
                        package_node.parent = parent
                        parent = package_node
        
        #create and process modules with contained program entities
        for file_path in python_files:
            try:
               self.process_file(file_path)
            except Exception as e:
                if 'invalid syntax' in str(e):
                    skipped_files += 1
                    continue #skip file

        self.append_modules()
        self.search_meth_defs()
        self.check_missing_calls()

        if write_in_file is True:
            if output_directory is not None:
                self.write_xmi(resource_set, output_directory, repository)
            else:
                print('output directory is required!')
        print(f'{repository}, Number of files skipped: {skipped_files}')
            

    def check_missing_calls(self):
        pass


    '''check_list at start contains all classes with method defs that are created in typegraph,
    then they are compared to the classes with meth defs found in modules at the end,
    those not found need to be appended to a module, otherwise the meth defs are missing'''
    def search_meth_defs(self):
        classes_found = []
        for class_node in self.check_list:
            for mod in self.graph.modules:
                if hasattr(mod, 'contains'):
                    for obj in mod.contains:
                        if obj.eClass.name == NodeTypes.CLASS.value: 
                            if obj.tName == class_node.tName:
                                classes_found.append(class_node)

        # remove already appended classes from check_list
        for cl in classes_found:
            for item in self.check_list:
                if cl.tName == item.tName:
                    self.check_list.remove(item)

        if len(self.check_list) > 0:
            module_node = self.create_ecore_instance(NodeTypes.MODULE)
            module_node.location = 'ImportedClasses' #actually base or parent classes of other classes that are inside modules
            self.graph.modules.append(module_node)
            for obj in self.check_list:
                module_node.contains.append(obj)
                ref, ty = self.get_reference_by_name(obj.tName)
                if ref is not None:
                    imported = ref.split('.')
                    del imported[-1] #delete name of the class
                    for im in reversed(imported):
                        for pack in self.package_list:
                            if pack[1] == im:
                                for m in self.module_list:
                                    if m[1]== imported[-1]:
                                        m[0].contains.append(obj)

    def get_epackage(self):
        return self.epackage

    def get_graph(self):
        return self.graph
    
    def create_ecore_instance(self, type):
        return self.epackage.getEClassifier(type.value)()
    
    def get_current_module(self):
        return self.current_module
    
    def get_module_by_name(self, name):
        for module in self.module_list:
            if name == module[1]:
                return module[0]
        return None
    
    def get_module_by_location(self, location):
        for list_object in self.module_list:
            module = list_object[0]
            if module.location == location:
                return module
        return None
    
    '''appends modules at the end of the typegraph/xmi file'''
    def append_modules(self):
        for module in self.module_list:
            self.graph.modules.append(module[0])

    '''this function parses the code of one source file into an ast and traverses it for conversion into a metamodel, 
    the modules are created here and connected to a package, one module per file'''
    def process_file(self, path):
        path = path.replace('\\', '/')
        current_package = self.get_package_by_path(path)

        #create module
        self.current_module = self.create_ecore_instance(NodeTypes.MODULE)
        #self.current_module.external = 'Library'
        #self.current_module.flag = 'Library'
        #self.current_module.tAnnotation = 'Library' #added to flag the imported external libraries, try if it works
        self.current_module.location = path.removesuffix('.py')
        self.current_module.namespace = current_package
        path_split = self.current_module.location.replace(f"{self.root_directory}/", '').split('/')
        self.current_module_name = path_split[-1]
        self.module_list.append([self.current_module, self.current_module_name])

        # necessary to create inheritance structure for classes
        for class_object in self.classes_without_module:
            for index, path_part in enumerate(path_split):
                if class_object.tName == path_part:
                    self.current_module.contains.append(class_object)
                    if index == len(path_split) - 1:
                        for child in class_object.childClasses: 
                            self.current_module.contains.append(child)
                    # check necessary! otherwise x not in list error for some repos
                    if class_object in self.classes_without_module:
                        self.classes_without_module.remove(class_object)
                        class_object.delete()

        # added errors='ignore' to fix encoding issues in some repositories ('charmap cannot decode byte..')
        with open(path, 'r', errors='ignore') as file:
            code = file.read()
        # added following to fix some invalid character and syntax errors
        code = code.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace("»", ">>").replace("—", "-")
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
        package_node = self.create_ecore_instance(NodeTypes.PACKAGE)
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

    def get_class_from_internal_structure(self, class_name, module):
        for current_class in self.class_list:
            if class_name == current_class[1]:
                if module is None and current_class[2] is None:
                    return current_class[0]
                if hasattr(module, 'location') and hasattr(current_class[2], 'location'):
                    if module.location == current_class[2].location:
                        return current_class[0]
        return None
    
    def get_module_of_class(self, class_name, child_name):
        for current_class in self.class_list:
            if class_name == current_class[1]:
                if hasattr(current_class[0], 'childClasses'):
                    for child in current_class[0].childClasses:
                        if child.tName == child_name:
                            return current_class[2] #return module of parent class
        return None

    def get_class_by_name(self, name, structure=None, create_if_not_found=True, module=None, move_to_module=True):
        if structure is None:
            structure = self.graph.classes
        for class_object in structure:
            if class_object.tName == name:
                return class_object
        for class_object in self.classes_without_module:
            if class_object.tName == name:
                if move_to_module and module is not None:
                    module.contains.append(class_object)
                    self.classes_without_module.remove(class_object)
                return class_object
        if create_if_not_found:
            class_node = self.create_ecore_instance(NodeTypes.CLASS)
            class_node.tName = name
            if module is not None:
                module.contains.append(class_node)
                self.class_list.append([class_node, name, module])
            else:
                self.classes_without_module.append(class_node)
                self.class_list.append([class_node, name, None])
            structure.append(class_node)  # class appended to typegraph
            return class_node
        return None

    '''this function checks imported modules and classes (type = 0) 
    and assigned instances (type = 1)'''
    def get_reference_by_name(self, name):
        first_name = name.split('.')[0]
        for import_reference in self.imports:
            if import_reference[1] == first_name:
                # return module of the alias/imported object and 0 for type
                return import_reference[0], 0
        for instance in self.instances:
            if instance[0] == name:
                for import_reference in self.imports:
                    if import_reference[1] == instance[1]:
                        return import_reference[0], 0
                # return class_name of instance and 1 for type
                return instance[1], 1
        return None, None

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
    
    '''checks if TMethodDefinition object in class already exists'''
    def get_method_def_in_class(self, name, class_node):
        for method_def in class_node.defines:
            if method_def.signature.method.tName == name:
                return method_def
        return None
    
    def get_method_def_in_module(self, method_name, module):
        for object in module.contains:
            if object.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                if object.signature.method.tName == method_name:
                    return object
            if object.eClass.name == NodeTypes.CLASS.value:
                for meth in object.defines:
                    if meth.signature.method.tName == method_name:
                        return meth
        return None
    
    def get_method_def_from_internal_structure(self, method_name, module):
        for current_method in self.method_list:
            if method_name == current_method[1]:
                if module is None and current_method[2] is None:
                    return current_method[0]
                if hasattr(module, 'location') and hasattr(current_method[2], 'location'):
                    if module.location == current_method[2].location:
                        return current_method[0]
        return None
    
    def create_method_signature(self, method_node, name, arguments):
        method_signature = self.create_ecore_instance(NodeTypes.METHOD_SIGNATURE)
        method = self.create_ecore_instance(NodeTypes.METHOD)
        method.tName = name
        self.graph.methods.append(method)
        method_signature.method = method

        previous = None
        for arg in arguments:
            parameter = self.create_ecore_instance(NodeTypes.PARAMETER)
            if previous is not None:
                parameter.previous = previous
            previous = parameter
            method_signature.parameters.append(parameter)

        method_node.signature = method_signature 

        # for interal structure
        module_node = self.get_current_module()
        self.method_list.append([method_node, name, module_node])

    '''checks if call already exists'''
    def get_calls(self, caller_node, called_node):
        for call_object in caller_node.accessing:
            if call_object.target == called_node:
                return True
        return False

    def create_calls(self, caller_node, called_node):
        call = self.create_ecore_instance(NodeTypes.CALL)
        call.source = caller_node
        call.target = called_node

    def write_xmi(self, resource_set, output_directory, repository):
        repository_name = repository.split('\\')[-1]
        resource = resource_set.create_resource(URI(f'{output_directory}/xmi_files/{repository_name}.xmi'), use_uuid=True)
        resource.append(self.graph)
        resource.save()


'''class ASTVisitor defines the visits of the different node types of the ast
ASTVisitor calls the functions of ProjectEcoreGraph to create ecore instances'''

class ASTVisitor(ast.NodeVisitor):
    def __init__(self, graph_class):
        self.graph = graph_class.get_graph()
        self.graph_class = graph_class  # ecore graph instance
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
                base_node.childClasses.append(child) 
            elif isinstance(base_node, str) and type == 0:
                import_parent = None
                for import_class in base_node.split('.'):
                    import_node = self.graph_class.get_class_by_name(import_class) #module is None here
                    if import_parent is not None:  # if import_node does not have parent, it becomes parent itself
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
                method_node = self.graph_class.get_method_def_in_class(method_name, class_node)
                if method_node is None:
                    method_node = self.graph_class.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
                    self.graph_class.create_method_signature(method_node, method_name, item.args.args)
                    class_node.defines.append(method_node)
                    #to search for missing meth defs later
                    self.graph_class.check_list.append(class_node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.current_method = None
        if self.current_class is not None:
            self.current_method = self.graph_class.get_method_def_in_class(node.name, self.current_class)
        if self.current_method is None:
            self.current_class = None
            self.current_method = self.graph_class.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
            self.graph_class.create_method_signature(self.current_method, node.name, node.args.args)
            module_node = self.graph_class.get_current_module()
            module_node.contains.append(self.current_method)
        self.current_indentation = node.col_offset
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

    def visit_Call(self, node):
        if node.col_offset <= self.current_indentation:
            self.current_method = None
            self.current_indentation = node.col_offset
        instance = ""
        instance_node = node.func

        #call node can contain different node types
        while isinstance(instance_node, ast.Attribute):
            instance = f"{instance_node.attr}.{instance}"
            instance_node = instance_node.value
        if not isinstance(instance_node, ast.Name):
            self.generic_visit(node)
            return
        instance = f"{instance_node.id}.{instance}"
        if instance.endswith('.'):
            instance = instance[:-1]
        instance_from_graph, type = self.graph_class.get_reference_by_name(instance.replace(f".{instance.split('.')[-1]}", ''))
        if instance_from_graph is None:
            self.generic_visit(node)
            return
        instances = instance.split('.')
        instances[0] = instance_from_graph
        instance_name = ".".join(instances)
        method_name = instance_name.split('.')[-1]
        self.called_node = None
        self.call_check = False
        self.instance_missing = None

        print(instance_from_graph, type)

        # set called_node
        if type == 1:  # instance from class being called
            self.graph_class.remove_instance(instance_name)
            instance_node = self.graph_class.get_class_from_internal_structure(instance_name, None)
            if instance_node is not None:
                self.called_node = self.graph_class.get_method_def_in_class(method_name, instance_node)
                if self.called_node is None:
                    self.called_node = self.graph_class.get_method_def_from_internal_structure(method_name, instance_node)
                    if self.called_node is None and instance_node is not None:
                        self.called_node = self.graph_class.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
                        self.graph_class.create_method_signature(self.called_node, method_name, [])
                        instance_node.defines.append(self.called_node)

        if type == 0:  # instance from module being called
            module = instance_name.split('.')[0]
            instance_node = self.graph_class.get_module_by_name(module)
            if instance_node is not None:
                self.called_node = self.graph_class.get_method_def_in_module(method_name, instance_node)
                if self.called_node is None:
                    self.called_node = self.graph_class.get_method_def_from_internal_structure(method_name, instance_node)
                    if self.called_node is None and instance_node is not None:
                        called_node = self.graph_class.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
                        self.graph_class.create_method_signature(called_node, method_name, [])
                        instance_node.contains.append(called_node)
                        self.called_node = called_node
            if instance_node is None:
                self.instance_missing = instance_name

        # set caller_node
        if self.current_method is not None:
            caller_node = self.current_method
        else:
            module_node = self.graph_class.get_module_by_location(self.graph_class.get_current_module().location)
            method_location = self.graph_class.get_current_module().location
            method_name = method_location.split('/')[-1]
            caller_node = self.graph_class.get_method_def_in_module(method_name, module_node)
            if caller_node is None:
                caller_node = self.graph_class.get_method_def_from_internal_structure(method_name, module_node)
                if caller_node is None:
                    caller_node = self.graph_class.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
                    self.graph_class.create_method_signature(caller_node, method_name, [])
                    module_node.contains.append(caller_node)

        if self.called_node is not None:
            # check if identical call object already exists
            self.call_check = self.graph_class.get_calls(caller_node, self.called_node)
            if self.call_check is False:
                self.graph_class.create_calls(caller_node, self.called_node)

        # check after all the files are processed if modules and methods called exist then
        if self.instance_missing is not None:
            self.graph_class.call_list.append([self.instance_missing, caller_node])

        self.generic_visit(node)