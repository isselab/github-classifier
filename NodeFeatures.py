from enum import Enum


# node types in the type graph
class NodeTypes(Enum):
    """
       Enum representing different types of nodes in a type graph.

       Each node type corresponds to a specific element in the type system,
       providing a way to categorize and manage these elements programmatically.
       """
    # TPackage
    PACKAGE = "TPackage"
    # TModule
    MODULE = "TModule"
    # TClass
    CLASS = "TClass"
    # TMethod
    METHOD = "TMethod"
    METHOD_SIGNATURE = "TMethodSignature"
    METHOD_DEFINITION = "TMethodDefinition"
    PARAMETER = "TParameter"
    # TField
    FIELD = "TField"
    FIELD_SIGNATURE = "TFieldSignature" # Todo implement this in AstToEcoreConverter (only missing TFieldSignature.type)
    FIELD_DEFINITION = "TFieldDefinition" # Todo implement this in AstToEcoreConverter (missing TFieldDefinition.hidden and ".hiddenBy)
    # TAccess
    CALL = "TCall"
    READ = "TRead"  # Todo implement this in AstToEcoreConverter
    WRITE = "TWrite"  # Todo implement this in AstToEcoreConverter
    READ_WRITE = "TReadWrite"  # Todo implement this in AstToEcoreConverter
    #TInterface
    INTERFACE = "TInterface"
    # In Python, there is no formal concept of interfaces as found in some other programming languages like Java or C#.
    # However, Python supports a similar concept through the use of abstract base classes (ABCs) and duck typing.
    # The return on investment probably is not sufficient to justify the implementation.
