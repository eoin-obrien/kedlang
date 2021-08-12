import os
import time
from typing import Any, Union

from . import ast, exception, lexer, parser, stack, visitor
from .builtins import to_ked_boolean, to_ked_number, to_ked_string
from .symbol import Symbol


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

    def resolve(self, target: Union[ast.KedAST, Symbol, Any]):
        # Visit nodes before resolving
        if isinstance(target, ast.KedAST):
            target = self.visit(target)

        # Resolve symbols from the current stack frame
        if isinstance(target, Symbol):
            return self.current_scope.fetch(target)

        # Value types are returned as-is
        return target

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
        raise exception.Return(self.visit(node.value))

    def visit_Print(self, node: ast.Print) -> None:
        value = to_ked_string(self.visit(node.value))
        print(value)

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
        left = self.resolve(node.left)
        right = self.resolve(node.right)

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
        operand = self.resolve(node.operand)

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
        time.sleep(self.resolve(node.value))

    def visit_Exit(self, node: ast.Exit) -> None:
        raise exception.Exit()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        func_name = self.visit(node.name)
        func_params = [self.visit(param) for param in node.params]
        func_body = node.body

        def func_impl(*args):
            frame = stack.Frame(func_name, parent=self.current_scope)
            # TODO match arity?
            # Add parameter symbols to stack frame
            for (param, arg) in zip(func_params, args):
                frame.declare(param, self.resolve(arg))

            # Execute function body
            return_value = None
            try:
                self.call_stack.push(frame)
                self.visit(func_body)
            except exception.Return as ked_return:
                return_value = ked_return.value
            finally:
                self.call_stack.pop()
            return return_value

        self.current_scope.declare(func_name, func_impl)

    def visit_Call(self, node: ast.Call) -> Any:
        func = self.resolve(node.func)
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def visit_IsDeclared(self, node: ast.IsDeclared) -> bool:
        return self.visit(node.variable) in self.current_scope

    def visit_Constant(self, node: ast.Constant) -> str:
        return node.token.value

    def visit_Name(self, node: ast.Name) -> None:
        return Symbol(node.token.value)

    def visit_Variable(self, node: ast.Variable) -> None:
        return Symbol(node.token.value)
