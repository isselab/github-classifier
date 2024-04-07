from pyecore.resources import ResourceSet, URI
from enum import Enum
from ASTToEcore import ProjectEcoreGraph

class xmiToGcnConverter:
    def __init__(self, resource:ResourceSet):
        self.typegraph_root = resource.contents[0] #we have the entire typegraph object here
        self.node_matrix = [] #nxc feature matrix with n nodes and c features for each node: node type and identifier (e.g. name or location)
        self.adjacency_matrix = [] #weighted graph edges

        self.convert_nodes(self.typegraph_root)
        #print(self.node_matrix)

    def get_node_matrix(self):
        return self.node_matrix
    
    def get_adjacency_matrix(self):
        return self.adjacency_matrix
    
    def get_graph_name(self):
        return self.typegraph_root.tName
    
    def convert_nodes(self, typegraph):
        #convert packages and subpackages
        for tpackage in typegraph.packages:
            current_package = None
            current_subpackage = None
            current_subsubpackage = None
            current_package = self.get_node(tpackage.tName, self.NodeLabels.PACKAGE.value) #necessary because too many objects in xmi file
            if current_package is None:
                self.node_matrix.append([self.NodeLabels.PACKAGE.value, tpackage.tName])
                if hasattr(tpackage, 'subpackages'): 
                    for tsubpackage in tpackage.subpackages: 
                        current_subpackage = self.get_node(tsubpackage.tName, self.NodeLabels.PACKAGE.value)
                        if current_subpackage is None:
                            self.node_matrix.append([self.NodeLabels.PACKAGE.value, tsubpackage.tName])
                            if hasattr(tsubpackage, 'subpackages'):
                                for tsubsubpackage in tsubpackage.subpackages:
                                    current_subsubpackage = self.get_node(tsubsubpackage.tName, self.NodeLabels.PACKAGE.value)
                                    if current_subsubpackage is None:
                                        self.node_matrix.append([self.NodeLabels.PACKAGE.value, tsubsubpackage.tName])
        
        #convert modules and contained objects
        for tmodule in typegraph.modules:
            current_module = None
            current_module = self.get_node(tmodule.location, self.NodeLabels.MODULE.value)
            if current_module is None:
                self.node_matrix.append([self.NodeLabels.MODULE.value, tmodule.location]) #maybe only use last element of location as name?
                if hasattr(tmodule, 'contains'):
                    for tobject in tmodule.contains: #can contain TContainableElements (TAbstractType and TMember)
                    #check TAbstractTypes
                        if tobject.eClass.name == ProjectEcoreGraph.Types.CLASS.value:
                            current_class = None
                            current_class = self.get_node(tobject.tName, self.NodeLabels.CLASS.value)
                            if current_class is None:
                                self.node_matrix.append([self.NodeLabels.CLASS.value, tobject.tName])
                                if hasattr(tobject, 'childClasses'):
                                    self.convert_childClasses(tobject)
                                if hasattr(tobject, 'defines'):
                                    self.convert_defined_methods(tobject)
                        if tobject.eClass.name == ProjectEcoreGraph.Types.METHOD_DEFINITION.value:
                                current_method_def = None
                                tobject_name = tobject.signature.method.tName
                                tobject_name += '_definition'
                                current_method_def = self.get_node(tobject_name, self.NodeLabels.METHOD_DEFINITION.value)
                                if current_method_def is None:
                                    self.node_matrix.append([self.NodeLabels.METHOD_DEFINITION.value, tobject_name])
            
        
        #convert methods and contained objects
        for tmethod in typegraph.methods:
            current_method = None
            current_method = self.get_node(tmethod.tName, self.NodeLabels.METHOD.value)
            if current_method is None:
                self.node_matrix.append([self.NodeLabels.METHOD.value, tmethod.tName])
                node_name = tmethod.tName
                for tobject in tmethod.signatures:
                    node_name += '_signature'
                    self.node_matrix.append([self.NodeLabels.METHOD_SIGNATURE.value, node_name])
                    if hasattr(tobject, 'parameters'):
                        node_name += '_param'
                        for p,tparam in enumerate(tobject.parameters):
                            param_counter = p+1
                            current_param = str(param_counter)
                            param_name = node_name + current_param
                            self.node_matrix.append([self.NodeLabels.PARAMETER.value, param_name])
        
        #convert classes and contained objects
        for tclass in typegraph.classes:
            current_class = None
            current_class = self.get_node(tclass.tName, self.NodeLabels.CLASS.value)
            if current_class is None:
                self.node_matrix.append([self.NodeLabels.CLASS.value, tclass.tName])
                if hasattr(tclass, 'childClasses'):
                    self.convert_childClasses(tclass)
                if hasattr(tclass, 'defines'):
                    self.convert_defined_methods(tclass)

    def convert_childClasses(self, tclass):
        for child in tclass.childClasses:
            self.node_matrix.append([self.NodeLabels.CLASS.value, child.tName])
            if hasattr(child, 'defines'):
                    self.convert_defined_methods(child)

    def convert_defined_methods(self, tclass):
        for tobject in tclass.defines:
                if tobject.eClass.name == ProjectEcoreGraph.Types.METHOD_DEFINITION.value:
                    current_method_def = None
                    tobject_name = tobject.signature.method.tName
                    tobject_name += '_definition'
                    current_method_def = self.get_node(tobject_name, self.NodeLabels.METHOD_DEFINITION.value)
                    if current_method_def is None:
                        self.node_matrix.append([self.NodeLabels.METHOD_DEFINITION.value, tobject_name])

    #this function checks if a node already exists by comparing both features
    def get_node(self, node_name, type):
        for current_node in self.node_matrix:
            if node_name == current_node[1]:
                if type == current_node[0]:
                    return current_node
        return None

    class NodeLabels(Enum):
        PACKAGE = 1
        MODULE = 2
        CLASS = 3
        METHOD_DEFINITION = 4
        METHOD_SIGNATURE = 5
        METHOD = 6
        PARAMETER = 7
        CALL = 8

    class EdgeLabels(Enum):
        UNLABELED = 1
        CONTAINS = 2
        DEFINES = 3
        ACCESSING = 4
        CHILDCLASSES = 5
        NEXT = 6
        PREVIOUS = 7
        TARGET = 8
        SOURCE = 9