from pyecore.resources import ResourceSet, URI

#load xmi instance
rset = ResourceSet()
resource = rset.get_resource(URI('Basic.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root
resource = rset.get_resource(URI('../test_xmi/test.xmi'))
typegraph_root = resource.contents[0]

print(typegraph_root)