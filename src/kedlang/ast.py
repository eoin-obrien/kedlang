import abc
from typing import List, Optional

from sly.lex import Token


class KedAST(abc.ABC):
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Expression(KedAST, metaclass=abc.ABCMeta):
    pass


class Statement(KedAST, metaclass=abc.ABCMeta):
    pass


class Operator(KedAST, metaclass=abc.ABCMeta):
    pass


class UnaryOperator(Operator, metaclass=abc.ABCMeta):
    pass


class UAdd(UnaryOperator):
    pass


class USub(UnaryOperator):
    pass


class Not(UnaryOperator):
    pass


class BinaryOperator(Operator, metaclass=abc.ABCMeta):
    pass


class Add(BinaryOperator):
    pass


class Sub(BinaryOperator):
    pass


class Mult(BinaryOperator):
    pass


class Div(BinaryOperator):
    pass


class Mod(BinaryOperator):
    pass


class And(BinaryOperator):
    pass


class Or(BinaryOperator):
    pass


class Concat(BinaryOperator):
    pass


class Eq(BinaryOperator):
    pass


class NotEq(BinaryOperator):
    pass


class StrictEq(BinaryOperator):
    pass


class NotStrictEq(BinaryOperator):
    pass


class Name(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = self.token.value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


class Variable(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = self.token.value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


class Program(KedAST):
    def __init__(self, statements: List[Statement]) -> None:
        self.statements = statements

    def __repr__(self) -> str:
        statements = '\n'.join(self.statements)
        return f"<{self.__class__.__name__} {statements}>"


class Declare(Statement):
    def __init__(
        self, variable: Variable, initializer: Optional[Expression] = None
    ) -> None:
        self.variable, self.initializer = variable, initializer

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.variable}={self.initializer}>"


class FunctionDef(Statement):
    # TODO returns
    def __init__(self, name: Name, params: List[Variable], body: Statement) -> None:
        self.name, self.params, self.body = name, params, body


class Delete(Statement):
    def __init__(self, variable: Variable) -> None:
        self.variable = variable


class Compound(Statement):
    def __init__(self, children: List[Statement]) -> None:
        self.children = children


class Expr(Statement):
    def __init__(self, value: Expression) -> None:
        self.value = value


class If(Statement):
    def __init__(
        self,
        test: Expression,
        body: List[Statement],
        orelse: List[Statement],
    ) -> None:
        self.test = test
        self.body = body
        self.orelse = orelse


class While(Statement):
    def __init__(self, test: Expression, body: List[Statement]) -> None:
        self.test = test
        self.body = body


class Continue(Statement):
    pass


class Break(Statement):
    pass


class Return(Statement):
    def __init__(self, value: Optional[Expression] = None) -> None:
        self.value = value


class Print(Statement):
    def __init__(self, value: Expression) -> None:
        self.value = value


class Import(Statement):
    def __init__(self, name: Expression, is_strict: bool = False) -> None:
        self.name, self.is_strict = name, is_strict


class Assign(Expression):
    def __init__(self, variable: Variable, expression: Expression) -> None:
        self.variable, self.expression = variable, expression


class BinaryOp(Expression):
    def __init__(self, left: Expression, op: BinaryOperator, right: Expression) -> None:
        self.left, self.right = left, right
        self.token = self.op = op


class UnaryOp(Expression):
    def __init__(self, op: UnaryOperator, operand: Expression) -> None:
        self.op, self.operand = op, operand


class Attribute(Expression):
    def __init__(self, value: Expression, attr: str) -> None:
        self.value, self.attr = value, attr


class Subscript(Expression):
    def __init__(self, value: Expression, index: Expression) -> None:
        self.value, self.index = value, index


class Call(Expression):
    def __init__(self, func: Expression, args: List[Expression]) -> None:
        self.func, self.args = func, args


class IsDeclared(Expression):
    def __init__(self, variable: Variable) -> None:
        self.variable = variable


class Constant(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token


class NoOp(Expression):
    pass


class Sleep(Expression):
    def __init__(self, value: Expression) -> None:
        self.value = value


class Exit(Expression):
    pass
