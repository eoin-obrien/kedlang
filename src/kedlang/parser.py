from sly import Parser
from sly.lex import Token
from sly.yacc import YaccProduction

from . import ast, lexer


def get_token(p: YaccProduction, index: int = 0) -> Token:
    return p._slice[index]


class KedParser(Parser):

    # Get the token list from the lexer (required)
    tokens = lexer.KedLexer.tokens
    debugfile = "parser.out"

    # pyright: reportUndefinedVariable=false

    precedence = (
        ("nonassoc", IF),
        ("nonassoc", ELIF),
        ("nonassoc", ELSE),
        ("right", "="),
        ("nonassoc", ARRAY),
        ("left", OR),
        ("left", AND),
        ("left", EQ, STRICTEQ),
        ("left", LT, LTE, GT, GTE),
        ("left", CONCAT),
        ("left", PLUS, MINUS),
        ("left", TIMES, DIVIDE, MOD),
        ("right", UMINUS),
        ("left", "(", "["),
    )

    @_("statements")
    def translation_unit(self, p: YaccProduction):
        return ast.Program(p.statements)

    @_("DECLARE variable LIKE")
    def declaration(self, p: YaccProduction):
        return ast.Declare(p.variable)

    @_('DECLARE variable "=" assignment_expression LIKE')
    def declaration(self, p: YaccProduction):
        return ast.Declare(p.variable, p.assignment_expression)

    @_('DECLARE name "(" spread_parameter_list ")" statement')
    def declaration(self, p: YaccProduction):
        return ast.FunctionDef(p.name, p.spread_parameter_list, p.statement)

    @_("UNDECLARE variable LIKE")
    def undeclaration(self, p: YaccProduction):
        return ast.Delete(p.variable)

    @_('parameter_list "," spread_parameter')
    def spread_parameter_list(self, p: YaccProduction):
        return [*p.parameter_list, p.spread_parameter]

    @_("spread_parameter")
    def spread_parameter_list(self, p: YaccProduction):
        return [p.spread_parameter]

    @_("parameter_list")
    def spread_parameter_list(self, p: YaccProduction):
        return p.parameter_list

    @_("")
    def spread_parameter_list(self, p: YaccProduction):
        return []

    @_('parameter_list "," parameter')
    def parameter_list(self, p: YaccProduction):
        return [*p.parameter_list, p.parameter]

    @_("parameter")
    def parameter_list(self, p: YaccProduction):
        return [p.parameter]

    @_("SPREAD variable")
    def spread_parameter(self, p: YaccProduction):
        return ast.Spread(p.variable)

    @_("variable")
    def parameter(self, p: YaccProduction):
        return p.variable

    @_('"{" statements "}"')
    def compound_statement(self, p: YaccProduction):
        return ast.Compound(p.statements)

    @_("")
    def statements(self, p: YaccProduction):
        return []

    @_("statements statement")
    def statements(self, p: YaccProduction):
        return [*p.statements, p.statement]

    @_(
        "declaration",
        "undeclaration",
        "expression_statement",
        "compound_statement",
        "if_statement",
        "iteration_statement",
        "jump_statement",
        "print_statement",
        "import_statement",
    )
    def statement(self, p: YaccProduction):
        return p[0]

    @_("LIKE")
    def expression_statement(self, p: YaccProduction):
        return ast.Expr(ast.NoOp())

    @_("expression LIKE")
    def expression_statement(self, p: YaccProduction):
        return ast.Expr(p.expression)

    @_('IF "(" expression ")" statement %prec IF')
    def if_statement(self, p: YaccProduction):
        return ast.If(p.expression, [p.statement], [])

    @_('IF "(" expression ")" statement else_statement')
    def if_statement(self, p: YaccProduction):
        return ast.If(p.expression, [p.statement], [p.else_statement])

    @_('ELIF "(" expression ")" statement %prec ELIF')
    def else_statement(self, p: YaccProduction):
        return ast.If(p.expression, [p.statement], [])

    @_('ELIF "(" expression ")" statement else_statement')
    def else_statement(self, p: YaccProduction):
        return ast.If(p.expression, [p.statement], [p.else_statement])

    @_("ELSE statement")
    def else_statement(self, p: YaccProduction):
        return p.statement

    @_('WHILE "(" expression ")" statement')
    def iteration_statement(self, p: YaccProduction):
        return ast.While(p.expression, [p.statement])

    @_("CONTINUE LIKE")
    def jump_statement(self, p: YaccProduction):
        return ast.Continue()

    @_("BREAK LIKE")
    def jump_statement(self, p: YaccProduction):
        return ast.Break()

    @_("RETURN LIKE")
    def jump_statement(self, p: YaccProduction):
        return ast.Return()

    @_("RETURN expression LIKE")
    def jump_statement(self, p: YaccProduction):
        return ast.Return(p.expression)

    @_("PRINT expression LIKE")
    def print_statement(self, p: YaccProduction):
        return ast.Print(p.expression)

    @_("IMPORT expression LIKE")
    def import_statement(self, p: YaccProduction):
        return ast.Import(p.expression)

    @_("STRICT_IMPORT expression LIKE")
    def import_statement(self, p: YaccProduction):
        return ast.Import(p.expression, is_strict=True)

    @_("logical_or_expression")
    def conditional_expression(self, p: YaccProduction):
        return p[0]

    @_("logical_and_expression")
    def logical_or_expression(self, p: YaccProduction):
        return p[0]

    @_("logical_or_expression OR logical_and_expression")
    def logical_or_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Or(), p[-1])

    @_("eq_expression")
    def logical_and_expression(self, p: YaccProduction):
        return p[0]

    @_("logical_and_expression AND eq_expression")
    def logical_and_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.And(), p[-1])

    @_("relational_expression")
    def eq_expression(self, p: YaccProduction):
        return p[0]

    @_("eq_expression EQ relational_expression")
    def eq_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Eq(), p[-1])

    @_("eq_expression STRICTEQ relational_expression")
    def eq_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.StrictEq(), p[-1])

    @_("eq_expression eq_operator NOT relational_expression %prec EQ")
    def eq_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.NotEq(), p[-1])

    @_("eq_expression strict_eq_operator NOT relational_expression %prec STRICTEQ")
    def eq_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.NotStrictEq(), p[-1])

    @_("EQ")
    def eq_operator(self, p: YaccProduction):
        return p[0]

    @_("STRICTEQ")
    def strict_eq_operator(self, p: YaccProduction):
        return p[0]

    @_("concat_expression")
    def relational_expression(self, p: YaccProduction):
        return p[0]

    @_("relational_expression LT concat_expression")
    def relational_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Lt(), p[2])

    @_("relational_expression GT concat_expression")
    def relational_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Gt(), p[2])

    @_("relational_expression LTE concat_expression")
    def relational_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.LtE(), p[2])

    @_("relational_expression GTE concat_expression")
    def relational_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.GtE(), p[2])

    @_("additive_expression")
    def concat_expression(self, p: YaccProduction):
        return p[0]

    @_("concat_expression CONCAT additive_expression")
    def concat_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Concat(), p[2])

    @_("multiplicative_expression")
    def additive_expression(self, p: YaccProduction):
        return p[0]

    @_("additive_expression PLUS cast_expression")
    def additive_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Add(), p[2])

    @_("additive_expression MINUS cast_expression")
    def additive_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[2], ast.Sub(), p[0])  # reversed

    @_("cast_expression")
    def multiplicative_expression(self, p: YaccProduction):
        return p[0]

    @_("multiplicative_expression TIMES cast_expression")
    def multiplicative_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Mult(), p[2])

    @_("multiplicative_expression DIVIDE cast_expression")
    def multiplicative_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[2], ast.Div(), p[0])  # reversed

    @_("multiplicative_expression MOD cast_expression")
    def multiplicative_expression(self, p: YaccProduction):
        return ast.BinaryOp(p[0], ast.Mod(), p[2])

    @_("unary_expression")
    def cast_expression(self, p: YaccProduction):
        return p[0]

    @_("postfix_expression %prec UMINUS")
    def unary_expression(self, p: YaccProduction):
        return p[0]

    @_("unary_operator cast_expression %prec UMINUS")
    def unary_expression(self, p: YaccProduction):
        return ast.UnaryOp(p.unary_operator, p.cast_expression)

    @_("primary_expression")
    def postfix_expression(self, p: YaccProduction):
        return p[0]

    @_('postfix_expression "[" expression "]"')
    def postfix_expression(self, p: YaccProduction):
        return ast.Subscript(p.postfix_expression, p.expression)

    @_('postfix_expression "(" ")"')
    def postfix_expression(self, p: YaccProduction):
        return ast.Call(p.postfix_expression, [])

    @_('postfix_expression "(" argument_list ")"')
    def postfix_expression(self, p: YaccProduction):
        return ast.Call(p.postfix_expression, p.argument_list)

    @_('postfix_expression "." NAME')
    def postfix_expression(self, p: YaccProduction):
        return ast.Attribute(p.postfix_expression, p.NAME)

    @_('argument_list "," argument')
    def argument_list(self, p: YaccProduction):
        return [*p.argument_list, p.argument]

    @_("argument")
    def argument_list(self, p: YaccProduction):
        return [p.argument]

    @_("SPREAD assignment_expression")
    def argument(self, p: YaccProduction):
        return ast.Spread(p.assignment_expression)

    @_("assignment_expression")
    def argument(self, p: YaccProduction):
        return p.assignment_expression

    @_('element_list "," element')
    def element_list(self, p: YaccProduction):
        return [*p.element_list, p.element]

    @_("element")
    def element_list(self, p: YaccProduction):
        return [p.element]

    @_("SPREAD assignment_expression")
    def element(self, p: YaccProduction):
        return ast.Spread(p.assignment_expression)

    @_("assignment_expression")
    def element(self, p: YaccProduction):
        return p.assignment_expression

    @_("identifier", "array", "number", "string", "boolean", "null")
    def primary_expression(self, p: YaccProduction):
        return p[0]

    @_('"(" expression ")"')
    def primary_expression(self, p: YaccProduction):
        return p.expression

    @_("assignment_expression")
    def expression(self, p: YaccProduction):
        return p[0]

    @_("conditional_expression")
    def assignment_expression(self, p: YaccProduction):
        return p[0]

    @_('variable "=" assignment_expression')
    def assignment_expression(self, p: YaccProduction):
        return ast.Assign(p.variable, p.assignment_expression)

    @_("NOT", '"!"')
    def unary_operator(self, p: YaccProduction):
        return ast.Not()

    @_('"+"')
    def unary_operator(self, p: YaccProduction):
        return ast.UAdd()

    @_('"-"')
    def unary_operator(self, p: YaccProduction):
        return ast.USub()

    @_('"[" "]" %prec ARRAY')
    def array(self, p: YaccProduction):
        return ast.List([])

    @_('"[" element_list "]" %prec ARRAY')
    def array(self, p: YaccProduction):
        return ast.List(p.element_list)

    @_("STRING")
    def string(self, p: YaccProduction):
        return ast.Constant(get_token(p))

    @_("NUMBER")
    def number(self, p: YaccProduction):
        return ast.Constant(get_token(p))

    @_("TRUE", "FALSE")
    def boolean(self, p: YaccProduction):
        return ast.Constant(get_token(p))

    @_("NULL")
    def null(self, p: YaccProduction):
        return ast.Constant(get_token(p))

    @_('IS_DECLARED "(" variable ")"')
    def boolean(self, p: YaccProduction):
        return ast.IsDeclared(p.variable)

    @_('NOOP "(" ")"')
    def expression(self, p: YaccProduction):
        return ast.NoOp()

    @_('SLEEP "(" expression ")"')
    def expression(self, p: YaccProduction):
        return ast.Sleep(p.expression)

    @_('EXIT "(" ")"')
    def expression(self, p: YaccProduction):
        return ast.Exit()

    @_("variable", "name")
    def identifier(self, p: YaccProduction):
        return p[0]

    @_("NAME")
    def name(self, p: YaccProduction):
        return ast.Name(get_token(p))

    @_("VARIABLE")
    def variable(self, p: YaccProduction):
        return ast.Variable(get_token(p))

    def error(self, p: YaccProduction):
        raise SyntaxError(f"invalid syntax on line {p.lineno} at token '{p.type}'")
