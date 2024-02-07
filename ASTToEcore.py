import ast
import os
from enum import Enum
from pyecore.resources import ResourceSet, URI


class ProjectEcoreGraph:
    def __init__(self, directory):
        if directory is None or directory == '':
            raise ValueError('Directory is required')

        self.root_directory = directory.replace('\\', '/')

        resource_set = ResourceSet()
        metamodel_resource = resource_set.get_resource(URI('metamodel.ecore'))

        self.package = metamodel_resource.contents[0]
        self.graph = self.package.getEClassifier('TypeGraph')(tName=self.root_directory.split('/')[-1])

        self.instances = []
        self.imports = []
        self.methods_without_signature = []
        self.calls_without_target = []
        self.current_module = None

        python_files = [os.path.join(root, file) for root, _, files in os.walk(project_directory) for file in files if file.endswith('.py')]

        for file_path in python_files:
            self.process_file(file_path)

    def get_package(self):
        return self.package

    def get_graph(self):
        return self.graph

    def get_current_module(self):
        return self.current_module

    def add_import(self, module, alias):
        self.imports.append([module, alias])

    def add_instance(self, instance_name, class_name):
        self.instances.append([instance_name, class_name])

    def add_method_without_signature(self, method_node):
        self.methods_without_signature.append(method_node)

    def add_call_without_target(self, source, target_instance, method_name):
        self.calls_without_target.append([source, target_instance, method_name])

    def process_file(self, path):
        path = path.replace('\\', '/')
        self.instances = []
        self.imports = []
        self.current_module = self.create_ecore_instance(self.Types.MODULE)
        self.current_module.location = path.removesuffix('.py')
        self.current_module.namespace = self.get_package_by_path(path)
        self.graph.modules.append(self.current_module)
        with open(path, 'r') as file:
            code = file.read()
        tree = ast.parse(code)
        visitor = ASTVisitor(self)
        visitor.visit(tree)

    def get_reference_by_name(self, name):
        for import_reference in self.imports:
            if import_reference[1] == name:
                return import_reference[0]
        for instance in self.instances:
            if instance[0] == name:
                return instance[1]
        return None

    def get_class_by_name(self, name, structure=None, create_if_not_found=True, module=None):
        if structure is None:
            structure = self.graph.classes
        for class_object in structure:
            if class_object.tName == name:
                return class_object
        if create_if_not_found:
            class_node = self.create_ecore_instance(self.Types.CLASS)
            class_node.tName = name
            if module is None:
                class_node.module = self.current_module
            else:
                class_node.module = module
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
                return method_object
        return None

    def get_module_by_location(self, location):
        for module in self.graph.modules:
            if module.location == location:
                return module
        return None

    def get_method_in_module(self, method_name, module):
        for object in module.contains:
            if object.eClass == self.Types.METHOD_DEFINITION:
                if object.signature.method.tName == method_name:
                    return object
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
        return self.package.getEClassifier(type.value)()

    def create_method_signature(self, method_node, name, arguments):
        method_signature = self.create_ecore_instance(self.Types.METHOD_SIGNATURE)
        method = self.create_ecore_instance(self.Types.METHOD)
        method.tName = method_node.tName = name
        method.model = self.graph
        method_signature.method = method

        previous = None
        for index, argument in enumerate(arguments):
            parameter = self.create_ecore_instance(self.Types.PARAMETER)
            if previous is not None:
                parameter.previous = previous
            previous = parameter
            if index == 0:
                method_signature.firstParameter = parameter
                continue
            method_signature.parameters.append(parameter)

        method_node.signature = method_signature

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


class ASTVisitor(ast.NodeVisitor):
    def __init__(self, graph_class):
        self.graph = graph_class.get_graph()
        self.graph_class = graph_class
        self.current_method = None
        self.current_class = None

    def visit_Import(self, node):
        for name in node.names:
            if name.asname is None:
                self.graph_class.add_import(name.name, name.name)
            else:
                self.graph_class.add_import(name.name, name.asname)

    def visit_ImportFrom(self, node):
        for name in node.names:
            if name.asname is None:
                self.graph_class.add_import(node.module, name.name)
            else:
                self.graph_class.add_import(node.module, name.asname)

    def create_inheritance_structure(self, node, child):
        base_node = None
        if isinstance(node, ast.Name):
            base_node = self.graph_class.get_reference_by_name(node.id)
            if base_node is None:
                base_node = self.graph_class.get_class_by_name(node.id)
            elif isinstance(base_node, str):
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
        class_node = self.graph_class.get_class_by_name(class_name)
        self.current_class = class_node

        for base in node.bases:
            self.create_inheritance_structure(base, class_node)

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
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
        self.generic_visit(node)

    def get_dependency_nodes(self, structure):
        class_list = structure.split('.')
        root_class = self.graph_class.get_class_by_name(class_list[0])
        current_node = root_class
        for class_name in class_list[1:]:
            current_node = self.graph_class.get_class_by_name(class_name, current_node.childClasses)
        return current_node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            instances = [node.func.attr]
            instance_node = node.func.value
            while isinstance(instance_node, ast.Attribute):
                instances.append(instance_node.attr)
                instance_node = instance_node.value
            if not isinstance(instance_node, ast.Name):
                self.generic_visit(node)
                return
            instance_name = instance_node.id
            instance_from_graph = self.graph_class.get_reference_by_name(instance_name)
            if instance_from_graph is None:
                self.generic_visit(node)
                return
            instance_name = instance_from_graph
            instance_node = self.get_dependency_nodes(instance_name)

            called_node = self.graph_class.get_method_by_name(node.func.attr, instance_node)
            if called_node is None and instance_node is not None:
                called_node = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
                self.graph_class.create_method_signature(called_node, node.func.attr, [])
                self.graph_class.add_method_without_signature(called_node)
                instance_node.defines.append(called_node)
            if self.current_method is not None:
                caller_node = self.current_method
            else:
                module_node = self.graph_class.get_module_by_location(self.graph_class.get_current_module().location)
                caller_node = self.graph_class.get_method_in_module(self.graph_class.get_current_module().location, module_node)
                if caller_node is None:
                    caller_node = self.graph_class.create_ecore_instance(self.graph_class.Types.METHOD_DEFINITION)
                    self.graph_class.create_method_signature(caller_node, self.graph_class.get_current_module().location, [])
                    module_node.contains.append(caller_node)
            for call_object in caller_node.accessing:
                if call_object.target == called_node:
                    self.generic_visit(node)
                    return
            call = self.graph_class.create_ecore_instance(self.graph_class.Types.CALL)
            call.source = caller_node
            call.target = called_node
            self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and isinstance(node.value, ast.Call):
                class_name = target.value.id
    #             attribute_name = target.attr
    #             self.graph.classes.append(Class(name=class_name))
    #             self.graph.add_edge(class_name, attribute_name)
    #             self.graph.add_edge(class_name, node.value.func.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        pass


project_directory = '/home/marwin/Documents/Studienprojekt_Master/studienprojekt-grundrissgenerierung'
#project_directory = 'D:/Dokumente/Studium/Informatik/04/Studienprojekt'#/studienprojekt-grundrissgenerierung'
project_graph = ProjectEcoreGraph(project_directory)

rset = ResourceSet()
resource = rset.create_resource(URI('test.xmi'))
resource.append(project_graph.get_graph())
resource.save()
