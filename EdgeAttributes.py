from enum import Enum

#types of relations between nodes in the type graph
class EdgeTypes(Enum):
    PARENT = "parent"
    SUBPACKAGE = "subpackage"
    MODULES = "modules"
    NAMESPACE = "namespace"
    PARENTCLASSES = "parentClasses"
    CHILDCLASSES = "childClasses"
    CONTAINS = "contains"
    DEFINES = "defines"
    SIGNATURES = "signatures"
    DEFINITIONS = "definitions"
    PARAMETERS = "parameters"
    NEXT = "next"
    PREVIOUS = "previous"
    ACCESSING = "accessing"
    ACCESSEDBY = "accessedBy"
    TARGET = "target"
    SOURCE = "source"