import os
import time
from typing import Any

from . import ast, exception, lexer, parser, stack, visitor
from .builtins import to_ked_boolean, to_ked_number, to_ked_string


class KedInterpreter(visitor.KedASTVisitor):
    def __init__(
        self, lexer: lexer.KedLexer, parser: parser.KedParser, cwd=None
    ) -> None:
        super().__init__()
        self.parser = parser
        self.lexer = lexer
        self.call_stack = stack.CallStack()
        self.cwd_stack = [cwd or os.getcwd()]

        # Create global stack frame
        self.call_stack.push(stack.GlobalFrame(name="global"))

    def interpret(self, ast: ast.KedAST) -> Any:
        return self.visit(ast)

    @property
    def cwd(self) -> str:
        return self.cwd_stack[-1]

    def push_cwd(self, cwd: str):
        self.cwd_stack.append(cwd)

    def pop_cwd(self) -> str:
        return self.cwd_stack.pop()

    @property
    def current_scope(self):
        return self.call_stack.peek()

    # TODO move to Frame instance methods
    def declare_identifier(self, name, value=None):
        if name in self.current_scope:
            raise SyntaxError("Identifier '" + name + "' has already been declared")
        self.current_scope[name] = value

    def undeclare_identifier(self, name):
        if name not in self.current_scope:
            raise SyntaxError("Identifier '" + name + "' has not been declared")
        del self.current_scope[name]

    def assign_to_identifier(self, name, value=None):
        if name not in self.current_scope:
            raise ReferenceError("'" + name + "' is not defined")
        self.current_scope[name] = value

    def resolve_identifier(self, name):
        return self.current_scope[name]
        while frame is not None:
            # print("RESOLVE", name, frame.members)
            if name in frame:
                return frame[name]
            frame = frame.parent

        raise ReferenceError("'" + name + "' is not defined")

    def visit_Program(self, node: ast.Program) -> None:
        try:
            for statement in node.statements:
                self.visit(statement)
        except exception.Exit:
            pass

    def visit_Declare(self, node: ast.Declare) -> None:
        variable = node.variable.value
        initializer = self.visit(node.initializer)
        if variable in self.current_scope:
            raise f"Attempting to redeclare variable {variable}"
        self.current_scope[variable] = initializer

    def visit_Delete(self, node: ast.Delete) -> None:
        variable = node.variable.value
        self.undeclare_identifier(variable)

    def visit_Assign(self, node: ast.Assign) -> Any:
        value = self.visit(node.expression)
        self.assign_to_identifier(node.variable.value, value)
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
        raise exception.Return(self.visit(node.value))

    def visit_Print(self, node: ast.Print) -> None:
        value = to_ked_string(self.visit(node.value))
        print("PRINT:", value)

    def visit_Import(self, node: ast.Import) -> None:
        import_path = os.path.join(self.cwd, self.visit(node.name))
        import_dir = os.path.dirname(os.path.realpath(import_path))

        try:
            with open(import_path) as f:
                ast = parser.parse(lexer.tokenize(f.read()))
        except FileNotFoundError:
            if node.is_strict:
                raise ImportError("No such file or directory: '" + import_path + "'")
        else:
            self.push_cwd(import_dir)
            self.visit(ast)
            self.pop_cwd()

    def visit_BinaryOp(self, node: ast.BinaryOp) -> None:
        left = self.visit(node.left)
        right = self.visit(node.right)

        # TODO should operators coerce types?

        # Arithmetic operators
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * left
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.Mod):
            return left % right

        # String operators
        if isinstance(node.op, ast.Concat):
            return to_ked_string(left) + to_ked_string(right)

        # Comparison operators
        if isinstance(node.op, ast.Eq):
            return to_ked_string(left) == to_ked_string(right)
        elif isinstance(node.op, ast.NotEq):
            return to_ked_string(left) != to_ked_string(right)
        elif isinstance(node.op, ast.NotStrictEq):
            return not (left == right and type(left) == type(right))
        elif isinstance(node.op, ast.StrictEq):
            return left == right and type(left) == type(right)

        # Logical operators
        if isinstance(node.op, ast.And):
            return left and right
        elif isinstance(node.op, ast.Or):
            return left or right

        raise TypeError("Unknown binary operator " + type(node.op).__name__)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        operand = self.visit(node.operand)

        if isinstance(node.op, ast.UAdd):
            return +operand
        elif isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.Not):
            return not operand

        raise TypeError("Unknown unary operator " + type(node.op).__name__)

    def visit_NoOp(self, node: ast.NoOp) -> None:
        pass

    def visit_Sleep(self, node: ast.Sleep) -> None:
        time.sleep(self.visit(node.value))

    def visit_Exit(self, node: ast.Exit) -> None:
        raise exception.Exit()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        func_name = node.name.value
        func_params = [param.value for param in node.params]
        func_body = node.body

        def func_impl(*args):
            frame = stack.Frame(func_name, parent=self.current_scope)
            # TODO match arity?
            # Add parameter symbols to stack frame
            for (param, arg) in zip(func_params, args):
                frame[param] = arg

            # Execute function body
            try:
                self.call_stack.push(frame)
                self.visit(func_body)
            except exception.Return as ked_return:
                return_value = ked_return.value
            else:
                return_value = None
            finally:
                self.call_stack.pop()
            return return_value

        self.declare_identifier(func_name, func_impl)

    def visit_Call(self, node: ast.Call) -> Any:
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def visit_IsDeclared(self, node: ast.IsDeclared) -> bool:
        return node.variable.value in self.current_scope

    def visit_Constant(self, node: ast.Constant) -> str:
        return node.token.value

    def visit_Name(self, node: ast.Name) -> None:
        # TODO context
        return self.resolve_identifier(node.token.value)

    def visit_Variable(self, node: ast.Variable) -> None:
        # TODO context
        return self.resolve_identifier(node.token.value)
