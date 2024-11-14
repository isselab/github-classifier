from enum import Enum


# types of relations between nodes in the type graph
class EdgeTypes(Enum):
    """
     Enum representing the types of relations between nodes in a type graph.

     This enumeration defines various types of edges that can exist between nodes,
    providing a structured way to represent connections in a type graph. Each member
    corresponds to a specific type of relationship, facilitating the understanding
    and manipulation of the graph's structure.
     """
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
