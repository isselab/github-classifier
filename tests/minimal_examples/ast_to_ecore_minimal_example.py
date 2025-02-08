import ast


class ProjectEcoreGraph:
    def __init__(self):
        self.graph = None
        self.current_module = None
        self.field_list = []

    def create_field(self, field_node, name, field_type=None):
        field = Field()
        field.name = name
        field.type = field_type
        field_node.fields.append(field)
        self.field_list.append([field_node, name, field_type])

    def get_field_from_internal_structure(self, field_name, module=None):
        for current_field in self.field_list:
            if field_name == current_field[1]:
                if module is None and current_field[2] is None:
                    return current_field[0]
                if hasattr(module, 'location') and hasattr(current_field[2], 'location'):
                    if module.location == current_field[2].location:
                        return current_field[0]
        return None


class Field:
    def __init__(self):
        self.name = None
        self.type = None


class Module:
    def __init__(self):
        self.fields = []


class ASTVisitor(ast.NodeVisitor):
    def __init__(self, ecore_graph):
        self.ecore_graph = ecore_graph
        self.current_module = None
        self.current_class = None

    def visit_Assign(self, node):
        if self.current_class is not None:
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name):
                        if target.value.id == 'self':
                            field_name = target.attr
                            field_type = None
                            if isinstance(node.value, ast.Constant):
                                field_type = type(node.value.value).__name__
                            elif isinstance(node.value, ast.Call):
                                if isinstance(node.value.func, ast.Name):
                                    field_type = node.value.func.id
                                elif isinstance(node.value.func, ast.Attribute):
                                    field_type = node.value.func.attr
                            elif isinstance(node.value, ast.Name):
                                field_type = node.value.id
                            elif isinstance(node.value, ast.Attribute):
                                field_type = node.value.attr
                            self.ecore_graph.create_field(self.current_class, field_name, field_type)
                elif isinstance(target, ast.Name):
                    field_name = target.id
                    field_type = None
                    if isinstance(node.value, ast.Constant):
                        field_type = type(node.value.value).__name__
                    elif isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name):
                            field_type = node.value.func.id
                        elif isinstance(node.value.func, ast.Attribute):
                            field_type = node.value.func.attr
                    elif isinstance(node.value, ast.Name):
                        field_type = node.value.id
                    elif isinstance(node.value, ast.Attribute):
                        field_type = node.value.attr
                    self.ecore_graph.create_field(self.current_class, field_name, field_type)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.current_class = Module()
        self.generic_visit(node)


class VarVisitor(ast.NodeVisitor):
    def __init__(self, var_name):
        self.var_name = var_name
        self.found = False

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == self.var_name:
                self.found = True

    def visit_FunctionDef(self, node):
        for statement in node.body:
            self.visit(statement)

    def visit_ClassDef(self, node):
        for statement in node.body:
            self.visit(statement)


def check_var_in_class(code, var_name):
    tree = ast.parse(code)
    visitor = VarVisitor(var_name)
    visitor.visit(tree)
    return visitor.found


# Example usage
ecore_graph = ProjectEcoreGraph()
visitor = ASTVisitor(ecore_graph)

code = """
class MyClass:
    def __init__(self):
        self.my_field = 5
        self.my_field_2 = "Hi"

    a = 5
    b = "Hallo"
"""

tree = ast.parse(code)
visitor.visit(tree)

print(ecore_graph.field_list)

var_name = "a"
if check_var_in_class(code, var_name):
    print(f"Variable {var_name} found in class")
else:
    print(f"Variable {var_name} not found in class")