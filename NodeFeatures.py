from enum import Enum


# node types in the type graph
class NodeTypes(Enum):
    CALL = "TCall"
    CLASS = "TClass"
    MODULE = "TModule"
    METHOD = "TMethod"
    METHOD_SIGNATURE = "TMethodSignature"
    METHOD_DEFINITION = "TMethodDefinition"
    PACKAGE = "TPackage"
    PARAMETER = "TParameter"
