import abc
from typing import Optional

from . import ast


class KedASTVisitor(abc.ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """

    def visit(self, node: Optional[ast.KedAST]):
        if node is None:
            return None
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.fallback)
        return visitor(node)

    def fallback(self, node: ast.KedAST):
        raise NotImplementedError("No visit_{} method".format(type(node).__name__))
