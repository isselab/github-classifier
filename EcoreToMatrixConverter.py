from pyecore.resources import ResourceSet
from Encoder import one_hot_encoding
from NodeFeatures import NodeTypes
import hashlib
import numpy as np
from EdgeAttributes import EdgeTypes

class EcoreToMatrixConverter:
    def __init__(self, resource: ResourceSet, write_in_file, output_folder=None):
        if write_in_file is True:
            self.typegraph_root = resource.contents[0]
        else:
            self.typegraph_root = resource
        #nxc feature matrix with n nodes and c features for each node: node type and identifier (e.g. name or location)
        self.node_matrix = []
        self.adjacency_list = []
        self.node_dict = {}  #internal structure to set edges later, node_id as key, value is list with type, name, object name, that's connected by edge
        self.node_count = 0  #to create id for nodes, keys in node_dict
        self.hashed_names = [] #contains hashed node names
        self.edge_attributes = [] #contains type of relationship between nodes
        self.library_flag = [] #True if object is from external library, False when from repository

        self.convert_nodes(self.typegraph_root)
        self.convert_edges()
        
        library_flags = ['true', 'false']

        node_labels = [NodeTypes.PACKAGE.value, NodeTypes.MODULE.value, NodeTypes.CLASS.value, NodeTypes.METHOD_DEFINITION.value, 
                       NodeTypes.METHOD.value, NodeTypes.METHOD_SIGNATURE.value, NodeTypes.PARAMETER.value, NodeTypes.CALL.value]
        
        edge_labels = [EdgeTypes.ACCESSEDBY.value, EdgeTypes.ACCESSING.value, EdgeTypes.CHILDCLASSES.value, EdgeTypes.CONTAINS.value,
                       EdgeTypes.DEFINES.value, EdgeTypes.DEFINITIONS.value, EdgeTypes.MODULES.value, EdgeTypes.NAMESPACE.value, EdgeTypes.NEXT.value,
                       EdgeTypes.PARAMETERS.value, EdgeTypes.PREVIOUS.value, EdgeTypes.SIGNATURES.value, EdgeTypes.SOURCE.value, EdgeTypes.SUBPACKAGE.value, 
                       EdgeTypes.TARGET.value]
        
        self.encoded_node_matrix = one_hot_encoding(node_labels, self.node_matrix)
        self.encoded_lib_flags = one_hot_encoding(library_flags, self.library_flag)

        if len(self.edge_attributes)>0:
            self.encoded_edge_attributes = one_hot_encoding(edge_labels, self.edge_attributes)

        features = zip(self.encoded_node_matrix, self.hashed_names, self.encoded_lib_flags)
        self.node_features = self.combine_node_features(features)

        output_name = self.get_graph_name()
        if write_in_file is True:
            if output_folder is not None:
                self.write_csv(output_folder, output_name)
                print(f'{output_name}')
            else:
                print('output directory is required!')
 
    '''returns sparse matrix containing the node types'''
    def get_node_matrix(self):
        return self.node_matrix
    
    '''returns sparse matrix containing the one hot encoded node types'''
    def get_encoded_node_matrix(self):
        return self.encoded_node_matrix
    
    '''returns node names hashed with sha 256, utf-8 encoded'''
    def get_hashed_names(self):
        return self.hashed_names
    
    '''returns flags for external libraries'''
    def get_external_library_flags(self):
        return self.library_flag
    
    '''returns one hot encoded flags for external libraries'''
    def get_encoded_library_flags(self):
        return self.encoded_lib_flags
    
    '''returns all of the node features: (ohe enc) node types and hashed names'''
    def get_node_features(self):
        return self.node_features

    '''returns sparse adjacency matrix, [node_id, node_id]'''
    def get_adjacency_list(self):
        return self.adjacency_list
    
    '''returns list of edge attributes'''
    def get_edge_attributes(self):
        return self.edge_attributes
    
    '''returns list of one hot encoded edge attributes'''
    def get_encoded_edge_attributes(self):
        return self.encoded_edge_attributes
    
    def get_graph_name(self):
        return self.typegraph_root.tName
    
    '''adds enc node types, hashed names, and library flags in one feature array per node'''
    def combine_node_features(self, features):
        feature_list = list(features)
        combined_list = []
        for arr, hash, flag in feature_list:
            arr = np.append(arr, hash)
            arr = np.append(arr, flag)
            combined_list.append(arr)
        return combined_list

    '''this is the main function, that converts the nodes in the ecore graph into a matrix structure
    it saves the node types in a list, and hashes the nodes names with md5 and saves the hex hash in a list'''
    def convert_nodes(self, typegraph):

        #convert packages and subpackages
        for tpackage in typegraph.packages:
            current_package = None
            current_package = self.get_node(tpackage.tName, NodeTypes.PACKAGE.value)
            #if package exists but has length 4 it was a subpackage --> different package, same name
            if current_package is None or len(current_package) == 4:
                self.node_matrix.append(NodeTypes.PACKAGE.value)
                self.node_dict[self.node_count] = [NodeTypes.PACKAGE.value, tpackage.tName]
                if '_ExternalLibrary' in tpackage.tName:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(tpackage.tName.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(tpackage, 'subpackages'):
                    self.convert_subpackages_recursive(tpackage)

        #convert modules and contained objects
        for tmodule in typegraph.modules:
            current_module = None
            current_module = self.get_node(tmodule.location, NodeTypes.MODULE.value)
            
            if current_module is None:
                self.node_matrix.append(NodeTypes.MODULE.value)
                if '_ExternalLibrary' in tmodule.location:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(tmodule.location.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                if tmodule.namespace is not None:
                    self.node_dict[self.node_count] = [NodeTypes.MODULE.value, tmodule.location, NodeTypes.PACKAGE.value, tmodule.namespace.tName]  # name of TPackage object
                else:
                    self.node_dict[self.node_count] = [NodeTypes.MODULE.value, tmodule.location]
                self.node_count += 1
                if hasattr(tmodule, 'contains'):
                    #can contain TContainableElements (TAbstractType and TMember)
                    current_class = None
                    for tobject in tmodule.contains:
                        if tobject.eClass.name == NodeTypes.CLASS.value:
                            current_class = self.get_node(tobject.tName, NodeTypes.CLASS.value)
                            if current_class is None:
                                self.node_matrix.append(NodeTypes.CLASS.value)
                                self.node_dict[self.node_count] = [NodeTypes.CLASS.value, tobject.tName, NodeTypes.MODULE.value, tmodule.location]
                                if hasattr(tobject, 'tLib'):
                                    if tobject.tLib is True:
                                        self.library_flag.append('true')
                                    else:
                                        self.library_flag.append('false')
                                else:
                                    self.library_flag.append('false')
                                hashed_name = hashlib.md5(tobject.tName.encode('utf-8'))
                                self.hashed_names.append(hashed_name.hexdigest())
                                self.node_count += 1
                                if hasattr(tobject, 'childClasses'):
                                    self.convert_childClasses(tobject)
                                if hasattr(tobject, 'defines'):
                                    self.convert_defined_methods(tobject)
                        if tobject.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                            self.convert_method_definitions(tobject, NodeTypes.MODULE.value, tmodule.location)

        #convert methods and contained objects
        for tmethod in typegraph.methods:
            self.node_matrix.append(NodeTypes.METHOD.value)
            self.node_dict[self.node_count] = [NodeTypes.METHOD.value, tmethod.tName]
            if '_ExternalLibrary' in tmethod.tName:
                self.library_flag.append('true')
            else:
                self.library_flag.append('false')
            hashed_name = hashlib.md5(tmethod.tName.encode('utf-8'))
            self.hashed_names.append(hashed_name.hexdigest())
            self.node_count += 1
            node_name = tmethod.tName
            for tobject in tmethod.signatures:
                node_name += '_signature'
                signature_name = node_name
                self.node_matrix.append(NodeTypes.METHOD_SIGNATURE.value)
                self.node_dict[self.node_count] = [NodeTypes.METHOD_SIGNATURE.value, node_name, NodeTypes.METHOD.value, tmethod.tName]
                if '_ExternalLibrary' in node_name:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(node_name.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(tobject, 'parameters'):
                    node_name += '_param'
                    for p, tparam in enumerate(tobject.parameters):
                        param_counter = p+1
                        current_param = str(param_counter)
                        param_name = node_name + current_param

                        #check for next parameter to save info for edges later
                        if tparam.next is None:
                            self.node_matrix.append(NodeTypes.PARAMETER.value)
                            self.node_dict[self.node_count] = [NodeTypes.PARAMETER.value, param_name, NodeTypes.METHOD_SIGNATURE.value, signature_name]
                            #if signature was from an imported external library, its parameters are too
                            if '_ExternalLibrary' in param_name:
                                self.library_flag.append('true')
                            else:
                                self.library_flag.append('false')
                            hashed_name = hashlib.md5(param_name.encode('utf-8'))
                            self.hashed_names.append(hashed_name.hexdigest())
                            self.node_count += 1

                        if tparam.next is not None:
                            #create name of the next parameter
                            next_param_counter = param_counter+1
                            next_param = str(next_param_counter)
                            next_param_name = node_name + next_param
                            self.node_matrix.append(NodeTypes.PARAMETER.value)
                            self.node_dict[self.node_count] = [NodeTypes.PARAMETER.value, param_name, NodeTypes.METHOD_SIGNATURE.value, signature_name, 'Next', next_param_name]
                            if '_ExternalLibrary' in param_name:
                                self.library_flag.append('true')
                            else:
                                self.library_flag.append('false')
                            hashed_name = hashlib.md5(param_name.encode('utf-8'))
                            self.hashed_names.append(hashed_name.hexdigest())
                            self.node_count += 1

        #convert classes and contained objects
        for tclass in typegraph.classes:
            current_class = None
            current_class = self.get_node(tclass.tName, NodeTypes.CLASS.value)
            if current_class is None:
                self.node_matrix.append(NodeTypes.CLASS.value)
                self.node_dict[self.node_count] = [NodeTypes.CLASS.value, tclass.tName]
                #TClass objects have extra flag, instead of checking via name
                if hasattr(tclass, 'tLib'):
                    if tclass.tLib is True:
                        self.library_flag.append('true')
                    else:
                        self.library_flag.append('false')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(tclass.tName.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(tclass, 'childClasses'):
                    self.convert_childClasses(tclass)
                if hasattr(tclass, 'defines'):
                    self.convert_defined_methods(tclass)

    def convert_subpackages_recursive(self, tpackage):
        for tsubpackage in tpackage.subpackages:
            current_subpackage = self.get_node_in_container(tsubpackage.tName, NodeTypes.PACKAGE.value, tpackage.tName, NodeTypes.PACKAGE.value)
            if current_subpackage is None:
                self.node_matrix.append(NodeTypes.PACKAGE.value)
                self.node_dict[self.node_count] = [NodeTypes.PACKAGE.value, tsubpackage.tName, NodeTypes.PACKAGE.value, tpackage.tName]  # save type and name for edge info
                if '_ExternalLibrary' in tsubpackage.tName:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(tsubpackage.tName.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1
                if hasattr(tsubpackage, 'subpackages'):
                    self.convert_subpackages_recursive(tsubpackage)

    '''has only one attribute childclasses checking recursively will result 
        in potential endless loop, without these child classes existing in the xmi file'''
    def convert_childClasses(self, tclass):
        for child in tclass.childClasses:
            self.node_matrix.append(NodeTypes.CLASS.value)
            self.node_dict[self.node_count] = [NodeTypes.CLASS.value, child.tName, NodeTypes.CLASS.value, tclass.tName]
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

    '''convert TMethod objects that are defined within a class'''
    def convert_defined_methods(self, tclass):
        for tobject in tclass.defines:
            if tobject.eClass.name == NodeTypes.METHOD_DEFINITION.value:
                self.convert_method_definitions(tobject, NodeTypes.CLASS.value, tclass.tName)

    '''convert TMethodDefinition objects and contained call objects'''
    def convert_method_definitions(self, t_meth_def, container_type, tcontainer_name):
        tobject_name = t_meth_def.signature.method.tName
        tobject_name += '_definition'
        self.node_matrix.append(NodeTypes.METHOD_DEFINITION.value)
        self.node_dict[self.node_count] = [NodeTypes.METHOD_DEFINITION.value, tobject_name, container_type, tcontainer_name]
        if '_ExternalLibrary' in tobject_name:
            self.library_flag.append('true')
        else:
            self.library_flag.append('false')
        hashed_name = hashlib.md5(tobject_name.encode('utf-8'))
        self.hashed_names.append(hashed_name.hexdigest())
        self.node_count += 1
        if hasattr(t_meth_def, 'accessing'):
            self.convert_call(t_meth_def, tobject_name)

    '''convert call objects, are only contained in TMethodDefinition objects'''
    def convert_call(self, tmethod_def, tmethod_def_name):
        call_source = tmethod_def_name
        tmethod_def_name += '_call'
        for c, call in enumerate(tmethod_def.accessing):
            methoddef_target = call.target
            if methoddef_target is not None:
                #name of the TMethod object that's being called
                target_name = methoddef_target.signature.method.tName
                #create a name for the call object
                call_counter = c+1
                calls = str(call_counter)
                current_call = tmethod_def_name + calls
                self.node_matrix.append(NodeTypes.CALL.value)
                self.node_dict[self.node_count] = [NodeTypes.CALL.value, current_call, 'Source', call_source, 'Target', target_name]
                #if the target is imported from an external library, set flag for call object to true
                if '_ExternalLibrary' in target_name:
                    self.library_flag.append('true')
                else:
                    self.library_flag.append('false')
                hashed_name = hashlib.md5(current_call.encode('utf-8'))
                self.hashed_names.append(hashed_name.hexdigest())
                self.node_count += 1

    '''checks if a node already exists by comparing node type and name'''
    def get_node(self, node_name, type):
        for current_node in self.node_dict:
            node = self.node_dict[current_node]
            if node[0] == type:
                if node[1] == node_name:
                    return node

    '''necessary for objects with the same name but different parents/container objects'''
    def get_node_in_container(self, node_name, type, parent_name, parent_type):
        for current_node in self.node_dict:
            node = self.node_dict[current_node]
            if len(node) >= 4:
                if node[0] == type:
                    if node[1] == node_name:
                        if node[2] == parent_type:
                            if node[3] == parent_name:
                                return node

    '''this function sets the existing edges, it appends the node_ids of the nodes connected 
    by an edge to the adjacency list, it saves the type of relationship between the nodes, 
    e.g. "contains", in an extra list'''
    def convert_edges(self):
        for keys in self.node_dict:
            current_node = self.node_dict[keys]

            #set edges between packages and subpackages
            if current_node[0] == NodeTypes.PACKAGE.value:
                if len(current_node) == 4:
                    find_key = self.find_key_of_connected_node(NodeTypes.PACKAGE.value, current_node)  # search for key of the parent package
                    if find_key is not None:
                        self.edge_attributes.append(EdgeTypes.SUBPACKAGE.value)
                        self.adjacency_list.append([find_key, keys])

            #set edges between modules and packages
            if current_node[0] == NodeTypes.MODULE.value:
                if len(current_node) == 4:
                    if current_node[2] == NodeTypes.PACKAGE.value:
                        find_key = self.find_key_of_connected_node(NodeTypes.PACKAGE.value, current_node)
                        if find_key is not None:
                            #edge in both directions
                            #package to module
                            self.edge_attributes.append(EdgeTypes.MODULES.value)
                            self.adjacency_list.append([find_key, keys])
                            #module to package
                            self.edge_attributes.append(EdgeTypes.NAMESPACE.value)
                            self.adjacency_list.append([keys, find_key])

            #set edges between classes and modules/child classes
            if current_node[0] == NodeTypes.CLASS.value:
                if len(current_node) == 4:
                    if current_node[2] == NodeTypes.MODULE.value:
                        find_key = self.find_key_of_connected_node(NodeTypes.MODULE.value, current_node)
                        if find_key is not None:
                            self.edge_attributes.append(EdgeTypes.CONTAINS.value)
                            self.adjacency_list.append([find_key, keys])
                    if current_node[2] == NodeTypes.CLASS.value:
                        find_key = self.find_key_of_connected_node(NodeTypes.CLASS.value, current_node)
                        if find_key is not None:
                            #edge from class to child class
                            self.edge_attributes.append(EdgeTypes.CHILDCLASSES.value)
                            self.adjacency_list.append([find_key, keys])

            #set edges between classes/modules and method definitions
            if current_node[0] == NodeTypes.METHOD_DEFINITION.value:
                if len(current_node) == 4:
                    if current_node[2] == NodeTypes.MODULE.value:
                        find_key = self.find_key_of_connected_node(NodeTypes.MODULE.value, current_node)
                        if find_key is not None:
                            self.edge_attributes.append(EdgeTypes.CONTAINS.value)
                            self.adjacency_list.append([find_key, keys])
                    if current_node[2] == NodeTypes.CLASS.value:
                        find_key = self.find_key_of_connected_node(NodeTypes.CLASS.value, current_node)
                        if find_key is not None:
                            self.edge_attributes.append(EdgeTypes.DEFINES.value)
                            self.adjacency_list.append([find_key, keys])

            #set edges for TMethod objects
            if current_node[0] == NodeTypes.METHOD_SIGNATURE.value:
                find_key = self.find_key_of_connected_node(NodeTypes.METHOD.value, current_node)
                if find_key is not None:
                    #edge from TMethod to TMethodSignature object
                    self.edge_attributes.append(EdgeTypes.SIGNATURES.value)
                    self.adjacency_list.append([find_key, keys])
            if current_node[0] == NodeTypes.METHOD.value:
                method_name = current_node[1]
                method_name += '_definition'
                find_key = self.find_connected_node(NodeTypes.METHOD_DEFINITION.value, method_name)
                if find_key is not None:
                    #edge from TMethod to TMethodDef object
                    self.edge_attributes.append(EdgeTypes.DEFINITIONS.value)
                    self.adjacency_list.append([keys, find_key])

            #set edges for parameters
            if current_node[0] == NodeTypes.PARAMETER.value:
                find_key = self.find_key_of_connected_node(NodeTypes.METHOD_SIGNATURE.value, current_node)
                if find_key is not None:
                    #edge from TMethodSignature to TParameter
                    self.edge_attributes.append(EdgeTypes.PARAMETERS.value)
                    self.adjacency_list.append([find_key, keys])
                if len(current_node) == 6:
                    next_parameter_name = current_node[5]
                    find_key = self.find_connected_node(NodeTypes.PARAMETER.value, next_parameter_name)
                    if find_key is not None:
                        #edges between next/previous parameters of one function
                        self.edge_attributes.append(EdgeTypes.NEXT.value)
                        self.adjacency_list.append([keys, find_key])
                        self.edge_attributes.append(EdgeTypes.PREVIOUS.value)
                        self.adjacency_list.append([find_key, keys])           

            #set edges for calls
            if current_node[0] == NodeTypes.CALL.value:
                find_key = self.find_key_of_connected_node(NodeTypes.METHOD_DEFINITION.value, current_node)
                if find_key is not None:
                    #edge TMethDef to TCall, 'accessing'
                    self.edge_attributes.append(EdgeTypes.ACCESSING.value)
                    self.adjacency_list.append([find_key, keys])
                    #edge TCall to TMethDef, 'source'
                    self.edge_attributes.append(EdgeTypes.SOURCE.value)
                    self.adjacency_list.append([keys, find_key])
                if len(current_node) == 6:
                    target_name = current_node[5]
                    target_name += '_definition'
                    find_key = self.find_connected_node(NodeTypes.METHOD_DEFINITION.value, target_name)
                    if find_key is not None:
                        #edge TMethDef to TCall, 'accessedBy'
                        self.edge_attributes.append(EdgeTypes.ACCESSEDBY.value)
                        self.adjacency_list.append([find_key, keys])
                        #edge TCall to TMethDef, 'target'
                        self.edge_attributes.append(EdgeTypes.TARGET.value)
                        self.adjacency_list.append([keys, find_key])

    '''find number of node (key), name explicitly saved in current_node'''
    def find_key_of_connected_node(self, type_string, current_node):
        for find_key in self.node_dict:
            find_node = self.node_dict[find_key]
            if find_node[0] == type_string:
                if find_node[1] == current_node[3]:
                    return find_key
        return None

    '''find number of node (key), name not explicitly saved'''
    def find_connected_node(self, type_string, node_name):
        for find_key in self.node_dict:
            find_node = self.node_dict[find_key]
            if find_node[0] == type_string:
                if find_node[1] == node_name:
                    return find_key
        return None

    '''write graph in two csv files'''
    def write_csv(self, output_folder, output_name):
        new_resource_nodes = open(f"{output_folder}/{output_name}_nodefeatures.csv", "w+")
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

        #edge is array with two entries [node_id, node_id]
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
            new_resource_edge_attr = open(f"{output_folder}/{output_name}_edge_attributes.csv", "w+")
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
        
