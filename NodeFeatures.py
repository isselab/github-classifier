from enum import Enum


# node types in the type graph
class NodeTypes(Enum):
    """
       Enum representing different types of nodes in a type graph.

       Each node type corresponds to a specific element in the type system,
       providing a way to categorize and manage these elements programmatically.
       """
    CALL = "TCall"
    CLASS = "TClass"
    MODULE = "TModule"
    METHOD = "TMethod"
    METHOD_SIGNATURE = "TMethodSignature"
    METHOD_DEFINITION = "TMethodDefinition"
    PACKAGE = "TPackage"
    PARAMETER = "TParameter"
