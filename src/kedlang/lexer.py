from sly import Lexer
from sly.lex import Token


def find_column(text: str, token: Token):
    last_cr = text.rfind("\n", 0, token.index)
    if last_cr < 0:
        last_cr = 0
    column = (token.index - last_cr) + 1
    return column


class KedLexer(Lexer):
    # pyright: reportUndefinedVariable=false

    # Set of token names. This is always required
    tokens = {
        NUMBER,
        STRING,
        NAME,
        VARIABLE,
        SCOPE_RESOLUTION,
        SPREAD,
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
        LT,
        LTE,
        GT,
        GTE,
        EQ,
        STRICTEQ,
        CONCAT,
        DECLARE,
        UNDECLARE,
        IS_DECLARED,
        LIKE,
        PRINT,
        INPUT,
        SLEEP,
        NOOP,
        IMPORT,
        STRICT_IMPORT,
        EXIT,
        CLASS,
        EXTENDS,
        NEW,
        STATIC,
        TRY,
        CATCH,
        FINALLY,
        THROW,
    }

    literals = {"(", ")", "[", "]", "{", "}", "=", "+", "-", ".", ",", "!"}

    # String containing ignored characters
    ignore = " \t"

    SCOPE_RESOLUTION = r"::"
    SPREAD = r"\.\.\."

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

    # Identifiers
    NAME = r"[a-zA-Z_][a-zA-Z0-9_]*"
    VARIABLE = r"€[a-zA-Z_][a-zA-Z0-9_]*"

    # Classes
    NAME[r"new"] = NEW
    NAME[r"class"] = CLASS
    NAME[r"isTheBulbOff"] = EXTENDS
    NAME[r"static"] = STATIC

    # Exception handling
    NAME[r"giveItALash"] = TRY
    NAME[r"jaHearYourMan"] = CATCH
    NAME[r"atTheEndOfTheDay"] = FINALLY
    NAME[r"release"] = THROW

    # Conditionals
    NAME[r"eh"] = IF
    NAME[r"orEh"] = ELIF
    NAME[r"orEvenJust"] = ELSE

    # Loops
    NAME[r"eraGoOnSure"] = WHILE
    NAME[r"ahStop"] = BREAK
    NAME[r"ahGoOn"] = CONTINUE
    NAME[r"return"] = RETURN

    # Boolean operators
    NAME[r"not"] = NOT
    NAME[r"an"] = AND
    NAME[r"or"] = OR

    # Arithmetic operators
    NAME[r"plus"] = PLUS
    NAME[r"awayFrom"] = MINUS
    NAME[r"times"] = TIMES
    NAME[r"into"] = DIVIDE
    NAME[r"mod"] = MOD

    # Relational operators
    NAME[r"isDoonshierThanOrIs"] = LTE
    NAME[r"isDoonshierThan"] = LT
    NAME[r"isLankierThanOrIs"] = GTE
    NAME[r"isLankierThan"] = GT

    # Comparison operators
    NAME[r"isTheHeadOff"] = STRICTEQ
    NAME[r"isTheAbsoluteHeadOff"] = STRICTEQ
    NAME[r"is"] = EQ

    # Import keywords
    NAME[r"hereLa"] = IMPORT
    NAME[r"cmereToMeWilla"] = STRICT_IMPORT

    # String operators
    NAME[r"em"] = CONCAT

    # Variables
    NAME[r"remember"] = DECLARE
    NAME[r"forget"] = UNDECLARE
    NAME[r"jaKnow"] = IS_DECLARED

    # Utilities
    NAME[r"like"] = LIKE
    NAME[r"saysI"] = PRINT
    NAME[r"storyBoi"] = INPUT
    NAME[r"holdOn"] = SLEEP
    NAME[r"iWillYa"] = NOOP
    NAME[r"yaTwoMinutesThereNow"] = NOOP
    NAME[r"stopTheLights"] = EXIT

    @_(r"'.*?'")
    @_(r'".*?"')
    def STRING(self, t: Token) -> Token:
        t.value = (
            t.value[1:-1].encode("latin-1", "backslashreplace").decode("unicode-escape")
        )
        return t

    @_(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
    def NUMBER(self, t: Token) -> Token:
        t.value = float(t.value)
        return t

    ignore_comment = r"//.*"

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t: Token):
        print("Line %d: Bad character %r" % (self.lineno, t.value[0]))
        self.index += 1
        return t
