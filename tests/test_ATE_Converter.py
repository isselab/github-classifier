import unittest
import sys
import os

#getting the name of the directory where this file is
current = os.path.dirname(os.path.realpath(__file__))
 
#getting the parent directory name where the current directory is
parent = os.path.dirname(current)
 
#adding the parent directory to the sys.path.
sys.path.append(parent)

from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes
from test_utils import check_path_exists

class TestATEConv(unittest.TestCase):


       #buggy unit test -> missing file
    #def test_package(self):
        #repo = 'unit_tests/test_package'
        #check_path_exists(repo)
        #resource_set = ResourceSet()
        #graph = ProjectEcoreGraph(resource_set, repo, False)
        #ecore_graph = graph.get_graph()
        # original
        #self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        #self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        #self.assertEqual(ecore_graph.packages[0].tName, 'my_package', 'wrong package name')
        #self.assertEqual(len(ecore_graph.packages[0].subpackages), 0, 'package should not have subpackage')
        #self.assertEqual(len(ecore_graph.modules), 0, 'wrong number of modules')
        #self.assertEqual(len(ecore_graph.classes), 0, 'wrong number of classes')
        #self.assertEqual(len(ecore_graph.methods), 0, 'wrong number of methods')

    #buggy unit test -> missing file
    #def test_subpackage(self):
        #repo = 'unit_tests/test_subpackage'
        #check_path_exists(repo)
        #resource_set = ResourceSet()
        #graph = ProjectEcoreGraph(resource_set, repo, False)
        #ecore_graph = graph.get_graph()
        #self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        #self.assertEqual(ecore_graph.packages[0].tName, 'parent', 'wrong package name')
        #self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        #self.assertEqual(ecore_graph.packages[0].subpackages[0].tName, 'child', 'wrong submodule name')
        #self.assertEqual(ecore_graph.packages[0].subpackages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        #self.assertEqual(len(ecore_graph.modules), 0, 'wrong number of modules')
        #self.assertEqual(len(ecore_graph.classes), 0, 'wrong number of classes')
        #self.assertEqual(len(ecore_graph.methods), 0, 'wrong number of methods')

    def test_module(self):
        repo = 'unit_tests/test_module'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.modules), 1, 'wrong number of modules')
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'unit_tests/test_module/my_module', 'wrong module location')
        self.assertIsNone(ecore_graph.modules[0].namespace, 'namespace should be empty')
        self.assertEqual(len(ecore_graph.modules[0].contains), 0, 'module should not contain any')

    def test_multiple_modules(self):
        repo = 'unit_tests/test_multiple_modules'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.modules), 2, 'wrong number of modules')
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'unit_tests/test_multiple_modules/first_module', 'wrong module location')
        self.assertIsNone(ecore_graph.modules[0].namespace, 'namespace should be empty')
        self.assertEqual(len(ecore_graph.modules[0].contains), 0, 'module should not contain any')
        self.assertEqual(ecore_graph.modules[1].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[1].location, 'unit_tests/test_multiple_modules/second_module', 'wrong module location')
        self.assertIsNone(ecore_graph.modules[1].namespace, 'namespace should be empty')
        self.assertEqual(len(ecore_graph.modules[1].contains), 0, 'module should not contain any')

    def test_module_in_package(self):
        repo = 'unit_tests/test_module_in_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        self.assertEqual(len(ecore_graph.modules), 1, 'wrong number of modules')
        self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        self.assertEqual(ecore_graph.packages[0].tName, 'my_package', 'wrong package name')
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'unit_tests/test_module_in_package/my_package/my_module', 'wrong module location')
        self.assertEqual(ecore_graph.modules[0].namespace.eClass.name, NodeTypes.PACKAGE.value, 'namespace should contain package')
        self.assertEqual(ecore_graph.modules[0].namespace.tName, 'my_package', 'wrong package name')

    def test_class(self):
        repo = 'unit_tests/test_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.classes), 1, 'wrong number of classes')
        self.assertEqual(ecore_graph.classes[0].tName, 'MyTestClass', 'wrong class name')
        self.assertEqual(len(ecore_graph.modules[0].contains), 1, 'class should be contained in module')
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.CLASS.value, 'class should be in module, wrong object type')

    def test_child_class(self):
        repo = 'unit_tests/test_child_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.classes[0].childClasses), 1, 'wrong number of child classes')
        self.assertEqual(ecore_graph.classes[0].childClasses[0].tName, 'FirstChild', 'wrong name of child class')

    def test_method(self):
        repo = 'unit_tests/test_method'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.methods), 1, 'wrong number of methods')
        self.assertEqual(ecore_graph.methods[0].tName, 'my_test_method', 'wrong method name')
        self.assertEqual(ecore_graph.methods[0].eClass.name, NodeTypes.METHOD.value, 'method is wrong type')
        self.assertEqual(ecore_graph.methods[0].signatures[0].eClass.name, NodeTypes.METHOD_SIGNATURE.value, 'method signature is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'method definition is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'my_test_method', 'edge method def to method wrong')

    #test defining a method inside a class
    def test_method_in_class(self):
        repo = 'unit_tests/test_method_in_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.CLASS.value, 'class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].tName, 'MyTestClass', 'class name wrong')
        self.assertEqual(len(ecore_graph.modules[0].contains[0].defines), 1, 'class should define one method')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'method in class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].signature.method.tName, 'my_test_method', 'wrong method name')

    #test defining multiple methods inside a class
    def test_multiple_methods_in_class(self):
        repo = 'unit_tests/test_multiple_methods_in_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.CLASS.value, 'class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].tName, 'MyTestClass', 'class name wrong')
        self.assertEqual(len(ecore_graph.modules[0].contains[0].defines), 2, 'class should define two methods')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'first method in class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].signature.method.tName, 'my_test_method', 'wrong method name')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[1].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'second method in class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[1].signature.method.tName, 'my_second_method', 'wrong method name')

    def test_parameter(self):
        repo = 'unit_tests/test_parameter'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.methods[0].signatures[0].parameters), 1, 'wrong number of parameters')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].eClass.name, NodeTypes.PARAMETER.value, 'parameter is wrong type')

    def test_multiple_parameter(self):
        repo = 'unit_tests/test_multiple_parameter'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.methods[0].signatures[0].parameters), 2, 'wrong number of parameters')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].eClass.name, NodeTypes.PARAMETER.value, 'parameter is wrong type')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].next.eClass.name, NodeTypes.PARAMETER.value, 'parameter should have next parameter set')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[1].eClass.name, NodeTypes.PARAMETER.value, 'parameter is wrong type')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[1].previous.eClass.name, NodeTypes.PARAMETER.value, 'parameter should have previous parameter set')
    
    #test call of method by another method, both in same module
    def test_module_internal_method_call(self):
        repo = 'unit_tests/test_module_internal_method_call'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[1].signature.method.tName, 'caller_func', 'caller method has wrong name')
        self.assertEqual(len(ecore_graph.modules[0].contains[1].accessing), 1, 'call object is missing')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is wrong type')
        self.assertIsNotNone(ecore_graph.modules[0].contains[1].accessing[0].target, 'target is missing')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].target.signature.method.tName, 'called_func', 'target has wrong method name')

    #test importing a method from another module in the repo
    def test_internal_method_imports(self):
        repo = 'unit_tests/test_internal_method_imports'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[1].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')

    #test importing a method from a class in another module in the repo
    def test_internal_class_imports(self):
        repo = 'unit_tests/test_internal_class_imports'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[1].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'method_two', 'source method for call is wrong')
 
    #test calling a function from an imported module from another package
    def test_internal_method_imports_package(self):
        repo = 'unit_tests/test_internal_method_imports_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #test calling a function from an imported class from another package
    def test_internal_method_class_imports_package(self):
        repo = 'unit_tests/test_internal_method_class_imports_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[1].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #test call of method in a class by another method not in the class, both in same module
    def test_module_internal_class_call(self):
        repo = 'unit_tests/test_module_internal_class_call'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertIsNotNone(ecore_graph.modules[0].contains[0].defines[0].accessedBy, 'call source is missing')
        self.assertEqual(len(ecore_graph.modules[0].contains[1].accessing), 1, 'call object is missing')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].target.signature.method.tName, 'called_func', 'target has wrong name')
        self.assertEqual(ecore_graph.modules[0].contains[1].signature.method.tName, 'caller_func', 'caller method has wrong name')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is wrong type')
        self.assertIsNotNone(ecore_graph.modules[0].contains[1].accessing[0].target, 'target is missing')

    #test call of method in a class by another method, both in same class
    def test_class_internal_method_call(self):
        repo = 'unit_tests/test_class_internal_method_call'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[1].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[1].accessing[0].target.signature.method.tName, 'called_func', 'target has wrong method name')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'caller_func', 'source has wrong method name')

    #test call for method in multiple packages(subpackage)
    def test_internal_method_imports_multiple_packages(self):
        repo = 'unit_tests/test_internal_method_imports_multiple_packages'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[2].contains[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #test call for method in class in multiple packages(subpackage)
    def test_internal_method_class_imports_multiple_packages(self):
        repo = 'unit_tests/test_internal_method_class_imports_multiple_packages'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[2].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #test importing external library, one module, one method
    def test_call_external_library(self):
        repo = 'unit_tests/test_call_external_library'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.packages[0].tName, 'numpy_ExternalLibrary', 'imported library package is missing')
        self.assertEqual(ecore_graph.modules[1].namespace.tName, 'numpy_ExternalLibrary', 'imported library module and package edge wrong')
        self.assertEqual(len(ecore_graph.modules), 2, 'wrong number of modules')
        self.assertEqual(ecore_graph.modules[1].location, 'numpy_ExternalLibrary', 'imported library has wrong name')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'call object is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'array_ExternalLibrary', 'target has wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessedBy[0].source.signature.method.tName, 'one_method', 'source has wrong name')

    #test importing multiple packages/subpackages from external library
    def test_call_external_library_submodule(self):
        repo = 'unit_tests/test_call_external_library_submodule'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages), 2, 'wrong number of packages')
        self.assertEqual(ecore_graph.packages[1].tName, 'torch_geometric_ExternalLibrary', 'import with length>2 has wrong package name')
        self.assertEqual(ecore_graph.modules[2].namespace.tName, 'torch_geometric_ExternalLibrary', 'wrong modules namespace')
        self.assertEqual(ecore_graph.modules[2].contains[0].signature.method.tName, 'global_mean_pool_ExternalLibrary', 'wrong method name in imported module')
        self.assertEqual(ecore_graph.modules[2].contains[0].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'wrong object type')

    #test importing class with a method (external libraries)
    def test_call_external_library_class(self):
        repo = 'unit_tests/test_call_external_library_class'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.packages[0].tName, 'torch_ExternalLibrary', 'wrong package name for import')
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of imported packages')
        self.assertEqual(len(ecore_graph.packages[0].subpackages), 1, 'subpackage wrong number')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].tName, 'utils_ExternalLibrary', 'subpackages wrong name')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].parent.tName, 'torch_ExternalLibrary', 'parent package wrong')
        self.assertEqual(len(ecore_graph.modules), 2, 'wrong umber of modules')
        self.assertEqual(ecore_graph.modules[1].location, 'data_ExternalLibrary', 'imported module from external library has wrong name')
        self.assertEqual(len(ecore_graph.modules[1].contains), 2, 'wrong number of imported methods/classes')
        self.assertEqual(ecore_graph.modules[1].contains[0].signature.method.tName, 'Dataset_ExternalLibrary', 'method wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'call is missing')
        self.assertEqual(ecore_graph.modules[1].contains[1].eClass.name, NodeTypes.CLASS.value, 'class is missing')
        self.assertEqual(ecore_graph.modules[1].contains[1].tName, 'Dataset', 'class has wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[1].tLib, True, 'flag for imported class from external library not set to true')
        self.assertEqual(ecore_graph.modules[1].contains[1].defines[0].signature.method.tName, '__len___ExternalLibrary', 'method in class has wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[1].defines[0].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'call is missing')

    #test importing class with multiple methods (external libraries)
    def test_call_external_library_class_multiple_methods(self):
        repo = 'unit_tests/test_call_external_library_class_multiple_methods'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[1].contains[1].defines[1].signature.method.tName, '__getitem___ExternalLibrary', 'second class method has wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[1].defines[1].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'call is missing')
 
    #test importing multiple methods in one module (external libraries)
    def test_call_external_library_multiple_methods(self):
        repo = 'unit_tests/test_call_external_library_multiple_methods'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[1].contains[1].signature.method.tName, 'max_ExternalLibrary', 'second method in imported module wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[1].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'call is missing')

    #test imported packages (and subpackages) with multiple modules (external libraries)
    def test_call_external_library_multiple_modules_same_package(self):
        repo = 'unit_tests/test_call_external_library_multiple_modules_same_package'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.modules), 3, 'wrong number of modules')
        self.assertEqual(ecore_graph.modules[1].namespace.tName, 'utils_ExternalLibrary', 'wrong subpackage name in imported module')
        self.assertEqual(ecore_graph.modules[2].namespace.tName, 'utils_ExternalLibrary', 'wrong subpackage name in imported module')
        self.assertEqual(ecore_graph.modules[2].location, 'benchmark_ExternalLibrary', 'wrong name for imported module')
        self.assertEqual(ecore_graph.modules[2].contains[0].signature.method.tName, 'Timer_ExternalLibrary', 'wrong method name in imported module')
        self.assertEqual(ecore_graph.modules[2].contains[0].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'call is missing')

    #test imported packages with multiple subpackages (external libraries)
    def test_call_external_library_multiple_subpackages(self):
        repo = 'unit_tests/test_call_external_library_multiple_subpackages'
        check_path_exists(repo)
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages[0].subpackages), 2, 'wrong number of subpackages')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].tName, 'utils_ExternalLibrary', 'wrong subpackage name')
        self.assertEqual(ecore_graph.packages[0].subpackages[1].tName, 'cuda_ExternalLibrary', 'wrong subpackage name')
        self.assertEqual(ecore_graph.modules[2].location, 'random_ExternalLibrary', 'wrong module location in second subpackage')
        self.assertEqual(ecore_graph.modules[2].contains[0].signature.method.tName, 'Tensor_ExternalLibrary', 'wrong method name in module in second subpackage')
        self.assertEqual(ecore_graph.modules[2].contains[0].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'call is missing')

if __name__ == "__main__":
    unittest.main()