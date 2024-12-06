import hashlib

import numpy as np
from pyecore.resources import ResourceSet

from EdgeAttributes import EdgeTypes
from Encoder import one_hot_encoding
from NodeFeatures import NodeTypes


class EcoreToMatrixConverter:
    """
    A converter that transforms an Ecore model into a matrix representation.

    This class takes an Ecore model represented as a resource set and converts it into
    a matrix format suitable for further analysis or processing. The conversion includes
    extracting nodes and edges, encoding them into numerical values, and writing the
    output to a CSV file if specified.

    Attributes:
        typegraph_root (Resource): The root of the type graph extracted from the resource set.
        node_matrix (list): A list containing the feature node types.
        adjacency_list (list): A sparse edge matrix represented as pairs of node IDs.
        node_dict (dict): A mapping of node IDs to their connections, including type, name, and object name.
        node_count (int): A counter to generate unique IDs for nodes.
        hashed_names (list): A list of hashed node names using MD5.
        edge_attributes (list): A list of types of relationships between nodes.
        library_flag (list): Flags indicating whether nodes are from an external library or a repository.
        encoded_node_matrix (list): A matrix of one-hot encoded node features.
        encoded_lib_flags (list): A matrix of one-hot encoded library flags.
        encoded_edge_attributes (list): A matrix of one-hot encoded edge attributes.
        node_features (list): A combined representation of node features for output.

    Args:
        resource (ResourceSet): The input resource set containing the Ecore model.
        write_in_file (bool): Flag indicating whether to write the output to a file.
        output_folder (str, optional): The folder where the output file will be saved. Defaults to None.
    """

    def __init__(self, resource: ResourceSet, write_in_file, output_folder=None):
        """
        Initializes the EcoreToMatrixConverter with the provided resource set.

        Args:
            resource (ResourceSet): The input resource set containing the Ecore model.
            write_in_file (bool): Flag indicating whether to write the output to a file.
            output_folder (str, optional): The folder where the output file will be saved. Defaults to None.
        """
        if write_in_file is True:
            self.typegraph_root = resource.contents[0]
        else:
            self.typegraph_root = resource

        self.node_matrix = []  # contains the feature node types
        self.adjacency_list = []  # sparse edge matrix, entries: [node_id1, node_id2]
        self.node_dict = {}  # internal structure to set edges later, node_id is key, value is list with type, name, and object name, that it is connected to with an edge
        self.node_count = 0  # to create id for nodes
        self.hashed_names = []  # contains node names hashed with md5
        self.edge_attributes = []  # contains type of relationship between nodes
        self.library_flag = []  # flags for nodes in graph

        self.convert_nodes(self.typegraph_root)
        self.convert_edges()

        # True if object is from external library, False when from repository
        library_flags = ['true', 'false']

        node_labels = [NodeTypes.PACKAGE.value, NodeTypes.MODULE.value, NodeTypes.CLASS.value,
                       NodeTypes.METHOD_DEFINITION.value,
                       NodeTypes.METHOD.value, NodeTypes.METHOD_SIGNATURE.value, NodeTypes.PARAMETER.value,
                       NodeTypes.CALL.value]

        edge_labels = [EdgeTypes.ACCESSEDBY.value, EdgeTypes.ACCESSING.value, EdgeTypes.CHILDCLASSES.value,
                       EdgeTypes.CONTAINS.value,
                       EdgeTypes.DEFINES.value, EdgeTypes.DEFINITIONS.value, EdgeTypes.MODULES.value,
                       EdgeTypes.NAMESPACE.value, EdgeTypes.NEXT.value,
                       EdgeTypes.PARAMETERS.value, EdgeTypes.PREVIOUS.value, EdgeTypes.SIGNATURES.value,
                       EdgeTypes.SOURCE.value, EdgeTypes.SUBPACKAGE.value,
                       EdgeTypes.TARGET.value, EdgeTypes.PARENT.value, EdgeTypes.PARENTCLASSES.value]

        # encode features to numerical values
        self.encoded_node_matrix = one_hot_encoding(
            node_labels, self.node_matrix)
        self.encoded_lib_flags = one_hot_encoding(
            library_flags, self.library_flag)

        if len(self.edge_attributes) > 0:
            self.encoded_edge_attributes = one_hot_encoding(
                edge_labels, self.edge_attributes)

        # combine node features into single matrix for output
        features = zip(self.encoded_node_matrix,
                       self.hashed_names, self.encoded_lib_flags)
        self.node_features = self.combine_node_features(features)

        output_name = self.get_graph_name()
        if write_in_file is True:
            if output_folder is not None:
                self.write_csv(output_folder, output_name)
            else:
                print('output directory is required!')
        print(f'{output_name} \n')

    def get_node_matrix(self):
        """returns sparse matrix containing the node types as strings"""
        return self.node_matrix

    def get_encoded_node_matrix(self):
        """returns sparse matrix containing the one hot encoded node types"""
        return self.encoded_node_matrix

    def get_hashed_names(self):
        """returns node names hashed with md5, hexadecimal encoded"""
        return self.hashed_names

    def get_external_library_flags(self):
        """returns flags for external libraries as strings"""
        return self.library_flag

    def get_encoded_library_flags(self):
        """returns one hot encoded flags for external libraries"""
        return self.encoded_lib_flags

    def get_node_features(self):
        """returns all the node features: (ohe enc) node types, hashed names, and (ohe enc) library flags"""
        return self.node_features

    def get_adjacency_list(self):
        """returns sparse edge matrix, E=[number of edges, 2]"""
        return self.adjacency_list

    def get_edge_attributes(self):
        """returns list of edge attributes as strings"""
        return self.edge_attributes

    def get_encoded_edge_attributes(self):
        """returns list of one hot encoded edge attributes"""
        return self.encoded_edge_attributes

    def get_graph_name(self):
        """Returns the name of the graph."""
        return self.typegraph_root.tName

    @staticmethod
    def combine_node_features(features):
        """
        Combines encoded node types, hashed names, and library flags into one feature array per node.

        Args:
            features (iterable): An iterable containing tuples of (encoded node types, hashed names, library flags).

        Returns:
            list: A list of combined feature arrays for each node.
        """
        feature_list = list(features)
        combined_list = []
        for arr, hash_name, flag in feature_list:
            arr = np.append(arr, hash_name)
            arr = np.append(arr, flag)
            combined_list.append(arr)
        return combined_list

    def convert_nodes(self, typegraph):
        """
        Converts the nodes in the Ecore graph into a matrix structure. Used as main func in the code.

        This method saves the node types in a list, hashes the node names with MD5, and sets the library flags.

        Args:
            typegraph (Resource): The type graph to convert nodes from.
        """
        # convert packages and subpackages
        for t_package in typegraph.packages:
            current_package = self.get_node(
                t_package.tName, NodeTypes.PACKAGE.value)
            # if package exists but has length 4 it was a subpackage --> different package, same name
            if current_package is None or len(current_package) == 4:
                self.node_matrix.append(NodeTypes.PACKAGE.value)
                self.node_dict[self.node_count] = [
                    NodeTypes.PACKAGE.value, t_package.tName]
                if '_ExternalLibrary' in t_package.tName:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(t_package.tName.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(t_package, 'subpackages'):
                    self.convert_subpackages_recursive(t_package)

        # convert modules and contained objects
        for t_module in typegraph.modules:
            current_module = self.get_node(
                t_module.location, NodeTypes.MODULE.value)
            if current_module is None:
                self.node_matrix.append(NodeTypes.MODULE.value)
                if '_ExternalLibrary' in t_module.location:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(t_module.location.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                if t_module.namespace is not None:
                    self.node_dict[self.node_count] = [NodeTypes.MODULE.value, t_module.location,
                                                       NodeTypes.PACKAGE.value,
                                                       t_module.namespace.tName]  # name of TPackage object
                else:
                    self.node_dict[self.node_count] = [
                        NodeTypes.MODULE.value, t_module.location]
                self.node_count += 1
                if hasattr(t_module, 'contains'):
                    # can contain TContainableElements (TAbstractType and TMember)
                    for t_object in t_module.contains:
                        if t_object.eClass.name == NodeTypes.CLASS.value:
                            current_class = self.get_node(
                                t_object.tName, NodeTypes.CLASS.value)
                            if current_class is None:
                                self.node_matrix.append(NodeTypes.CLASS.value)
                                self.node_dict[self.node_count] = [NodeTypes.CLASS.value, t_object.tName,
                                                                   NodeTypes.MODULE.value, t_module.location]
                                if hasattr(t_object, 'tLib'):
                                    if t_object.tLib is True:
                                        self.library_flag.append('true')
                                    else:
                                        self.library_flag.append('false')
                                else:
                                    self.library_flag.append('false')
                                hashed_name = hashlib.md5(
                                    t_object.tName.encode('utf-8'))
                                self.hashed_names.append(
                                    hashed_name.hexdigest())
                                self.node_count += 1
                                if hasattr(t_object, 'childClasses'):
                                    self.convert_child_classes(t_object)
                                if hasattr(t_object, 'defines'):
                                    self.convert_defined_methods(t_object)
                        if t_object.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                            self.convert_method_definitions(
                                t_object, NodeTypes.MODULE.value, t_module.location)

        # convert methods and contained objects
        for t_method in typegraph.methods:
            self.node_matrix.append(NodeTypes.METHOD.value)
            self.node_dict[self.node_count] = [
                NodeTypes.METHOD.value, t_method.tName]
            if '_ExternalLibrary' in t_method.tName:
                self.library_flag.append('true')
            else:
                self.library_flag.append('false')
            hashed_name = hashlib.md5(t_method.tName.encode('utf-8'))
            self.hashed_names.append(hashed_name.hexdigest())
            self.node_count += 1
            node_name = t_method.tName
            for t_object in t_method.signatures:
                node_name += '_signature'
                signature_name = node_name
                self.node_matrix.append(NodeTypes.METHOD_SIGNATURE.value)
                self.node_dict[self.node_count] = [NodeTypes.METHOD_SIGNATURE.value, node_name, NodeTypes.METHOD.value,
                                                   t_method.tName]
                if '_ExternalLibrary' in node_name:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(node_name.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(t_object, 'parameters'):
                    node_name += '_param'
                    for p, t_param in enumerate(t_object.parameters):
                        param_counter = p + 1
                        current_param = str(param_counter)
                        param_name = node_name + current_param

                        # check for next parameter to save info for edges later
                        if t_param.next is None:
                            self.node_matrix.append(NodeTypes.PARAMETER.value)
                            self.node_dict[self.node_count] = [NodeTypes.PARAMETER.value, param_name,
                                                               NodeTypes.METHOD_SIGNATURE.value, signature_name]
                            # if signature was from an imported external library, its parameters are too
                            if '_ExternalLibrary' in param_name:
                                self.library_flag.append('true')
                            else:
                                self.library_flag.append('false')
                            hashed_name = hashlib.md5(
                                param_name.encode('utf-8'))
                            self.hashed_names.append(hashed_name.hexdigest())
                            self.node_count += 1

                        if t_param.next is not None:
                            # create name of the next parameter
                            next_param_counter = param_counter + 1
                            next_param = str(next_param_counter)
                            next_param_name = node_name + next_param
                            self.node_matrix.append(NodeTypes.PARAMETER.value)
                            self.node_dict[self.node_count] = [NodeTypes.PARAMETER.value, param_name,
                                                               NodeTypes.METHOD_SIGNATURE.value, signature_name, 'Next',
                                                               next_param_name]
                            if '_ExternalLibrary' in param_name:
                                self.library_flag.append('true')
                            else:
                                self.library_flag.append('false')
                            hashed_name = hashlib.md5(
                                param_name.encode('utf-8'))
                            self.hashed_names.append(hashed_name.hexdigest())
                            self.node_count += 1

        # convert classes and contained objects
        for t_class in typegraph.classes:
            current_class = self.get_node(t_class.tName, NodeTypes.CLASS.value)
            if current_class is None:
                self.node_matrix.append(NodeTypes.CLASS.value)
                self.node_dict[self.node_count] = [
                    NodeTypes.CLASS.value, t_class.tName]
                # TClass objects have an extra Flag, instead of checking via name
                if hasattr(t_class, 'tLib'):
                    if t_class.tLib is True:
                        self.library_flag.append('true')
                    else:
                        self.library_flag.append('false')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(t_class.tName.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(t_class, 'childClasses'):
                    self.convert_child_classes(t_class)
                if hasattr(t_class, 'defines'):
                    self.convert_defined_methods(t_class)

    def convert_subpackages_recursive(self, t_package):
        """
        Recursively converts subpackages of a given package into the node matrix.

        Args:
            t_package: The package to convert subpackages from.
        """
        for t_subpackage in t_package.subpackages:
            current_subpackage = self.get_node_in_container(t_subpackage.tName, NodeTypes.PACKAGE.value, t_package.tName,
                                                            NodeTypes.PACKAGE.value)
            if current_subpackage is None:
                self.node_matrix.append(NodeTypes.PACKAGE.value)
                self.node_dict[self.node_count] = [NodeTypes.PACKAGE.value, t_subpackage.tName, NodeTypes.PACKAGE.value,
                                                   t_package.tName]  # save type and name for edge info
                if '_ExternalLibrary' in t_subpackage.tName:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(t_subpackage.tName.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(t_subpackage, 'subpackages'):
                    self.convert_subpackages_recursive(t_subpackage)

    # classes have only one attribute childClasses
    # checking recursively will result in potential endless loop, without these child classes existing in the xmi file
    def convert_child_classes(self, t_class):
        """
        Converts child classes of a given class into the node matrix.

        Args:
            t_class: The class to convert child classes from.
        """
        for child in t_class.childClasses:
            self.node_matrix.append(NodeTypes.CLASS.value)
            self.node_dict[self.node_count] = [
                NodeTypes.CLASS.value, child.tName, NodeTypes.CLASS.value, t_class.tName]
            if hasattr(child, 'tLib'):
                if child.tLib is True:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
            else:
                self.library_flag.append('false')
            hashed_name = hashlib.md5(child.tName.encode('utf-8'))
            self.hashed_names.append(hashed_name.hexdigest())
            self.node_count += 1
            if hasattr(child, 'defines'):
                self.convert_defined_methods(child)

    def convert_defined_methods(self, t_class):
        """
        Converts TMethod objects that are defined within a class.

        Args:
            t_class: The class containing defined methods to convert.
        """
        for t_object in t_class.defines:
            if t_object.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                self.convert_method_definitions(
                    t_object, NodeTypes.CLASS.value, t_class.tName)

    def convert_method_definitions(self, t_meth_def, container_type, t_container_name):
        """
        Converts TMethodDefinition objects and contained call objects.

        Args:
            t_meth_def: The method definition to convert.
            container_type: The type of the container (e.g., class or module).
            t_container_name: The name of the container.
        """
        t_object_name = t_meth_def.signature.method.tName
        t_object_name += '_definition'
        self.node_matrix.append(NodeTypes.METHOD_DEFINITION.value)
        self.node_dict[self.node_count] = [NodeTypes.METHOD_DEFINITION.value, t_object_name, container_type,
                                           t_container_name]
        if '_ExternalLibrary' in t_object_name:
            self.library_flag.append('true')
        else:
            self.library_flag.append('false')
        hashed_name = hashlib.md5(t_object_name.encode('utf-8'))
        self.hashed_names.append(hashed_name.hexdigest())
        self.node_count += 1
        if hasattr(t_meth_def, 'accessing'):
            self.convert_call(t_meth_def, t_object_name)

    def convert_call(self, t_method_def, t_method_def_name):
        """
        Converts call objects contained in TMethodDefinition objects.

        Args:
            t_method_def: The method definition containing call objects.
            t_method_def_name: The name of the method definition.
        """
        call_source = t_method_def_name
        t_method_def_name += '_call'
        for c, call in enumerate(t_method_def.accessing):
            method_def_target = call.target
            if method_def_target is not None:
                # name of the TMethod object that's being called
                target_name = method_def_target.signature.method.tName
                # create a name for the call object
                call_counter = c + 1
                calls = str(call_counter)
                current_call = t_method_def_name + calls
                self.node_matrix.append(NodeTypes.CALL.value)
                self.node_dict[self.node_count] = [NodeTypes.CALL.value, current_call, 'Source', call_source, 'Target',
                                                   target_name]
                # if the target is imported from an external library, set flag for call object to true
                if '_ExternalLibrary' in target_name:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(current_call.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1

    def get_node(self, node_name, node_type):
        """
        Checks if a node already exists by comparing node type and name.

        Args:
            node_name (str): The name of the node to check.
            node_type (str): The type of the node to check.

        Returns:
            The node if it exists, otherwise None.
        """
        for current_node in self.node_dict:
            node = self.node_dict[current_node]
            if node[0] == node_type:
                if node[1] == node_name:
                    return node
        return None

    def get_node_in_container(self, node_name, node_type, parent_name, parent_type):
        """
        Checks for nodes with the same name but different parents/container objects.

        Args:
            node_name (str): The name of the node to check.
            node_type (str): The type of the node to check.
            parent_name (str): The name of the parent/container.
            parent_type (str): The type of the parent/container.

        Returns:
            The node if it exists, otherwise None.
        """
        for current_node in self.node_dict:
            node = self.node_dict[current_node]
            if len(node) >= 4:
                if node[0] == node_type:
                    if node[1] == node_name:
                        if node[2] == parent_type:
                            if node[3] == parent_name:
                                return node
        return None

    def convert_edges(self):
        """
        Sets the existing edges, appending the node IDs of connected nodes to the sparse edge matrix.

        This method also saves the type of relationship between the nodes in an extra list of edge attributes.
        """
        for keys in self.node_dict:
            current_node = self.node_dict[keys]

            # set edges between packages and subpackages
            if current_node[0] == NodeTypes.PACKAGE.value:
                if len(current_node) == 4:
                    find_key = self.find_key_of_connected_node(NodeTypes.PACKAGE.value,
                                                               current_node)  # search for key of the parent package
                    if find_key is not None:
                        # package to subpackage
                        self.edge_attributes.append(EdgeTypes.SUBPACKAGE.value)
                        self.adjacency_list.append([find_key, keys])
                        # subpackage to parent package
                        self.edge_attributes.append(EdgeTypes.PARENT.value)
                        self.adjacency_list.append([keys, find_key])

            # set edges between modules and packages
            if current_node[0] == NodeTypes.MODULE.value:
                if len(current_node) == 4:
                    if current_node[2] == NodeTypes.PACKAGE.value:
                        find_key = self.find_key_of_connected_node(
                            NodeTypes.PACKAGE.value, current_node)
                        if find_key is not None:
                            # package to module
                            self.edge_attributes.append(
                                EdgeTypes.MODULES.value)
                            self.adjacency_list.append([find_key, keys])
                            # module to package
                            self.edge_attributes.append(
                                EdgeTypes.NAMESPACE.value)
                            self.adjacency_list.append([keys, find_key])

            # set edges between classes and modules/child classes
            if current_node[0] == NodeTypes.CLASS.value:
                if len(current_node) == 4:
                    if current_node[2] == NodeTypes.MODULE.value:
                        find_key = self.find_key_of_connected_node(
                            NodeTypes.MODULE.value, current_node)
                        if find_key is not None:
                            self.edge_attributes.append(
                                EdgeTypes.CONTAINS.value)
                            self.adjacency_list.append([find_key, keys])
                    if current_node[2] == NodeTypes.CLASS.value:
                        find_key = self.find_key_of_connected_node(
                            NodeTypes.CLASS.value, current_node)
                        if find_key is not None:
                            # class to child class
                            self.edge_attributes.append(
                                EdgeTypes.CHILDCLASSES.value)
                            self.adjacency_list.append([find_key, keys])
                            # child to parent class
                            self.edge_attributes.append(
                                EdgeTypes.PARENTCLASSES.value)
                            self.adjacency_list.append([keys, find_key])

            # set edges between classes/modules and method definitions
            if current_node[0] == NodeTypes.METHOD_DEFINITION.value:
                if len(current_node) == 4:
                    if current_node[2] == NodeTypes.MODULE.value:
                        find_key = self.find_key_of_connected_node(
                            NodeTypes.MODULE.value, current_node)
                        if find_key is not None:
                            self.edge_attributes.append(
                                EdgeTypes.CONTAINS.value)
                            self.adjacency_list.append([find_key, keys])
                    if current_node[2] == NodeTypes.CLASS.value:
                        find_key = self.find_key_of_connected_node(
                            NodeTypes.CLASS.value, current_node)
                        if find_key is not None:
                            self.edge_attributes.append(
                                EdgeTypes.DEFINES.value)
                            self.adjacency_list.append([find_key, keys])

            # set edges for TMethod nodes
            if current_node[0] == NodeTypes.METHOD_SIGNATURE.value:
                find_key = self.find_key_of_connected_node(
                    NodeTypes.METHOD.value, current_node)
                if find_key is not None:
                    # TMethod to TMethodSignature node
                    self.edge_attributes.append(EdgeTypes.SIGNATURES.value)
                    self.adjacency_list.append([find_key, keys])
            if current_node[0] == NodeTypes.METHOD.value:
                method_name = current_node[1]
                method_name += '_definition'
                find_key = self.find_connected_node(
                    NodeTypes.METHOD_DEFINITION.value, method_name)
                if find_key is not None:
                    # TMethod to TMethodDef node
                    self.edge_attributes.append(EdgeTypes.DEFINITIONS.value)
                    self.adjacency_list.append([keys, find_key])

            # set edges for parameters
            if current_node[0] == NodeTypes.PARAMETER.value:
                find_key = self.find_key_of_connected_node(
                    NodeTypes.METHOD_SIGNATURE.value, current_node)
                if find_key is not None:
                    # TMethodSignature to TParameter
                    self.edge_attributes.append(EdgeTypes.PARAMETERS.value)
                    self.adjacency_list.append([find_key, keys])
                if len(current_node) == 6:
                    next_parameter_name = current_node[5]
                    find_key = self.find_connected_node(
                        NodeTypes.PARAMETER.value, next_parameter_name)
                    if find_key is not None:
                        # edges between next/previous parameters of one function
                        self.edge_attributes.append(EdgeTypes.NEXT.value)
                        self.adjacency_list.append([keys, find_key])
                        self.edge_attributes.append(EdgeTypes.PREVIOUS.value)
                        self.adjacency_list.append([find_key, keys])

                        # set edges for calls
            if current_node[0] == NodeTypes.CALL.value:
                find_key = self.find_key_of_connected_node(
                    NodeTypes.METHOD_DEFINITION.value, current_node)
                if find_key is not None:
                    # TMethDef to TCall, 'accessing'
                    self.edge_attributes.append(EdgeTypes.ACCESSING.value)
                    self.adjacency_list.append([find_key, keys])
                    # TCall to TMethDef, 'source'
                    self.edge_attributes.append(EdgeTypes.SOURCE.value)
                    self.adjacency_list.append([keys, find_key])
                if len(current_node) == 6:
                    target_name = current_node[5]
                    target_name += '_definition'
                    find_key = self.find_connected_node(
                        NodeTypes.METHOD_DEFINITION.value, target_name)
                    if find_key is not None:
                        # TMethDef to TCall, 'accessedBy'
                        self.edge_attributes.append(EdgeTypes.ACCESSEDBY.value)
                        self.adjacency_list.append([find_key, keys])
                        # TCall to TMethDef, 'target'
                        self.edge_attributes.append(EdgeTypes.TARGET.value)
                        self.adjacency_list.append([keys, find_key])

    def find_key_of_connected_node(self, type_string, current_node):
        """
        Finds the key of a node by comparing its type and name.

        Args:
            type_string (str): The type of the node to find.
            current_node: The current node to compare against.

        Returns:
            The key of the connected node if found, otherwise None.
        """
        for find_key in self.node_dict:
            find_node = self.node_dict[find_key]
            if find_node[0] == type_string:
                if find_node[1] == current_node[3]:
                    return find_key
        return None

    def find_connected_node(self, type_string, node_name):
        """
        Finds the key of a node by its type and name.

        Args:
            type_string (str): The type of the node to find.
            node_name (str): The name of the node to find.

        Returns:
            The key of the connected node if found, otherwise None.
        """
        for find_key in self.node_dict:
            find_node = self.node_dict[find_key]
            if find_node[0] == type_string:
                if find_node[1] == node_name:
                    return find_key
        return None

    def write_csv(self, output_folder, output_name):
        """
        Writes the graph data to three CSV files.

        Args:
            output_folder (str): The folder where the output files will be saved.
            output_name (str): The base name for the output files.
        """
        new_resource_nodes = open(
            f"{output_folder}/{output_name}_nodefeatures.csv", "w+")
        new_resource_edges = open(f"{output_folder}/{output_name}_A.csv", "w+")

        for node in self.node_features:
            node_counter = 1
            for item in node:
                if node_counter < len(node):
                    new_resource_nodes.write("%s, " % item)
                    node_counter += 1
                else:
                    new_resource_nodes.write("%s" % item)
            new_resource_nodes.write("\n")

        # edge is array with two entries: [node_id1, node_id2]
        for edge in self.adjacency_list:
            edge_counter = 1
            for item in edge:
                if edge_counter < len(edge):
                    new_resource_edges.write("%s, " % item)
                    edge_counter += 1
                else:
                    new_resource_edges.write("%s" % item)
            new_resource_edges.write("\n")

        if hasattr(self, 'encoded_edge_attributes'):
            new_resource_edge_attr = open(
                f"{output_folder}/{output_name}_edge_attributes.csv", "w+")
            for attr in self.encoded_edge_attributes:
                attr_counter = 1
                for item in attr:
                    if attr_counter < len(attr):
                        new_resource_edge_attr.write("%s, " % item)
                        attr_counter += 1
                    else:
                        new_resource_edge_attr.write("%s" % item)
                new_resource_edge_attr.write("\n")
            new_resource_edge_attr.close()

        new_resource_nodes.close()
        new_resource_edges.close()
