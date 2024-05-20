from enum import Enum

#recursively count number of packages
def count_packages(package, count):
    for subpackage in package.subpackages:
        count += 1
        if hasattr(subpackage, 'subpackages'):
              count = count_packages(subpackage, count)
    return count

def count_calls(method_definition, count_call):
    for call_obj in method_definition.accessing:
        count_call += 1
    return count_call

#programm entities in metamodel
class Types(Enum):
    CALL = "TCall"
    CLASS = "TClass"
    FIELD = "TField"
    MODULE = "TModule"
    METHOD = "TMethod"
    METHOD_SIGNATURE = "TMethodSignature"
    METHOD_DEFINITION = "TMethodDefinition"
    PACKAGE = "TPackage"
    PARAMETER = "TParameter"
    