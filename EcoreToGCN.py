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
            self.node_matrix.append([self.NodeLabels.PACKAGE.value, tpackage.tName])
            if hasattr(tpackage, 'subpackages'):
                for tsubpackage in tpackage.subpackages:
                    self.node_matrix.append([self.NodeLabels.PACKAGE.value, tsubpackage.tName])
                    if hasattr(tsubpackage, 'subpackages'):
                        for tsubsubpackage in tsubpackage.subpackages:
                            self.node_matrix.append([self.NodeLabels.PACKAGE.value, tsubsubpackage.tName])
        
        #convert modules and contained objects
        for tmodule in typegraph.modules:
            self.node_matrix.append([self.NodeLabels.MODULE.value, tmodule.location])
            for tobject in tmodule.contains:
                if tobject.eClass.name == ProjectEcoreGraph.Types.CLASS.value:
                    self.node_matrix.append([self.NodeLabels.CLASS.value, tobject.tName])
                if tobject.eClass.name == ProjectEcoreGraph.Types.METHOD_DEFINITION.value:
                    self.node_matrix.append([self.NodeLabels.METHOD_DEFINITION.value])
        
        #convert methods and contained objects
        for tmethod in typegraph.methods:
            self.node_matrix.append([self.NodeLabels.METHOD.value, tmethod.tName])
            for tobject in tmethod.signatures:
                self.node_matrix.append([self.NodeLabels.METHOD_SIGNATURE.value])
        
        #convert classes and contained objects
        for tclass in typegraph.classes:
            self.node_matrix.append([self.NodeLabels.CLASS.value, tclass.tName])



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