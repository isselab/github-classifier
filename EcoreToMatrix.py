from pyecore.resources import ResourceSet, URI
from enum import Enum
from ASTToEcore import ProjectEcoreGraph
from sklearn.preprocessing import LabelEncoder

class EcoreToMatrixConverter:
    def __init__(self, resource:ResourceSet):
        self.typegraph_root = resource.contents[0] #we have the entire typegraph object here
        self.node_matrix = [] #nxc feature matrix with n nodes and c features for each node: node type and identifier (e.g. name or location)
        self.node_dict = {} #internal structure to set edges later, node_id as key, value is list with type, name, object name, that's connected by edge
        self.node_count = 0 #to create id for nodes, keys in node_dict

        self.convert_nodes(self.typegraph_root)

        number_of_nodes = len(self.get_node_matrix())
        self.adjacency_list = [[] for i in range(number_of_nodes)] #empty list for every node, list will cotain edge info
        
        self.convert_edges()

        node_labels = [self.NodeTypes.PACKAGE.value, self.NodeTypes.MODULE.value, self.NodeTypes.CLASS.value, self.NodeTypes.METHOD_DEFINITION.value, self.NodeTypes.METHOD.value, self.NodeTypes.METHOD_SIGNATURE.value, self.NodeTypes.PARAMETER.value, self.NodeTypes.CALL.value]
        self.encoded_node_matrix = self.convert_labels(node_labels)

    def get_node_matrix(self):
        return self.node_matrix
    
    def get_adjacency_list(self):
        return self.adjacency_list
    
    def get_encoded_node_matrix(self):
        return self.encoded_node_matrix
    
    def get_graph_name(self):
        return self.typegraph_root.tName
    
    #this is the main function, that converts the nodes in the ecore graph into a matrix structure
    def convert_nodes(self, typegraph): 
        #convert packages and subpackages
        for tpackage in typegraph.packages:
            current_package = None
            current_subpackage = None
            current_subsubpackage = None
            current_package = self.get_node(tpackage.tName, self.NodeTypes.PACKAGE.value) #check if package is already in node matrix
            if current_package is None:
                self.node_matrix.append(self.NodeTypes.PACKAGE.value)
                self.node_dict[self.node_count] = [self.NodeTypes.PACKAGE.value, tpackage.tName]
                self.node_count += 1
                if hasattr(tpackage, 'subpackages'): 
                    for tsubpackage in tpackage.subpackages: 
                        current_subpackage = self.get_node(tsubpackage.tName, self.NodeTypes.PACKAGE.value)
                        if current_subpackage is None:
                            self.node_matrix.append(self.NodeTypes.PACKAGE.value)
                            self.node_dict[self.node_count] = [self.NodeTypes.PACKAGE.value, tsubpackage.tName, self.NodeTypes.PACKAGE.value, tpackage.tName] #save type and name for edge info
                            self.node_count += 1
                            if hasattr(tsubpackage, 'subpackages'):
                                for tsubsubpackage in tsubpackage.subpackages:
                                    current_subsubpackage = self.get_node(tsubsubpackage.tName, self.NodeTypes.PACKAGE.value)
                                    if current_subsubpackage is None:
                                        self.node_matrix.append(self.NodeTypes.PACKAGE.value)
                                        self.node_dict[self.node_count] = [self.NodeTypes.PACKAGE.value, tsubsubpackage.tName, self.NodeTypes.PACKAGE.value, tsubpackage.tName]
                                        self.node_count += 1
        
        #convert modules and contained objects
        for tmodule in typegraph.modules:
            current_module = None
            current_module = self.get_node(tmodule.location, self.NodeTypes.MODULE.value)
            if current_module is None:
                self.node_matrix.append(self.NodeTypes.MODULE.value) 
                if tmodule.namespace is not None:
                    self.node_dict[self.node_count] = [self.NodeTypes.MODULE.value, tmodule.location, self.NodeTypes.PACKAGE.value, tmodule.namespace.tName] #name of TPackage object
                    self.node_count += 1
                else:
                    self.node_dict[self.node_count] = [self.NodeTypes.MODULE.value, tmodule.location]
                    self.node_count += 1
                if hasattr(tmodule, 'contains'):
                    for tobject in tmodule.contains: #can contain TContainableElements (TAbstractType and TMember)
                    #check TAbstractTypes
                        if tobject.eClass.name == ProjectEcoreGraph.Types.CLASS.value:
                            current_class = None
                            current_class = self.get_node(tobject.tName, self.NodeTypes.CLASS.value)
                            if current_class is None:
                                self.node_matrix.append(self.NodeTypes.CLASS.value)
                                self.node_dict[self.node_count] = [self.NodeTypes.CLASS.value, tobject.tName, self.NodeTypes.MODULE.value, tmodule.location]
                                self.node_count += 1
                                if hasattr(tobject, 'childClasses'):
                                    self.convert_childClasses(tobject)
                                if hasattr(tobject, 'defines'):
                                    self.convert_defined_methods(tobject)
                        if tobject.eClass.name == ProjectEcoreGraph.Types.METHOD_DEFINITION.value:
                            #here are the TMember objects checked
                            self.convert_method_definitions(tobject, self.NodeTypes.MODULE.value, tmodule.location)
            
        
        #convert methods and contained objects
        for tmethod in typegraph.methods:
            current_method = None
            current_method = self.get_node(tmethod.tName, self.NodeTypes.METHOD.value)
            if current_method is None:
                self.node_matrix.append(self.NodeTypes.METHOD.value)
                self.node_dict[self.node_count] = [self.NodeTypes.METHOD.value, tmethod.tName]
                self.node_count += 1
                node_name = tmethod.tName
                for tobject in tmethod.signatures:
                    node_name += '_signature'
                    signature_name = node_name
                    self.node_matrix.append(self.NodeTypes.METHOD_SIGNATURE.value)
                    self.node_dict[self.node_count] = [self.NodeTypes.METHOD_SIGNATURE.value, node_name, self.NodeTypes.METHOD.value, tmethod.tName] #savig method name helps later on!!
                    self.node_count += 1
                    if hasattr(tobject, 'parameters'):
                        node_name += '_param'
                        for p,tparam in enumerate(tobject.parameters):
                            param_counter = p+1
                            current_param = str(param_counter)
                            param_name = node_name + current_param
                            
                            #check for next parameter to save info for edges later
                            if tparam.next is None:
                                self.node_matrix.append(self.NodeTypes.PARAMETER.value)
                                self.node_dict[self.node_count] = [self.NodeTypes.PARAMETER.value, param_name, self.NodeTypes.METHOD_SIGNATURE.value, signature_name] 
                                self.node_count += 1

                            if tparam.next is not None:
                                #create name of the next parameter
                                next_param_counter = param_counter+1
                                next_param = str(next_param_counter)
                                next_param_name = node_name + next_param
                                self.node_matrix.append(self.NodeTypes.PARAMETER.value)
                                self.node_dict[self.node_count] = [self.NodeTypes.PARAMETER.value, param_name, self.NodeTypes.METHOD_SIGNATURE.value, signature_name, 'Next', next_param_name] 
                                self.node_count += 1
        
        #convert classes and contained objects
        for tclass in typegraph.classes:
            current_class = None
            current_class = self.get_node(tclass.tName, self.NodeTypes.CLASS.value)
            if current_class is None:
                self.node_matrix.append(self.NodeTypes.CLASS.value)
                self.node_dict[self.node_count] = [self.NodeTypes.CLASS.value, tclass.tName] #does not have package in namespace
                self.node_count += 1
                if hasattr(tclass, 'childClasses'):
                    self.convert_childClasses(tclass)
                if hasattr(tclass, 'defines'):
                    self.convert_defined_methods(tclass)

    def convert_childClasses(self, tclass):
        for child in tclass.childClasses:
            self.node_matrix.append(self.NodeTypes.CLASS.value)
            self.node_dict[self.node_count] = [self.NodeTypes.CLASS.value, child.tName, self.NodeTypes.CLASS.value, tclass.tName]
            self.node_count += 1
            if hasattr(child, 'defines'):
                    self.convert_defined_methods(child)

    #convert TMethod objects that are defined within a class
    def convert_defined_methods(self, tclass):
        for tobject in tclass.defines:
                if tobject.eClass.name == ProjectEcoreGraph.Types.METHOD_DEFINITION.value:
                    self.convert_method_definitions(tobject, self.NodeTypes.CLASS.value, tclass.tName)

    #convert TMethodDefinition objects and contained call objects
    def convert_method_definitions(self, t_meth_def, container_type, tcontainer_name): 
        current_method_def = None
        tobject_name = t_meth_def.signature.method.tName
        tobject_name += '_definition'
        current_method_def = self.get_node(tobject_name, self.NodeTypes.METHOD_DEFINITION.value)
        if current_method_def is None:
            self.node_matrix.append(self.NodeTypes.METHOD_DEFINITION.value)
            self.node_dict[self.node_count] = [self.NodeTypes.METHOD_DEFINITION.value, tobject_name, container_type, tcontainer_name] 
            self.node_count += 1
            if hasattr(t_meth_def, 'accessing'):
                self.convert_call(t_meth_def, tobject_name)

    #convert call objects, are only contained in TMethodDefinition objects
    def convert_call(self, tmethod_def, tmethod_def_name):
        call_source = tmethod_def_name
        tmethod_def_name += '_call'
        for c,call in enumerate(tmethod_def.accessing):
            methoddef_target = call.target
            target_name = methoddef_target.signature.method.tName #name of the TMethod object that's being called
            #create a ame for the call object
            call_counter = c+1
            calls = str(call_counter)
            current_call = tmethod_def_name + calls
            self.node_matrix.append(self.NodeTypes.CALL.value)
            self.node_dict[self.node_count] = [self.NodeTypes.CALL.value, current_call, 'Source', call_source, 'Target', target_name]
            self.node_count += 1

    #this function checks if a node already exists by comparing node type and name
    def get_node(self, node_name, type):
        for current_node in self.node_dict:
            node = self.node_dict[current_node]
            if node[0] == type:
                if node[1] == node_name:
                    return current_node
        return None
    
    #this function sets the existing edges in the adjacency matrix to 1
    def convert_edges(self):
        for keys in self.node_dict:
            current_node = self.node_dict[keys]

            #set edges between packages and subpackages
            if current_node[0] == self.NodeTypes.PACKAGE.value:
                if len(current_node) == 4: #there is a subpackage
                    find_key = self.find_key_of_connected_node(self.NodeTypes.PACKAGE.value, current_node) #search for key of the parent package
                    self.adjacency_list[find_key].append(keys)

            #set edges between Modules and Packages
            if current_node[0] == self.NodeTypes.MODULE.value:
                if len(current_node) == 4:
                    if current_node[2] == self.NodeTypes.PACKAGE.value:
                        find_key = self.find_key_of_connected_node(self.NodeTypes.PACKAGE.value, current_node)
                        #edge in both directions
                        self.adjacency_list[find_key].append(keys)
                        self.adjacency_list[keys].append(find_key)

            #set edges between classes and modules
            if current_node[0] == self.NodeTypes.CLASS.value:
                if len(current_node) == 4:
                    if current_node[2] == self.NodeTypes.MODULE.value:
                        find_key = self.find_key_of_connected_node(self.NodeTypes.MODULE.value, current_node)
                        self.adjacency_list[find_key].append(keys)
                    if current_node[2] == self.NodeTypes.CLASS.value:
                        find_key = self.find_key_of_connected_node(self.NodeTypes.CLASS.value, current_node)
                        self.adjacency_list[find_key].append(keys) #edge from TClass to child class
            
            #set edges between classes/modules and method definitions
            if current_node[0] == self.NodeTypes.METHOD_DEFINITION.value:
                if len(current_node) == 4:
                    if current_node[2] == self.NodeTypes.MODULE.value:
                        find_key = self.find_key_of_connected_node(self.NodeTypes.MODULE.value, current_node)
                        self.adjacency_list[find_key].append(keys)
                    if current_node[2] == self.NodeTypes.CLASS.value:
                        find_key = self.find_key_of_connected_node(self.NodeTypes.CLASS.value, current_node)
                        self.adjacency_list[find_key].append(keys)
            
            #set edges for TMethod objects
            if current_node[0] == self.NodeTypes.METHOD_SIGNATURE.value:
                find_key = self.find_key_of_connected_node(self.NodeTypes.METHOD.value, current_node)
                self.adjacency_list[find_key].append(keys) #edge from TMethod to TMethodSignature object
            if current_node[0] == self.NodeTypes.METHOD.value:
                method_name = current_node[1]
                method_name += '_definition'
                find_key = self.find_connected_node(self.NodeTypes.METHOD_DEFINITION.value, method_name)
                self.adjacency_list[keys].append(find_key) #edge from TMethod to TMethodDef object!

            #set edges for parameters
            if current_node[0] == self.NodeTypes.PARAMETER.value:
                find_key = self.find_key_of_connected_node(self.NodeTypes.METHOD_SIGNATURE.value, current_node)
                self.adjacency_list[find_key].append(keys) #edge from TMethodSignature to TParameter
                if len(current_node) == 6: #function has multiple parameters
                    next_parameter_name = current_node[5]
                    find_key = self.find_connected_node(self.NodeTypes.PARAMETER.value, next_parameter_name)
                    #edges between next/previous parameters of one function
                    self.adjacency_list[find_key].append(keys)
                    self.adjacency_list[keys].append(find_key)

            #set edges for calls
            if current_node[0] == self.NodeTypes.CALL.value:
                find_key = self.find_key_of_connected_node(self.NodeTypes.METHOD_DEFINITION.value, current_node)
                self.adjacency_list[find_key].append(keys) #edge TMethDef to TCall, 'accessing'
                if len(current_node) == 6:
                    target_name = current_node[5] #method name that's being called
                    target_name += '_definition'
                    find_key = self.find_connected_node(self.NodeTypes.METHOD_DEFINITION.value, target_name)
                    self.adjacency_list[find_key].append(keys) #edge TMethDef to TCall, 'accessedBy'
                    self.adjacency_list[keys].append(find_key) #edge TCall to TMethDef, 'target'

    #find number of node (key), name explicitly saved in current_node
    def find_key_of_connected_node(self, type_string, current_node):
        for find_key in self.node_dict:
            find_node = self.node_dict[find_key]
            if find_node[0] == type_string:
                if find_node[1] == current_node[3]:
                    return find_key

    #find number of node (key), name not explicitly saved                
    def find_connected_node(self, type_string, node_name):
        for find_key in self.node_dict:
            find_node = self.node_dict[find_key]
            if find_node[0] == type_string:
                if find_node[1] == node_name:
                    return find_key
                
    def convert_labels(self, labels):
        label_encoder = LabelEncoder()
        label_encoder.fit(labels)
        encoded_nodes = label_encoder.transform(self.node_matrix)
        return encoded_nodes

    class NodeTypes(Enum):
        PACKAGE = "TPackage"
        MODULE = "TModule"
        CLASS = "TClass"
        METHOD_DEFINITION = "TMethodDefinition"
        METHOD_SIGNATURE = "TMethodSignature"
        METHOD = "TMethod"
        PARAMETER = "TParameter"
        CALL = "TCall"
