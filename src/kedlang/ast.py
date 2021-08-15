import abc
from typing import List, Optional, Union

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


class Lt(BinaryOperator):
    pass


class LtE(BinaryOperator):
    pass


class Gt(BinaryOperator):
    pass


class GtE(BinaryOperator):
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
        return f"<{self.__class__.__name__} {self.statements}>"


class Declare(Statement):
    def __init__(
        self, variable: Variable, initializer: Optional[Expression] = None
    ) -> None:
        self.variable, self.initializer = variable, initializer

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.variable} {self.initializer}>"


class FunctionDef(Statement):
    def __init__(self, name: Name, params: List[Variable], body: Statement) -> None:
        self.name, self.__params, self.body = name, params, body

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.__params} {self.body}>"

    @property
    def params(self) -> List[Variable]:
        if self.rest_param is None:
            return self.__params
        else:
            return self.__params[:-1]

    @property
    def rest_param(self) -> Optional[Variable]:
        if len(self.__params) == 0:
            return None
        if not isinstance(self.__params[-1], Spread):
            return None
        return self.__params[-1].value


class Static(Statement):
    def __init__(self, statement: Statement) -> None:
        self.statement = statement

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.statement}>"


class ClassDef(Statement):
    def __init__(self, name: Name, base: Name, body: Statement) -> None:
        self.name, self.base, self.body = name, base, body

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.base} {self.body}>"


class Delete(Statement):
    def __init__(self, variable: Variable) -> None:
        self.variable = variable

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.variable}>"


class Compound(Statement):
    def __init__(self, children: List[Statement]) -> None:
        self.children = children

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.children}>"


class Expr(Statement):
    def __init__(self, value: Expression) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.test} {self.body} {self.orelse}>"


class Catch(KedAST):
    def __init__(
        self,
        type: Union[Name, Variable],
        name: Variable,
        body: List[Statement],
    ) -> None:
        self.type = type
        self.name = name
        self.body = body

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.type} {self.name} {self.body}>"


class Try(Statement):
    def __init__(
        self,
        body: List[Statement],
        handlers: List[Catch],
        finallybody: List[Statement],
    ) -> None:
        self.body = body
        self.handlers = handlers
        self.finallybody = finallybody

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.body} {self.handlers} {self.finallybody}>"


class Throw(Statement):
    def __init__(self, exc: Expression) -> None:
        self.exc = exc

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.exc}>"


class While(Statement):
    def __init__(self, test: Expression, body: List[Statement]) -> None:
        self.test = test
        self.body = body

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.test} {self.body}>"


class Continue(Statement):
    pass


class Break(Statement):
    pass


class Return(Statement):
    def __init__(self, value: Optional[Expression] = None) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


class Print(Statement):
    def __init__(self, value: Expression) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


class Import(Statement):
    def __init__(self, name: Expression, is_strict: bool = False) -> None:
        self.name, self.is_strict = name, is_strict

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.is_strict}>"


class Assign(Expression):
    def __init__(self, variable: Variable, expression: Expression) -> None:
        self.variable, self.expression = variable, expression

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.variable} {self.expression}>"


class BinaryOp(Expression):
    def __init__(self, left: Expression, op: BinaryOperator, right: Expression) -> None:
        self.left, self.right = left, right
        self.token = self.op = op

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.left} {self.op} {self.right}>"


class UnaryOp(Expression):
    def __init__(self, op: UnaryOperator, operand: Expression) -> None:
        self.op, self.operand = op, operand

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.op} {self.operand}>"


class Attribute(Expression):
    def __init__(self, value: Expression, attr: str) -> None:
        self.value, self.attr = value, attr

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value} {self.attr}>"


class ScopeResolution(Attribute):
    pass


class Subscript(Expression):
    def __init__(self, value: Expression, index: Expression) -> None:
        self.value, self.index = value, index

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value} {self.index}>"


class Call(Expression):
    def __init__(self, func: Expression, args: List[Expression]) -> None:
        self.func, self.args = func, args

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.func} {self.args}>"


class Constructor(Expression):
    def __init__(self, class_type: Expression, args: List[Expression]) -> None:
        self.class_type, self.args = class_type, args

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.class_type} {self.args}>"


class IsDeclared(Expression):
    def __init__(self, variable: Variable) -> None:
        self.variable = variable

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.variable}>"


class List(Expression):
    def __init__(self, elements: List[Expression]) -> None:
        self.elements = elements

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.elements}>"


class Spread(Expression):
    def __init__(self, value: Expression) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


class Constant(Expression):
    def __init__(self, token: Token) -> None:
        self.token = token

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.token.value}>"


class Input(Expression):
    def __init__(self, prompt: Expression) -> None:
        self.prompt = prompt

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.prompt}>"


class NoOp(Expression):
    pass


class Sleep(Expression):
    def __init__(self, value: Expression) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"


class Exit(Expression):
    pass
