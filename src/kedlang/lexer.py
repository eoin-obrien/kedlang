from sly import Lexer
from sly.lex import Token


class KedLexer(Lexer):
    # pyright: reportUndefinedVariable=false

    # Set of token names. This is always required
    tokens = {
        NUMBER,
        STRING,
        NAME,
        VARIABLE,
        IF,
        ELIF,
        ELSE,
        WHILE,
        BREAK,
        CONTINUE,
        RETURN,
        NULL,
        TRUE,
        FALSE,
        NOT,
        AND,
        OR,
        PLUS,
        MINUS,
        TIMES,
        DIVIDE,
        MOD,
        EQ,
        STRICTEQ,
        CONCAT,
        DECLARE,
        UNDECLARE,
        IS_DECLARED,
        LIKE,
        PRINT,
        SLEEP,
        NOOP,
        IMPORT,
        STRICT_IMPORT,
        EXIT,
    }

    literals = {"(", ")", "{", "}", "=", "+", "-", ",", "!"}

    # String containing ignored characters
    ignore = " \t"

    # Conditionals
    IF = r"eh"
    ELIF = r"orEh"
    ELSE = r"orEvenJust"

    # Loops
    WHILE = r"eraGoOnSure"
    BREAK = r"ahStop"
    CONTINUE = r"ahGoOn"
    RETURN = r"return"

    # Boolean operators
    NOT = r"not"
    AND = r"an"
    OR = r"or"

    # Arithmetic operators
    PLUS = r"plus"
    MINUS = r"awayFrom"
    TIMES = r"times"
    DIVIDE = r"into"
    MOD = r"mod"

    # Comparison operators
    STRICTEQ = r"isTheHeadOff|isTheAbsoluteHeadOff"
    EQ = r"is"

    # Import keywords
    IMPORT = r"hereLa"
    STRICT_IMPORT = r"cmereToMeWilla"

    # String operators
    CONCAT = r"em"

    # Variables
    DECLARE = r"remember"
    UNDECLARE = r"forget"
    IS_DECLARED = r"jaKnow"

    # Utilities
    LIKE = r"like"
    PRINT = r"saysI"
    SLEEP = r"holdOn"
    NOOP = r"iWillYa|yaTwoMinutesThereNow"
    EXIT = r"stopTheLights"

    # Constants
    @_(r"nattin")
    def NULL(self, t: Token) -> Token:
        t.value = None
        return t

    @_(r"gospel")
    def TRUE(self, t: Token) -> Token:
        t.value = True
        return t

    @_(r"bull")
    def FALSE(self, t: Token) -> Token:
        t.value = False
        return t

    @_(r"'.*?'")
    def STRING(self, t: Token) -> Token:
        t.value = t.value[1:-1]
        return t

    @_(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
    def NUMBER(self, t: Token) -> Token:
        t.value = float(t.value)
        return t

    # Identifiers
    NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"
    VARIABLE = r"€[a-zA-Z_][a-zA-Z0-9_]*"

    ignore_comment = r"//.*"

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print("Line %d: Bad character %r" % (self.lineno, t.value[0]))
        self.index += 1
