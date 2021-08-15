import itertools
import math
import operator
import os
import time
from typing import Any, Union

from . import ast, exception, lexer, parser, visitor
from .builtins import to_ked_boolean, to_ked_number, to_ked_string
from .callstack import CallStack, Frame
from .cwdstack import CWDStack
from .symbol import Namespace, NamespacedSymbol, Symbol
from .types import KedClass, KedFunction, KedObject


class KedInterpreter(visitor.KedASTVisitor):
    def __init__(
        self, lexer: lexer.KedLexer, parser: parser.KedParser, cwd=None
    ) -> None:
        super().__init__()
        self.parser = parser
        self.lexer = lexer

        # Track the current working directory
        self.cwd_stack = CWDStack()
        self.cwd_stack.push(cwd or os.getcwd())

        # Create global stack frame
        self.call_stack = CallStack()
        self.call_stack.push(Frame(name="global"))

        # Init builtins
        self.current_scope.declare(Symbol("boolean"), to_ked_boolean)
        self.current_scope.declare(Symbol("number"), to_ked_number)
        self.current_scope.declare(Symbol("string"), to_ked_string)
        self.current_scope.declare(Symbol("len"), self.get_length)

    def interpret(self, ast: ast.KedAST) -> Any:
        return self.visit(ast)

    @property
    def cwd(self) -> str:
        return self.cwd_stack.peek()

    @property
    def current_scope(self):
        return self.call_stack.peek()

    def get_length(self, target: Union[ast.KedAST, Symbol, Any]):
        return len(self.resolve(target))

    def resolve(self, target: Union[ast.KedAST, Symbol, Any]):
        # Visit nodes before resolving
        if isinstance(target, ast.KedAST):
            target = self.visit(target)

        # Resolve symbols from the current stack frame
        if isinstance(target, Symbol):
            return self.current_scope.fetch(target)

        # Value types are returned as-is
        return target

    def resolve_spread(self, target: Union[ast.KedAST, Symbol, Any]):
        def resolve_element(element):
            resolved = self.resolve(element)
            return [*resolved] if isinstance(element, ast.Spread) else [resolved]

        return list(itertools.chain(*map(resolve_element, target)))

    # TODO classes
    # TODO attributes
    # TODO exceptions

    def visit_Program(self, node: ast.Program) -> None:
        try:
            for statement in node.statements:
                self.visit(statement)
        except exception.Exit:
            pass

    def visit_Declare(self, node: ast.Declare) -> None:
        symbol = self.visit(node.variable)
        initializer = self.resolve(node.initializer)
        self.current_scope.declare(symbol, initializer)

    def visit_Delete(self, node: ast.Delete) -> None:
        symbol = self.visit(node.variable)
        self.current_scope.delete(symbol)

    def visit_Assign(self, node: ast.Assign) -> Any:
        symbol = self.visit(node.variable)
        value = self.resolve(node.expression)
        self.current_scope.assign(symbol, value)
        return value

    def visit_Compound(self, node: ast.Compound) -> None:
        for statement in node.children:
            self.visit(statement)

    def visit_Expr(self, node: ast.Expr) -> Any:
        return self.visit(node.value)

    def visit_If(self, node: ast.If) -> None:
        for statement in node.body if self.visit(node.test) else node.orelse:
            self.visit(statement)

    def visit_While(self, node: ast.While) -> None:
        while self.visit(node.test):
            try:
                for statement in node.body:
                    self.visit(statement)
            except exception.Continue:
                continue
            except exception.Break:
                break

    def visit_Continue(self, node: ast.Continue) -> None:
        raise exception.Continue()

    def visit_Break(self, node: ast.Break) -> None:
        raise exception.Break()

    def visit_Return(self, node: ast.Return) -> None:
        raise exception.Return(self.resolve(node.value))

    def visit_Print(self, node: ast.Print) -> None:
        value = to_ked_string(self.resolve(node.value))
        print(value)

    def visit_Import(self, node: ast.Import) -> None:
        import_path = os.path.realpath(os.path.join(self.cwd, self.resolve(node.name)))
        try:
            with open(import_path) as f:
                ast = self.parser.parse(self.lexer.tokenize(f.read()))
        except FileNotFoundError:
            if node.is_strict:
                raise ImportError(f"No such file or directory: '{import_path}'")
        else:
            self.cwd_stack.push(import_path)
            self.visit(ast)
            self.cwd_stack.pop()

    def visit_BinaryOp(self, node: ast.BinaryOp) -> None:
        left = self.resolve(node.left)
        right = self.resolve(node.right)
        op = node.op.__class__

        number_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
        }

        if op in number_ops:
            return number_ops[op](to_ked_number(left), to_ked_number(right))

        string_ops = {
            ast.Concat: operator.add,
        }

        if op in string_ops:
            return string_ops[op](to_ked_string(left), to_ked_string(right))

        is_eq = lambda a, b: to_ked_string(a) == to_ked_string(b)
        is_strict_eq = lambda a, b: a == b and type(a) == type(b)
        logic_ops = {
            ast.And: operator.and_,
            ast.Or: operator.or_,
            ast.Eq: is_eq,
            ast.NotEq: lambda a, b: not is_eq(a, b),
            ast.StrictEq: is_strict_eq,
            ast.NotStrictEq: lambda a, b: not is_strict_eq(a, b),
        }

        if op in logic_ops:
            return logic_ops[op](left, right)

        relational_ops = {
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
        }

        if op in relational_ops:
            if str in [type(left), type(right)]:
                left = to_ked_string(left)
                right = to_ked_string(right)
            return relational_ops[op](left, right)

        raise TypeError("Unknown binary operator " + op.__name__)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        operand = self.resolve(node.operand)

        if isinstance(node.op, ast.UAdd):
            return +to_ked_number(operand)
        elif isinstance(node.op, ast.USub):
            return -to_ked_number(operand)
        elif isinstance(node.op, ast.Not):
            return not operand

        raise TypeError("Unknown unary operator " + node.op.__class__.__name__)

    def visit_NoOp(self, node: ast.NoOp) -> None:
        pass

    def visit_Sleep(self, node: ast.Sleep) -> None:
        time.sleep(self.resolve(node.value))

    def visit_Exit(self, node: ast.Exit) -> None:
        raise exception.Exit()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        name = self.visit(node.name)
        params = list(map(self.visit, node.params))
        rest_param = self.visit(node.rest_param)
        body = node.body

        # Functions bind the scope they're defined in, not the one they're called in
        bound_scope = self.current_scope

        def func_impl(*args):
            # Pad args to match function arity
            args = list(args) + [None] * min(0, len(params) - len(args))

            # Add param symbols to stack frame
            frame = Frame(name, parent=bound_scope)
            for (param, arg) in zip(params, args):
                frame.declare(param, arg)
            if rest_param is not None:
                frame.declare(rest_param, args[len(params) :])

            # Execute function body
            return_value = None
            try:
                self.call_stack.push(frame)
                self.visit(body)
            except exception.Return as ked_return:
                return_value = ked_return.value
            finally:
                self.call_stack.pop()
            return return_value

        func_impl.__name__ = str(name)

        self.current_scope.declare(name, KedFunction(func_impl))

    def visit_Call(self, node: ast.Call) -> Any:
        func = self.resolve(node.func)
        args = self.resolve_spread(node.args)
        # TODO check func is function
        return func(*args)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        name = self.visit(node.name)
        base = self.resolve(node.base)

        statics = [stmt for stmt in node.body if isinstance(stmt, ast.Static)]
        members = [stmt for stmt in node.body if not isinstance(stmt, ast.Static)]

        class_impl = KedClass(name, base, members)

        # Construct static class members
        static_frame = Frame(name, parent=self.current_scope)
        static_frame.declare(Symbol("youKnowYourself"), class_impl)
        static_frame.declare(Symbol("youKnowYourDa"), base)
        static_frame.declare(Symbol("youKnowYourMa"), base)
        self.call_stack.push(static_frame)
        for stmt in statics:
            self.visit(stmt)
        self.call_stack.pop()

        # Declare static class members in namespace
        for key, value in static_frame._members.items():
            symbol = NamespacedSymbol(key.name, class_impl)
            class_impl[key.name] = symbol
            self.current_scope.declare(symbol, value)

        self.current_scope.declare(name, class_impl)

    def visit_Constructor(self, node: ast.Constructor) -> Namespace:
        class_type = self.resolve(node.class_type)
        # TODO pass args to constructor
        args = self.resolve_spread(node.args)
        # TODO check class_type is actually a class

        instance = self.__construct_class_instance(class_type)

        # Invoke constructor if one exists in the inheritance hierarchy
        constructor = self.current_scope.fetch(instance["constructor"])
        if callable(constructor):
            constructor(*args)

        return instance

    def visit_Static(self, node: ast.Static) -> Any:
        return self.visit(node.statement)

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        value = self.resolve(node.value)
        return value[node.attr]

    def visit_ScopeResolution(self, node: ast.ScopeResolution) -> Any:
        value = self.resolve(node.value)

        # If value is a namespace, operate on its class
        if isinstance(value, KedObject):
            value = value.class_type

        # If value is neither a class nor an object, raise an exception
        if not isinstance(value, KedClass):
            raise exception.SemanticError(
                f"Operator '::' must be used on a class or thing, not '{type(value).__name__}'"
            )

        # Return attribute from statics
        return value[node.attr]

    def visit_IsDeclared(self, node: ast.IsDeclared) -> bool:
        return self.visit(node.variable) in self.current_scope

    def visit_List(self, node: ast.List) -> list:
        return self.resolve_spread(node.elements)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        value = self.resolve(node.value)
        index = int(to_ked_number(self.resolve(node.index)))
        return value[index]

    def visit_Spread(self, node: ast.Spread) -> list:
        return self.resolve(node.value)

    def visit_Constant(self, node: ast.Constant) -> str:
        return node.token.value

    def visit_Name(self, node: ast.Name) -> None:
        return Symbol(node.token.value)

    def visit_Variable(self, node: ast.Variable) -> None:
        return Symbol(node.token.value)

    def __bind_instance_method(self, func, instance) -> KedFunction:
        def bound_func(*args):
            bound_frame = Frame(instance.name, parent=self.current_scope)
            self.call_stack.push(bound_frame)
            return_value = func(*args)
            self.call_stack.pop()
            return return_value

        return KedFunction(bound_func)

    def __construct_class_instance(self, class_type: KedClass):
        if class_type.base is not None:
            base_instance = self.__construct_class_instance(class_type.base)
        else:
            base_instance = None

        instance = KedObject(class_type)

        # Execute class body to create attributes
        frame = Frame(class_type.name, parent=self.current_scope)
        frame.declare(Symbol("youKnowYourself"), instance)
        frame.declare(Symbol("youKnowYourDa"), base_instance)
        frame.declare(Symbol("youKnowYourMa"), base_instance)
        self.call_stack.push(frame)
        for stmt in class_type.body:
            self.visit(stmt)
        self.call_stack.pop()

        # Inherit attributes from base class instance
        if base_instance is not None:
            for key in base_instance.attributes:
                instance[key] = base_instance[key]

        # Inherit attributes from base class instance
        for key, value in frame._members.items():
            if isinstance(value, KedFunction):
                value = self.__bind_instance_method(value, instance)
            symbol = NamespacedSymbol(key.name, instance)
            instance[key.name] = symbol
            self.current_scope.declare(symbol, value)

        return instance
