import ast
import logging
import os
from logging import warning

from pyecore.resources import ResourceSet, URI

from NodeFeatures import NodeTypes

logger = logging.getLogger(__name__)
logging.basicConfig(filename='skipped_files.log',
                    level=logging.WARNING, filemode='a')


class ProjectEcoreGraph:
    """
    Class to represent a project Ecore graph, processing Python files to create a type graph.
    """

    def __init__(self, resource_set: ResourceSet, repository, write_in_file, output_directory=None):
        """
        Initializes the ProjectEcoreGraph.

        Args:
            resource_set (ResourceSet?): The resource set for Ecore.
            repository (str?): The root directory of the project.
            write_in_file (bool?): Flag indicating whether to write output to a file.
            output_directory (str?, optional?): Directory for output files.

        Raises:
            ValueError: If the repository is None or empty.
        """
        self.current_module_name = None
        if repository is None or repository == '':
            raise ValueError('Directory is required')

        self.root_directory = repository.replace('\\', '/')
        self.e_package = resource_set.get_resource(URI('Basic.ecore')).contents[0]
        self.graph = self.e_package.getEClassifier('TypeGraph')(
            tName=self.root_directory.split('/')[-1])

        # initialize internal structures
        self.package_list = []  # entries: [package_node, name, parent]
        self.module_list = []  # entries: [module_node, module_name]
        self.current_module = None
        self.instances = []  # entries: [instance_name, class_name]
        self.imports = []  # entries: [module, alias]
        self.class_list = []  # entries: [class_node, name, module/None]
        self.classes_without_module = []
        self.method_list = []  # entries: [method_node, name, module_node]
        self.check_list = []  # entries: class_node
        # entries: [caller_node_module, caller_node, called_function_name] both methods in the same module
        self.call_in_module = []
        self.call_external_module = []  # entries: [imported instance, caller node]
        self.call_imported_library = []  # entries: [caller_node, imported_instance]
        # entries: [module_node, module_name, package_node, package_name]
        self.imported_libraries = []
        self.imported_package = None
        self.current_parent = None

        python_files = [os.path.join(root, file) for root, _, files in os.walk(
            self.root_directory) for file in files if file.endswith('.py')]

        # check for empty directories
        empty_dir = []
        for root, dirs, files in os.walk(self.root_directory):
            if not len(dirs) and not len(files):
                empty_dir.append(root)

        skipped_files = 0

        # create empty package structure
        if len(python_files) == 0 and len(empty_dir) > 0:
            for dir_path in empty_dir:
                dir_path = dir_path.split('\\')
                del dir_path[0]
                parent = None
                for item in dir_path:
                    if parent is None:
                        package_node = self.create_ecore_instance(
                            NodeTypes.PACKAGE)
                        package_node.tName = item
                        self.graph.packages.append(package_node)
                        self.package_list.append([package_node, item, None])
                        parent = package_node
                    else:
                        package_node = self.create_ecore_instance(
                            NodeTypes.PACKAGE)
                        package_node.tName = item
                        package_node.parent = parent
                        self.package_list.append([package_node, item, parent])
                        parent = package_node

        # create and process modules with contained program entities
        for file_path in python_files:
            try:
                self.process_file(str(file_path))
            except Exception as e:
                if 'invalid syntax' in str(e):
                    logger.warning(f'skipped: {file_path}')
                    skipped_files += 1
                    continue  # skip file

        # append modules and possibly missing nodes to type graph to set calls after
        self.append_modules()
        self.check_for_missing_nodes()

        # set calls
        if len(self.call_in_module) > 0:
            self.set_internal_module_calls()
        if len(self.call_external_module) > 0:
            self.set_external_module_calls()
        if len(self.call_imported_library) > 0:
            self.set_imported_libraries_calls()

        if write_in_file is True:
            if output_directory is not None:
                self.write_xmi(resource_set, output_directory, repository)
            else:
                print('output directory is required!')
        print(f'{repository}, Number of files skipped: {skipped_files} \n')

    def set_imported_libraries_calls(self):
        """Creates structure of imported external libraries and sets calls to it"""
        for item in self.call_imported_library:
            caller_node = item[0]
            imported = item[1]
            split_import = imported.split('.')

            package_name, subpackage_names, module_name, class_name, method_name = self.set_import_names(
                split_import)
            # flag tLib only works for classes, use name for other types
            package_name += '_ExternalLibrary'
            module_name += '_ExternalLibrary'
            method_name += '_ExternalLibrary'

            package_node = self.get_imported_library_package(package_name)
            if package_node is not None:
                module_node = self.get_imported_library(module_name)
                if module_node is not None:
                    if class_name is not None:
                        found_class = False
                        if hasattr(module_node, 'contains'):
                            for obj in module_node.contains:
                                if obj.eClass.name == NodeTypes.CLASS.value:
                                    if obj.tName == class_name:
                                        found_class = True
                                        found_method = False
                                        if hasattr(obj, 'defines'):
                                            for meth in obj.defines:
                                                if meth.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                                                    if meth.signature.method.tName == method_name:
                                                        found_method = True
                                                        call_check = self.get_calls(
                                                            caller_node, meth)
                                                        if call_check is False:
                                                            self.create_call(
                                                                caller_node, meth)
                                        if found_method is False:
                                            method_node = self.create_ecore_instance(
                                                NodeTypes.METHOD_DEFINITION)
                                            self.create_method_signature(
                                                method_node, method_name, [])
                                            obj.defines.append(method_node)
                                            self.create_call(
                                                caller_node, method_node)
                        if found_class is False:
                            self.create_imported_class_call(
                                module_node, class_name, method_name, caller_node)
                    if class_name is None:
                        found_method = False
                        if hasattr(module_node, 'contains'):
                            for meth_def in module_node.contains:
                                if meth_def.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                                    if meth_def.signature.method.tName == method_name:
                                        found_method = True
                                        call_check = self.get_calls(
                                            caller_node, meth_def)
                                        if call_check is False:
                                            self.create_call(
                                                caller_node, meth_def)
                        if found_method is False:
                            self.create_imported_method_call(
                                module_node, method_name, caller_node)
                if module_node is None:
                    module_node = self.create_ecore_instance(NodeTypes.MODULE)
                    module_node.location = module_name
                    self.graph.modules.append(module_node)
                    if class_name is not None:
                        self.create_imported_class_call(
                            module_node, class_name, method_name, caller_node)
                    if class_name is None:
                        self.create_imported_method_call(
                            module_node, method_name, caller_node)
                    # get package in whose namespace imported module is
                    pack_name = None
                    if isinstance(subpackage_names, str):
                        pack_name = subpackage_names + '_ExternalLibrary'
                    if isinstance(subpackage_names, list):
                        pack_name = subpackage_names[-1] + '_ExternalLibrary'
                    if pack_name is not None:
                        current_package_node = self.get_imported_library_package(
                            pack_name)
                        # subpackage exists
                        if current_package_node is not None:
                            module_node.namespace = current_package_node
                            self.imported_libraries.append(
                                [module_node, module_name, current_package_node, pack_name])
                        # subpackage does not exist
                        if current_package_node is None:
                            subpackage_node = self.create_ecore_instance(
                                NodeTypes.PACKAGE)
                            subpackage_node.tName = pack_name
                            subpackage_node.parent = package_node
                            module_node.namespace = subpackage_node
                            self.imported_libraries.append(
                                [module_node, module_name, subpackage_node, pack_name])
                    if subpackage_names is None:
                        self.imported_libraries.append(
                            [module_node, module_name, None, None])
            if package_node is None:
                if len(split_import) == 2:
                    package_node = self.create_ecore_instance(
                        NodeTypes.PACKAGE)
                    package_node.tName = package_name
                    module_node = self.create_ecore_instance(NodeTypes.MODULE)
                    module_node.location = package_name
                    module_node.namespace = package_node
                    method_node = self.create_ecore_instance(
                        NodeTypes.METHOD_DEFINITION)
                    self.create_method_signature(method_node, method_name, [])
                    module_node.contains.append(method_node)
                    self.imported_libraries.append(
                        [module_node, package_name, package_node, package_name])
                    self.graph.modules.append(module_node)
                    self.graph.packages.append(package_node)
                    self.create_call(caller_node, method_node)
                if len(split_import) > 2:
                    # create package hierarchy
                    package_node = self.create_ecore_instance(
                        NodeTypes.PACKAGE)  # parent package
                    package_node.tName = package_name
                    self.graph.packages.append(package_node)
                    self.imported_libraries.append(
                        [None, None, package_node, package_name])
                    self.imported_package = package_node
                    if subpackage_names is not None:
                        self.create_package_hierarchy(
                            package_node, subpackage_names)
                    # create module
                    module_node = self.create_ecore_instance(NodeTypes.MODULE)
                    module_node.location = module_name
                    self.graph.modules.append(module_node)
                    if self.imported_package is not None:
                        module_node.namespace = self.imported_package

                        package_key = self.get_imported_library_package_key(
                            self.imported_package.tName)
                        import_entry = self.imported_libraries[package_key]
                        import_entry[0] = module_node
                        import_entry[1] = module_name
                    else:
                        # self.imported_package can be None (very rarely) due to complex import possibilities
                        package_node = self.create_ecore_instance(
                            NodeTypes.PACKAGE)
                        package_node.tName = module_name
                        module_node.namespace = package_node
                        self.graph.packages.append(package_node)
                        self.imported_libraries.append(
                            [module_node, module_name, package_node, module_name])
                    # create called method
                    method_node = self.create_ecore_instance(
                        NodeTypes.METHOD_DEFINITION)
                    self.create_method_signature(method_node, method_name, [])
                    if class_name is not None:
                        class_node = self.create_ecore_instance(
                            NodeTypes.CLASS)
                        class_node.tName = class_name
                        class_node.tLib = True
                        class_node.defines.append(method_node)
                        self.graph.classes.append(class_node)
                        module_node.contains.append(class_node)
                    if class_name is None:
                        module_node.contains.append(method_node)
                    # set call
                    self.create_call(caller_node, method_node)

    def create_package_hierarchy(self, parent_package, subpackage_names, lib_flag=True):
        """
        Creates the hierarchy of packages and subpackages for imported external libraries.

        Args:
            parent_package: The parent package node.
            subpackage_names: The names of the subpackages to create.
            lib_flag (bool): Flag indicating if the packages are for libraries.
        """
        if isinstance(subpackage_names, str):
            package_node = self.create_ecore_instance(NodeTypes.PACKAGE)
            if lib_flag is True:
                name = subpackage_names + '_ExternalLibrary'
            else:
                name = subpackage_names
            package_node.tName = name
            package_node.parent = parent_package
            if lib_flag is True:
                self.imported_libraries.append(
                    [None, None, package_node, name])
            else:
                self.package_list.append([package_node, name, parent_package])
            self.imported_package = package_node
        if isinstance(subpackage_names, list):
            for e, element in enumerate(subpackage_names):
                if lib_flag is True:
                    element_lib = element + '_ExternalLibrary'
                else:
                    element_lib = element
                package_node = self.create_ecore_instance(NodeTypes.PACKAGE)
                package_node.tName = element_lib
                if e == 0:
                    package_node.parent = parent_package
                else:
                    package_node.parent = self.current_parent
                if lib_flag is True:
                    self.imported_libraries.append(
                        [None, None, package_node, element_lib])
                else:
                    if e == 0:
                        self.package_list.append(
                            [package_node, element_lib, parent_package])
                    else:
                        self.package_list.append(
                            [package_node, element_lib, self.current_parent])
                self.current_parent = package_node
                self.imported_package = package_node

    def create_imported_method_call(self, module_node, method_name, caller_node):
        """
        Creates a method from an imported module from an external library.

        Args:
            module_node: The module node where the method will be created.
            method_name: The name of the method.
            caller_node: The node that is calling the method.
        """
        method_node = self.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
        self.create_method_signature(method_node, method_name, [])
        module_node.contains.append(method_node)
        self.create_call(caller_node, method_node)

    def create_imported_class_call(self, module_node, class_name, method_name, caller_node):
        """
        Creates a class and method from an imported module from an external library.

        Args:
            module_node: The module node where the class will be created.
            class_name: The name of the class.
            method_name: The name of the method.
            caller_node: The node that is calling the method.
        """
        class_node = self.create_ecore_instance(NodeTypes.CLASS)
        class_node.tName = class_name
        class_node.tLib = True  # flag for external libraries, only works for classes
        self.graph.classes.append(class_node)
        module_node.contains.append(class_node)
        method_node = self.create_ecore_instance(NodeTypes.METHOD_DEFINITION)
        self.create_method_signature(method_node, method_name, [])
        class_node.defines.append(method_node)
        self.create_call(caller_node, method_node)

    def get_imported_library_package(self, package_name):
        """
        Retrieves the imported library package by name.

            Args:
                package_name (str?): The name of the package.

            Returns:
                Package node or None if not found.
            """
        for lib in self.imported_libraries:
            if lib[3] == package_name:
                return lib[2]
        return None

    def get_imported_library_package_key(self, package_name):
        """
        Gets the key of the imported library package by name.

        Args:
            package_name (str): The name of the package.

        Returns:
            int or None if not found.
        """
        for key, lib in enumerate(self.imported_libraries):
            if lib[3] == package_name:
                return key
        return None

    def get_imported_library(self, module_name):
        """
        Retrieves the imported library by module name.

        Args:
            module_name (str?): The name of the module.

        Returns:
            Module node or None if not found.
        """
        for lib in self.imported_libraries:
            if lib[1] == module_name:
                return lib[0]
        return None

    def set_external_module_calls(self):
        """sets calls for within the repo imported objects, these objects already exist
        because they are defined in the repo, but are in different modules/packages"""
        for item in self.call_external_module:
            imported_instance = item[0]
            caller_node = item[1]
            split_import = imported_instance.split('.')
            package_name, subpackage_names, module_name, class_name, method_name = self.set_import_names(
                split_import)

            module_node = self.get_module_by_name(module_name)
            if module_node is not None:
                for obj in module_node.contains:
                    if class_name is not None:
                        if obj.eClass.name == NodeTypes.CLASS.value:
                            if obj.tName == class_name:
                                self.create_method_in_class_call(
                                    method_name, obj, caller_node)
                    if obj.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                        self.create_method_call(obj, method_name, caller_node)
            if module_node is None:
                # if len==1 simple import … statement, included only if import is used (in that case len>1)
                if len(split_import) > 1:
                    self.call_imported_library.append(
                        [caller_node, imported_instance])

    @staticmethod
    def set_import_names(split_import):
        """
        Sets the names for imported modules, classes, and methods.

         Args:
            split_import (list): The split import path.

        Returns:
            tuple: Package name, subpackage names, module name, class name, method name.
        """
        package_name = split_import[0]
        method_name = split_import[-1]
        class_name = None
        module_name = None
        subpackage_names = None

        if len(split_import) == 2:
            module_name = split_import[0]

        if len(split_import) > 2:  # structure: package/module, module/class, method
            obj_name = split_import[1]
            if obj_name[0].isupper():  # relies on naming conventions to check the type
                class_name = obj_name
                module_name = split_import[0]
            else:
                module_name = obj_name  # in this case the first imported instance was a package name

        if len(split_import) > 3:  # structure: package, subpackage/module, module/class, method
            obj_name = split_import[2]
            if obj_name[0].isupper():
                class_name = obj_name
                module_name = split_import[1]
            else:
                module_name = obj_name
                subpackage_names = split_import[1]

        if len(split_import) > 4:  # structure: packages, subpackages...,module, (class,) method
            obj_name = split_import[-2]
            if obj_name[0].isupper():
                class_name = obj_name
                module_name = split_import[-3]
                subpackage_names = split_import[1:-3]
            else:
                module_name = obj_name
                subpackage_names = split_import[1:-2]

        return package_name, subpackage_names, module_name, class_name, method_name

    def set_internal_module_calls(self):
        """sets the calls for instances within the same module, no imports"""
        class_name = ''
        method_name = ''
        for item in self.call_in_module:
            module = item[0]
            caller_node = item[1]
            called_node = item[2]
            if '.' in called_node:
                check_called_name = called_node.split('.')
                if len(check_called_name) == 2:
                    class_name = check_called_name[0]
                    method_name = check_called_name[1]
            for obj in module.contains:
                # search for called method
                if obj.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                    self.create_method_call(obj, called_node, caller_node)

                # check for called method in class
                if obj.eClass.name == NodeTypes.CLASS.value:
                    found_class = obj
                    if obj.tName == class_name:
                        self.create_method_in_class_call(
                            method_name, obj, caller_node)
                    # if class name is self because both methods are in same class
                    if found_class is not None:
                        self.create_method_in_class_call(
                            method_name, found_class, caller_node)

    def create_method_in_class_call(self, method_name, class_node, caller_node):
        """
        Creates calls for methods defined in a class.

         Args:
             method_name (str?): The name of the method.
             class_node: The class node containing the method.
             caller_node: The node that is calling the method.
         """
        for method in class_node.defines:
            if method.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                self.create_method_call(method, method_name, caller_node)

    def create_method_call(self, method_node, method_name, caller_node):
        """Creates calls to a method.

         Args:
             method_node: The method node being called.
             method_name (str): The name of the method.
             caller_node: The node that is calling the method.
         """
        if method_node.signature.method.tName == method_name:
            call_check = self.get_calls(caller_node, method_node)
            if call_check is False:
                self.create_call(caller_node, method_node)

    def check_for_missing_nodes(self):
        """check_list contains all classes with method def that are created during conversion.
        They are compared to the classes with meth def found in modules in the type graph at the end,
        those not found need to be appended to a module, otherwise the meth def are missing.
        Entire modules are missing! Perhaps because only .py files are processed. They are created and appended to
        their packages, which are also created when they are not in the type graph."""
        # check if every created TClass node is in type graph
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

        # create missing modules/packages the TClass nodes belong to (from imports)
        if len(self.check_list) > 0:
            for obj in self.check_list:
                # get names of packages and modules
                ref, ty = self.get_reference_by_name(obj.tName)
                if ref is not None:
                    imported = ref.split('.')
                    # if len==1 simple import … statement, included only if import is used (in that case len>1)
                    if len(imported) > 1:
                        package_name, subpackage_names, module_name, class_name, method_name = self.set_import_names(
                            imported)
                        package_node = self.check_package_list(
                            package_name, None)
                        # (parent) package exists
                        if package_node is not None:
                            # package has no subpackages
                            if subpackage_names is None:
                                mod_found = False
                                if hasattr(package_node, 'modules'):
                                    for mod in package_node.modules:
                                        if mod.location == module_name:
                                            mod_found = True
                                    if mod_found is False:
                                        module_node = self.create_ecore_instance(
                                            NodeTypes.MODULE)
                                        module_node.location = module_name
                                        module_node.contains.append(obj)
                                        module_node.namespace = package_node
                                        self.graph.modules.append(module_node)
                            # package has subpackages
                            if subpackage_names is not None:
                                # single subpackage
                                if isinstance(subpackage_names, str):
                                    subpackage_node = self.check_package_list(
                                        subpackage_names, package_node)
                                    if subpackage_node is not None:
                                        mod_found = False
                                        if hasattr(package_node, 'modules'):
                                            for mod in package_node.modules:
                                                if mod.location == module_name:
                                                    mod_found = True
                                            if mod_found is False:
                                                self.create_missing_module(
                                                    module_name, obj, subpackage_node)
                                    if subpackage_node is None:
                                        subpackage_node = self.create_ecore_instance(
                                            NodeTypes.PACKAGE)
                                        subpackage_node.tName = subpackage_names
                                        subpackage_node.parent = package_node
                                        self.package_list.append(
                                            [subpackage_node, subpackage_names, package_node])
                                        self.create_missing_module(
                                            module_name, obj, subpackage_node)
                                # multiple subpackages
                                if isinstance(subpackage_names, list):
                                    for i, item in enumerate(subpackage_names):
                                        if i == 0:
                                            subpackage_node = self.check_package_list(
                                                item, package_node)
                                            # package hierarchy does not exist
                                            if subpackage_node is None:
                                                self.create_package_hierarchy(package_node, subpackage_names,
                                                                              lib_flag=False)
                                                # last subpackage in hierarchy is in self.imported_package
                                                self.create_missing_module(
                                                    module_name, obj, self.imported_package)
                                        # subpackages lower in hierarchy, continue searching as long as sub package exists
                                        if i > 0:
                                            subpackage_node = self.get_package_from_list_by_parent_name(
                                                subpackage_names[i - 1])
                                            # found sub package in hierarchy that does not exist yet
                                            if subpackage_node is None:
                                                missing_subpackages = subpackage_names[i:]
                                                self.create_package_hierarchy(subpackage_node, missing_subpackages,
                                                                              lib_flag=False)
                                                # last subpackage in hierarchy is in self.imported_package
                                                self.create_missing_module(
                                                    module_name, obj, self.imported_package)
                        # (parent) package does not exist
                        if package_node is None:
                            # create package and module
                            package_node = self.create_ecore_instance(
                                NodeTypes.PACKAGE)
                            package_node.tName = package_name
                            self.graph.packages.append(package_node)
                            self.package_list.append(
                                [package_node, package_name, None])
                            if subpackage_names is None:
                                self.create_missing_module(
                                    module_name, obj, package_node)
                            if subpackage_names is not None:
                                self.create_package_hierarchy(
                                    package_node, subpackage_names, lib_flag=False)
                                # last subpackage in hierarchy is in self.imported_package
                                self.create_missing_module(
                                    module_name, obj, self.imported_package)

    def create_missing_module(self, module_name, class_node, package_node):
        """
        Creates a missing module and associates it with a class and package.

        Args:
            module_name (str?): The name of the module.
            class_node: The class node to be included in the module.
            package_node: The package node to which the module belongs.
        """
        module_node = self.create_ecore_instance(NodeTypes.MODULE)
        module_node.location = module_name
        module_node.contains.append(class_node)
        module_node.namespace = package_node
        self.graph.modules.append(module_node)

    def get_e_package(self):
        """
        Retrieves the EPackage associated with the graph.

        Returns:
            The EPackage instance.
        """
        return self.e_package

    def get_graph(self):
        """
        Retrieves the graph representing the project.

        Returns:
            The graph instance.
        """
        return self.graph

    def create_ecore_instance(self, ecore_type):
        """
        Creates an Ecore instance of the specified type.

        Args:
            ecore_type: The type of the Ecore instance to create.

        Returns:
            The created Ecore instance.
        """
        return self.e_package.getEClassifier(ecore_type.value)()

    def get_current_module(self):
        """
        Retrieves the current module being processed.

        Returns:
            The current module instance.
        """
        return self.current_module

    def get_module_by_name(self, name):
        """
        Retrieves a module by its name.

        Args:
           name (str): The name of the module.

        Returns:
           The module node or None if not found.
       """
        for module in self.module_list:
            if name == module[1]:
                return module[0]
        return None

    def get_module_by_location(self, location):
        """
        Retrieves a module by its location.

        Args:
            location (str): The location of the module.

        Returns:
            The module node or None if not found.
        """
        for list_object in self.module_list:
            module = list_object[0]
            if module.location == location:
                return module
        return None

    def append_modules(self):
        """appends modules to the type graph/xmi file after every python file has been processed"""
        for module in self.module_list:
            self.graph.modules.append(module[0])

    def process_file(self, path):
        """
        Processes a single Python file, parsing its AST and converting it into a type graph.

        Args:
            path (str): The path to the Python file to process.
        """
        path = path.replace('\\', '/')
        current_package = self.get_package_by_path(path)

        # create module
        self.current_module = self.create_ecore_instance(NodeTypes.MODULE)
        self.current_module.location = path.removesuffix('.py')
        self.current_module.namespace = current_package
        path_split = self.current_module.location.replace(
            f"{self.root_directory}/", '').split('/')
        self.current_module_name = path_split[-1]
        self.module_list.append(
            [self.current_module, self.current_module_name])

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

        # added errors='ignore' to fix encoding issues in some repositories ('char-map cannot decode byte…')
        with open(path, 'r', errors='ignore') as file:
            code = file.read()
        # added following to fix some invalid character and syntax errors
        code = code.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'").replace("»", ">>").replace(
            "—", "-")
        tree = ast.parse(code)
        visitor = ASTVisitor(self)
        visitor.visit(tree)

    def get_package_by_path(self, path):
        """
        Retrieves the package node corresponding to a given file path.

        Args:
            path (str): The file path.

        Returns:
            The package node or None if not found.
        """
        package_hierarchy = path.replace(
            f"{self.root_directory}/", '').split('/')[:-1]
        parent_package = None
        package_node = None
        # first element is highest in package hierarchy
        for package_name in package_hierarchy:
            package_node = self.get_package_by_name_and_parent(
                package_name, parent_package)
            parent_package = package_node
        return package_node

    def get_package_by_name_and_parent(self, name, parent):
        """
        Retrieves or creates a package node by name and parent.

        Args:
            name (str): The name of the package.
            parent: The parent package node.

        Returns:
            The package node.
        """
        for package_node in self.graph.packages:
            return_package = self.get_package_recursive(
                package_node, name, parent)
            if return_package is not None:
                return return_package
        # checks if subpackage already exists
        my_package = self.check_package_list(name, parent)
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
        """
        Recursively searches for a package node by name and parent.

        Args:
            package_node: The starting package node for the search.
            name (str): The name of the package.
            parent: The parent package node.

        Returns:
            The found package node or None if not found.
        """
        if package_node.tName == name and package_node.parent == parent:
            return package_node
        for subpackage in package_node.subpackages:
            return self.get_package_recursive(subpackage, name, package_node)
        return None

    # this fixed the same subpackages being defined multiple times
    def check_package_list(self, package_name, parent):
        """
        Checks if a package already exists in the package list.

       Args:
           package_name (str): The name of the package.
           parent: The parent package node.

       Returns:
           The package node if found, otherwise None.
       """
        for package in self.package_list:
            if package_name == package[1]:
                if parent is None and package[2] is None:
                    return package[0]
                if parent is not None and package[2] is not None:
                    if parent.tName == package[2].tName:
                        return package[0]
        return None

    def get_package_from_list_by_parent_name(self, parent_name):
        """
        Retrieves a package from the list by its parent's name.

        Args:
            parent_name (str): The name of the parent package.

        Returns:
            The package node or None if not found.
        """
        for package in self.package_list:
            if package[2] is not None:
                if parent_name == package[2].tName:
                    return package[0]
        return None

    def get_class_from_internal_structure(self, class_name, module):
        """
        Retrieves a class from the internal structure by name and module.

        Args:
            class_name (str): The name of the class.
            module: The module to which the class belongs.

        Returns:
            The class node or None if not found.
        """
        for current_class in self.class_list:
            if class_name == current_class[1]:
                if module is None and current_class[2] is None:
                    return current_class[0]
                if hasattr(module, 'location') and hasattr(current_class[2], 'location'):
                    if module.location == current_class[2].location:
                        return current_class[0]
        return None

    def get_module_of_class(self, class_name, child_name):
        """
        Retrieves the module of a class by its name and the name of its child.

       Args:
           class_name (str): The name of the class.
           child_name (str): The name of the child class.

       Returns:
           The module node or None if not found.
       """
        for current_class in self.class_list:
            if class_name == current_class[1]:
                if hasattr(current_class[0], 'childClasses'):
                    for child in current_class[0].childClasses:
                        if child.tName == child_name:
                            # return module of parent class
                            return current_class[2]
        return None

    def get_class_by_name(self, name, structure=None, create_if_not_found=True, module=None, move_to_module=True):
        """
        Retrieves or creates a class by its name.

        Args:
            name (str): The name of the class.
            structure: The structure to search in (default is the graph's classes).
            create_if_not_found (bool): Flag indicating whether to create the class if not found.
            module: The module to which the class may belong.
            move_to_module (bool): Flag indicating whether to move the class to the module if found.

        Returns:
            The class node.
        """
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
            structure.append(class_node)  # class appended to type graph
            return class_node
        return None

    def get_reference_by_name(self, name):
        """
        Retrieves a reference by name, checking imported modules and classes (type = 0) and assigned instances (type = 1).

        Args:
            name (str): The name to look up.

        Returns:
            A tuple containing the reference and its type (0 for module, 1 for instance).
        """
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
        """
        Adds an import to the list of imports.

        Args:
            module: The module being imported.
            alias (str?): The alias for the import.
        """
        self.imports.append([module, alias])

    def add_instance(self, instance_name, class_name):
        """
        Adds an instance to the list of instances.

       Args:
           instance_name (str?): The name of the instance.
           class_name (str?): The name of the class to which the instance belongs.
       """
        reference, reference_type = self.get_reference_by_name(class_name)
        if reference is not None and reference_type == 0:
            classes = class_name.split('.')[1:]
            classes.insert(0, reference)
            class_name = ".".join(classes)
        self.instances.append([instance_name, class_name])

    def remove_instance(self, class_name):
        """
        Removes an instance from the list of instances by class name.

       Args:
           class_name (str): The name of the class whose instance should be removed.
       """
        for instance in self.instances:
            if instance[1] == class_name:
                self.instances.remove(instance)

    @staticmethod
    def get_method_def_in_class(name, class_node):
        """
        Checks if a method definition exists in a class.

        Args:
            name (str): The name of the method.
            class_node: The class node to check.

        Returns:
            The method definition node or None if not found.
        """
        for method_def in class_node.defines:
            if method_def.signature.method.tName == name:
                return method_def
        return None

    @staticmethod
    def get_method_def_in_module(method_name, module):
        """
        Checks if a method definition exists in a module.

        Args:
            method_name (str): The name of the method.
            module: The module to check.

        Returns:
            The method definition node or None if not found.
        """
        for module_object in module.contains:
            if module_object.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                if module_object.signature.method.tName == method_name:
                    return module_object
            if module_object.eClass.name == NodeTypes.CLASS.value:
                for meth in module_object.defines:
                    if meth.signature.method.tName == method_name:
                        return meth
        return None

    def get_method_def_from_internal_structure(self, method_name, module):
        """
        Retrieves a method definition from the internal structure.

       Args:
           method_name (str): The name of the method.
           module: The module to check.

       Returns:
           The method definition node or None if not found.
       """
        for current_method in self.method_list:
            if method_name == current_method[1]:
                if module is None and current_method[2] is None:
                    return current_method[0]
                if hasattr(module, 'location') and hasattr(current_method[2], 'location'):
                    if module.location == current_method[2].location:
                        return current_method[0]
        return None

    def create_method_signature(self, method_node, name, arguments):
        """
        Creates a method signature for a method definition.

        Args:
            method_node: The method definition node.
            name (str?): The name of the method.
            arguments (list?): The list of arguments for the method.
        """
        method_signature = self.create_ecore_instance(
            NodeTypes.METHOD_SIGNATURE)
        method = self.create_ecore_instance(NodeTypes.METHOD)
        method.tName = name
        self.graph.methods.append(method)
        method_signature.method = method

        previous = None
        for _ in arguments:
            parameter = self.create_ecore_instance(NodeTypes.PARAMETER)
            if previous is not None:
                parameter.previous = previous
            previous = parameter
            method_signature.parameters.append(parameter)

        method_node.signature = method_signature

        # for internal structure
        module_node = self.get_current_module()
        self.method_list.append([method_node, name, module_node])

    @staticmethod
    def get_calls(caller_node, called_node):
        """
        Checks if a call already exists between two nodes.

        Args:
            caller_node: The node making the call.
            called_node: The node being called.

        Returns:
            True if the call exists, otherwise False.
        """
        for call_object in caller_node.accessing:
            if call_object.target == called_node:
                return True
        return False

    def create_call(self, caller_node, called_node):
        """
        Creates a call between two nodes.

       Args:
           caller_node: The node making the call.
           called_node: The node being called.
       """
        call = self.create_ecore_instance(NodeTypes.CALL)
        call.source = caller_node
        call.target = called_node

    def write_xmi(self, resource_set, output_directory, repository):
        """
        Writes the graph to an XMI file.

        Args:
            resource_set (ResourceSet?): The resource set for Ecore.
            output_directory (str?): The directory for output files.
            repository (str?): The repository name for the output file.
        """
        repository_name = repository.split('\\')[-1]
        # Replace slashes in the repository name with underscores
        safe_repository_name = repository_name.replace('/', '_').replace('\\', '_')

        resource = resource_set.create_resource(URI(f'{output_directory}/{safe_repository_name}.xmi'),
                                                use_uuid=True)
        resource.append(self.graph)
        resource.save()


class ASTVisitor(ast.NodeVisitor):
    """Defines the visits of the different node types of the AST,
       ASTVisitor calls the functions of ProjectEcoreGraph to create Ecore instances."""

    def __init__(self, ecore_graph):
        """
        Initializes the ASTVisitor.

        Args:
            ecore_graph (ProjectEcoreGraph): The instance of ProjectEcoreGraph to interact with.
        """
        self.graph = ecore_graph.get_graph()
        self.ecore_graph = ecore_graph  # ProjectEcoreGraph instance
        self.current_method = None
        self.current_class = None
        self.current_indentation = 0
        self.current_module = None
        self.names_in_scope: set = set()
        self.fields_per_class: dict = dict()

    def visit_Import(self, node):
        """
        Visits an import statement in the AST.

        Args:
            node: The AST node representing the import statement.
        """
        for name in node.names:
            if name.asname is None:
                self.ecore_graph.add_import(name.name, name.name)
            else:
                self.ecore_graph.add_import(name.name, name.asname)

    def visit_ImportFrom(self, node):
        """
        Visits an import from statement in the AST.

        Args:
            node: The AST node representing the import from statement.
        """
        for name in node.names:
            if name.asname is None:
                self.ecore_graph.add_import(
                    f"{node.module}.{name.name}", name.name)
            else:
                self.ecore_graph.add_import(
                    f"{node.module}.{name.name}", name.asname)

    def create_inheritance_structure(self, node, child):
        """Creates the inheritance structure for classes.

           Args:
               node: The AST node representing the base class.
               child: The child class node being defined.

           Returns:
               The base class node or None if not found.
           """
        base_node = None
        if isinstance(node, ast.Name):
            base_node, base_type = self.ecore_graph.get_reference_by_name(node.id)
            if base_node is None:
                base_node = self.ecore_graph.get_class_by_name(
                    node.id, module=self.ecore_graph.get_current_module())
                base_node.childClasses.append(child)
            elif isinstance(base_node, str) and base_type == 0:
                import_parent = None
                for import_class in base_node.split('.'):
                    import_node = self.ecore_graph.get_class_by_name(
                        import_class)  # module is None here
                    if import_parent is not None:  # if import_node does not have parent, it becomes parent itself
                        import_parent.childClasses.append(import_node)
                    import_parent = import_node
                    base_node = import_node
                    base_node.childClasses.append(child)
        elif isinstance(node, ast.Attribute):
            base_node = self.ecore_graph.get_class_by_name(node.attr)
            base_node.childClasses.append(child)
            self.create_inheritance_structure(node.value, base_node)
        return base_node

    def visit_ClassDef(self, node):
        """
        Visits a class definition in the AST.

        Args:
            node: The AST node representing the class definition.
        """
        temp_scope = self.names_in_scope  # save previous scope in temp for later access.
        self.names_in_scope = set()

        class_name = node.name
        self.current_module = self.ecore_graph.get_current_module()
        class_node = self.ecore_graph.get_class_by_name(
            class_name, module=self.ecore_graph.get_current_module())
        temp_class = self.current_class
        self.current_class = class_node

        for base in node.bases:
            self.create_inheritance_structure(base, class_node)

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.current_indentation = item.col_offset
                method_name = item.name
                method_node = self.ecore_graph.get_method_def_in_class(
                    method_name, class_node)
                if method_node is None:
                    method_node = self.ecore_graph.create_ecore_instance(
                        NodeTypes.METHOD_DEFINITION)
                    self.ecore_graph.create_method_signature(
                        method_node, method_name, item.args.args)
                    class_node.defines.append(method_node)
                    # to search for missing meth def later
                    self.ecore_graph.check_list.append(class_node)
        self.generic_visit(node)

        self.current_class = temp_class
        self.names_in_scope = temp_scope  # Restore Scope from node before

    def visit_FunctionDef(self, node):
        """
        Visits a function definition in the AST.

        Args:
            node: The AST node representing the function definition.
        """
        # Check if Function already in Scope
        if node.name in self.names_in_scope:
            warning(f"Def {node.name} already in Scope")
        self.names_in_scope.add(node.name)
        temp_scope = self.names_in_scope # save previous scope in temp for later access.
        self.names_in_scope = set()
        temp_class, temp_method = self.current_class, self.current_method
        self.current_method = None
        if self.current_class is not None:
            self.current_method = self.ecore_graph.get_method_def_in_class(
                node.name, self.current_class)
        if self.current_method is None:

            self.current_class = None
            self.current_method = self.ecore_graph.create_ecore_instance(
                NodeTypes.METHOD_DEFINITION)
            self.ecore_graph.create_method_signature(
                self.current_method, node.name, node.args.args)
            module_node = self.ecore_graph.get_current_module()
            self.current_module = module_node
            module_node.contains.append(self.current_method)
        self.current_indentation = node.col_offset

        self.generic_visit(node)

        self.current_class,self.current_method = temp_class, temp_method # Restore current class and method

        self.names_in_scope = temp_scope # Restore Scope from node before

    def visit_Assign(self, node):
        """
        Visits an assignment statement in the AST.

       Args:
           node: The AST node representing the assignment statement.
       """
        # Find all field assignments in a class
        if self.current_class is not None:
            for target in node.targets:
                if isinstance(target,ast.Attribute):
                    if isinstance(target.value,ast.Name):
                        if target.value.id == 'self':
                            if self.current_class not in self.fields_per_class:
                                self.fields_per_class[self.current_class] = set()
                            self.fields_per_class[self.current_class].add(target.attr)
                            # Todo: Use class fields in ecore model here

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
                        self.ecore_graph.add_instance(
                            target_name[:-1], instance[:-1])
        self.generic_visit(node)

    def visit_Call(self, node):
        """
        Visits a function call in the AST.

        Args:
            node: The AST node representing the function call.
        """
        if node.col_offset <= self.current_indentation:
            self.current_method = None
            self.current_indentation = node.col_offset
        instance = ""
        instance_node = node.func

        # set caller_node
        if self.current_method is not None:
            caller_node = self.current_method
        else:
            module_node = self.ecore_graph.get_module_by_location(
                self.ecore_graph.get_current_module().location)
            self.current_module = module_node
            method_location = self.ecore_graph.get_current_module().location
            method_name = method_location.split('/')[-1]
            caller_node = self.ecore_graph.get_method_def_in_module(
                method_name, module_node)
            if caller_node is None:
                caller_node = self.ecore_graph.get_method_def_from_internal_structure(
                    method_name, module_node)
                if caller_node is None:
                    caller_node = self.ecore_graph.create_ecore_instance(
                        NodeTypes.METHOD_DEFINITION)
                    self.ecore_graph.create_method_signature(
                        caller_node, method_name, [])
                    module_node.contains.append(caller_node)

        # call node can contain different node types
        while isinstance(instance_node, ast.Attribute):
            instance = f"{instance_node.attr}.{instance}"
            instance_node = instance_node.value
        if not isinstance(instance_node, ast.Name):
            self.generic_visit(node)
            return
        instance = f"{instance_node.id}.{instance}"
        if instance.endswith('.'):
            instance = instance[:-1]

        # for calls within one module
        self.ecore_graph.call_in_module.append(
            [self.current_module, caller_node, instance])

        # for calls of imported instances, both within repo and external libraries
        instance_from_graph, instance_type = self.ecore_graph.get_reference_by_name(
            instance.replace(f".{instance.split('.')[-1]}", ''))

        # this is necessary to get all the called methods' names correctly
        if instance_from_graph is None:
            self.generic_visit(node)
            return
        instances = instance.split('.')

        # add method name to instance from graph
        instances[0] = instance_from_graph
        instance_name = ".".join(instances)

        self.ecore_graph.call_external_module.append(
            [instance_name, caller_node])

        self.generic_visit(node)
