import unittest
from AstToEcoreConverter import ProjectEcoreGraph
from pyecore.resources import ResourceSet
from NodeFeatures import NodeTypes

class TestATEConv(unittest.TestCase):

    def test_package(self):
        repo = 'tests/unit_tests/test_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        self.assertEqual(ecore_graph.packages[0].tName, 'my_package', 'wrong package name')
        self.assertEqual(len(ecore_graph.packages[0].subpackages), 0, 'package should not have subpackage')
        self.assertEqual(len(ecore_graph.modules), 0, 'wrong number of modules')
        self.assertEqual(len(ecore_graph.classes), 0, 'wrong number of classes')
        self.assertEqual(len(ecore_graph.methods), 0, 'wrong number of methods')

    def test_subpackage(self):
        repo = 'tests/unit_tests/test_subpackage'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        self.assertEqual(ecore_graph.packages[0].tName, 'parent', 'wrog package name')
        self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].tName, 'child', 'wrong submodule name')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        self.assertEqual(len(ecore_graph.modules), 0, 'wrong number of modules')
        self.assertEqual(len(ecore_graph.classes), 0, 'wrong number of classes')
        self.assertEqual(len(ecore_graph.methods), 0, 'wrong number of methods')

    def test_module(self):
        repo = 'tests/unit_tests/test_module'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.modules), 1, 'wrong number of modules')
        #print(ecore_graph.modules[0].tAnnotation)
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'tests/unit_tests/test_module/my_module', 'wrong module location')
        self.assertIsNone(ecore_graph.modules[0].namespace, 'namespace should be empty')
        self.assertEqual(len(ecore_graph.modules[0].contains), 0, 'module should not contain any')

    def test_multiple_modules(self):
        repo = 'tests/unit_tests/test_multiple_modules'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.modules), 2, 'wrong number of modules')
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'tests/unit_tests/test_multiple_modules/first_module', 'wrong module location')
        self.assertIsNone(ecore_graph.modules[0].namespace, 'namespace should be empty')
        self.assertEqual(len(ecore_graph.modules[0].contains), 0, 'module should not contain any')
        self.assertEqual(ecore_graph.modules[1].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[1].location, 'tests/unit_tests/test_multiple_modules/second_module', 'wrong module location')
        self.assertIsNone(ecore_graph.modules[1].namespace, 'namespace should be empty')
        self.assertEqual(len(ecore_graph.modules[1].contains), 0, 'module should not contain any')

    def test_module_in_package(self):
        repo = 'tests/unit_tests/test_module_in_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of packages')
        self.assertEqual(len(ecore_graph.modules), 1, 'wrong number of modules')
        self.assertEqual(ecore_graph.packages[0].eClass.name, NodeTypes.PACKAGE.value, 'package is wrong type')
        self.assertEqual(ecore_graph.packages[0].tName, 'my_package', 'wrong package name')
        self.assertEqual(ecore_graph.modules[0].eClass.name, NodeTypes.MODULE.value, 'module is wrong type')
        self.assertEqual(ecore_graph.modules[0].location, 'tests/unit_tests/test_module_in_package/my_package/my_module', 'wrong module location')
        self.assertEqual(ecore_graph.modules[0].namespace.eClass.name, NodeTypes.PACKAGE.value, 'namespace should contain package')
        self.assertEqual(ecore_graph.modules[0].namespace.tName, 'my_package', 'wrong package name')

    def test_class(self):
        repo = 'tests/unit_tests/test_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.classes), 1, 'wrong number of classes')
        self.assertEqual(ecore_graph.classes[0].tName, 'MyTestClass', 'wrong class name')
        self.assertEqual(len(ecore_graph.modules[0].contains), 1, 'class should be contained in module')
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.CLASS.value, 'class should be in module, wrong object type')

    def test_method(self):
        repo = 'tests/unit_tests/test_method'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.methods), 1, 'wrong number of methods')
        self.assertEqual(ecore_graph.methods[0].tName, 'my_test_method', 'wrong method name')
        self.assertEqual(ecore_graph.methods[0].eClass.name, NodeTypes.METHOD.value, 'method is wrong type')
        self.assertEqual(ecore_graph.methods[0].signatures[0].eClass.name, NodeTypes.METHOD_SIGNATURE.value, 'method signature is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'method definition is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'my_test_method', 'edge method def to method wrong')

    def test_parameter(self):
        repo = 'tests/unit_tests/test_parameter'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.methods[0].signatures[0].parameters), 1, 'wrong number of parameters')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].eClass.name, NodeTypes.PARAMETER.value, 'parameter is wrong type')

    def test_multiple_parameter(self):
        repo = 'tests/unit_tests/test_multiple_parameter'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.methods[0].signatures[0].parameters), 2, 'wrong number of parameters')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].eClass.name, NodeTypes.PARAMETER.value, 'parameter is wrong type')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[0].next.eClass.name, NodeTypes.PARAMETER.value, 'parameter should have next parameter set')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[1].eClass.name, NodeTypes.PARAMETER.value, 'parameter is wrong type')
        self.assertEqual(ecore_graph.methods[0].signatures[0].parameters[1].previous.eClass.name, NodeTypes.PARAMETER.value, 'parameter should have previous parameter set')
    
    #check call of method by another method, both in same module
    def test_module_internal_method_call(self):
        repo = 'tests/unit_tests/test_module_internal_method_call'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[1].signature.method.tName, 'caller_func', 'caller method has wrong name')
        self.assertEqual(len(ecore_graph.modules[0].contains[1].accessing), 1, 'call object is missing')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is wrong type')
        self.assertIsNotNone(ecore_graph.modules[0].contains[1].accessing[0].target, 'target is missing')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].target.signature.method.tName, 'called_func', 'target has wrong method name')

    def test_method_in_class(self):
        repo = 'tests/unit_tests/test_method_in_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].eClass.name, NodeTypes.CLASS.value, 'class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].tName, 'MyTestClass', 'class ame wrong')
        self.assertEqual(len(ecore_graph.modules[0].contains[0].defines), 1, 'class should define one method')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].eClass.name, NodeTypes.METHOD_DEFINITION.value, 'method in class is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].signature.method.tName, 'my_test_method', 'wrong method name')

    def test_internal_method_imports(self):
        repo = 'tests/unit_tests/test_internal_method_imports'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[1].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')

    def test_internal_class_imports(self):
        repo = 'tests/unit_tests/test_internal_class_imports'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[1].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'method_two', 'source method for call is wrong')
 
    #test calling a function from an imported module from another package
    def test_internal_method_imports_package(self):
        repo = 'tests/unit_tests/test_internal_method_imports_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #test calling a function from an imported class from another package
    def test_internal_method_class_imports_package(self):
        repo = 'tests/unit_tests/test_internal_method_class_imports_package'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[1].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #check call of method in a class by another method not in the class, both in same module
    def test_module_internal_class_call(self):
        repo = 'tests/unit_tests/test_module_internal_class_call'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertIsNotNone(ecore_graph.modules[0].contains[0].defines[0].accessedBy, 'call source is missing')
        self.assertEqual(len(ecore_graph.modules[0].contains[1].accessing), 1, 'call object is missing')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].target.signature.method.tName, 'called_func', 'target has wrong name')
        self.assertEqual(ecore_graph.modules[0].contains[1].signature.method.tName, 'caller_func', 'caller method has wrong name')
        self.assertEqual(ecore_graph.modules[0].contains[1].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is wrong type')
        self.assertIsNotNone(ecore_graph.modules[0].contains[1].accessing[0].target, 'target is missing')

    #check call of method in a class by another method, both in same class
    def test_class_internal_method_call(self):
        repo = 'tests/unit_tests/test_class_internal_method_call'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[1].accessing[0].eClass.name, NodeTypes.CALL.value, 'call is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[1].accessing[0].target.signature.method.tName, 'called_func', 'target has wrong method name')
        self.assertEqual(ecore_graph.modules[0].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'caller_func', 'source has wrong method name')

    #test call for method in multiple packages(subpackage)
    def test_internal_method_imports_multiple_packages(self):
        repo = 'tests/unit_tests/test_internal_method_imports_multiple_packages'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[2].contains[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    #test call for method in class in multiple packages(subpackage)
    def test_internal_method_class_imports_multiple_packages(self):
        repo = 'tests/unit_tests/test_internal_method_class_imports_multiple_packages'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.modules[0].contains[0].signature.method.tName, 'method_two', 'wrong method name using the import')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'imported method cannot be used, import did not work')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'one_method', 'imported method name wrong')
        self.assertEqual(ecore_graph.modules[2].contains[0].defines[0].accessedBy[0].source.signature.method.tName, 'method_two', 'call source is wrong')

    def test_call_external_library(self):
        repo = 'tests/unit_tests/test_call_external_library'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.packages[0].tName, 'numpy', 'imported library package is missing')
        self.assertEqual(ecore_graph.modules[1].namespace.tName, 'numpy', 'imported library module and package edge wrong')
        self.assertEqual(len(ecore_graph.modules), 2, 'wrong number of modules')
        self.assertEqual(ecore_graph.modules[1].location, 'numpy', 'imported library has wrong name')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].eClass.name, NodeTypes.CALL.value, 'call object is wrong type')
        self.assertEqual(ecore_graph.modules[0].contains[0].accessing[0].target.signature.method.tName, 'array', 'target has wrong name')
        self.assertEqual(ecore_graph.modules[1].contains[0].accessedBy[0].source.signature.method.tName, 'one_method', 'source has wrong name')

    '''multiple packages/subpackages in imported library'''
    def test_call_external_library_submodule(self):
        repo = 'tests/unit_tests/test_call_external_library_submodule'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(len(ecore_graph.packages), 2, 'wrong number of packages')
        self.assertEqual(ecore_graph.packages[1].tName, 'torch_geometric', 'import with length>2 has wrong package name')
        self.assertEqual(ecore_graph.modules[2].namespace.tName, 'torch_geometric', 'wrong modules namespace')
        self.assertEqual(ecore_graph.modules[2].contains[0].signature.method.tName, 'global_mean_pool', 'wrong method name in imported module')
        self.assertEqual(ecore_graph.modules[2].contains[0].accessedBy[0].eClass.name, NodeTypes.CALL.value, 'wrong object type')

    def test_call_external_library_class(self):
        repo = 'tests/unit_tests/test_call_external_library_class'
        resource_set = ResourceSet()
        graph = ProjectEcoreGraph(resource_set, repo, False)
        ecore_graph = graph.get_graph()
        self.assertEqual(ecore_graph.packages[0].tName, 'torch', 'wrong package name for import')
        self.assertEqual(len(ecore_graph.packages), 1, 'wrong number of imported packages')
        self.assertEqual(len(ecore_graph.packages[0].subpackages), 1, 'subpackage wrong number')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].tName, 'utils', 'subpackages wrong name')
        self.assertEqual(ecore_graph.packages[0].subpackages[0].parent.tName, 'torch', 'parent package wrong')

unittest.main()