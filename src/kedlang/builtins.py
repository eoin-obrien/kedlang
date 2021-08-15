from sly.lex import Token

from kedlang import ast
from kedlang.symbol import Symbol
from kedlang.types import KedClass


def to_ked_string(value="") -> str:
    if isinstance(value, list):
        return [to_ked_string(element) for element in value]

    if value is None:
        return "nuttin"
    elif isinstance(value, bool):
        return "gospel" if value else "bull"
    elif isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)
    return str(value)


def to_ked_number(value=None) -> float:
    if value is None:
        return 0
    try:
        return float(value)
    except ValueError:
        return float("nan")


def to_ked_boolean(value=None) -> bool:
    return bool(value)


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
