from sly.lex import Token

from kedlang import ast
from kedlang.symbol import Symbol
from kedlang.types import KedClass


def get_rebel_class() -> KedClass:
    msg_tok = Token()
    msg_tok.value = "€msg"
    constructor_tok = Token()
    constructor_tok.value = "constructor"
    this_tok = Token()
    this_tok.value = "youKnowYourself"
    return KedClass(
        Symbol("Rebel"),
        None,
        [
            ast.Declare(ast.Variable(msg_tok)),
            ast.FunctionDef(
                ast.Name(constructor_tok),
                [ast.Variable(msg_tok)],
                ast.Expr(
                    ast.Assign(
                        ast.Attribute(ast.Name(this_tok), msg_tok.value),
                        ast.Variable(msg_tok),
                    )
                ),
            ),
        ],
    )
