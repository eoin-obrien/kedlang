import enum
from typing import Optional


class Symbol:
    def __init__(self, name: str) -> None:
        self.__name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__name}>"

    @property
    def name(self) -> str:
        return self.__name


class SymbolTableType(enum.Enum):
    MODULE = enum.auto()
    FUNCTION = enum.auto()
    CLASS = enum.auto()


class SymbolTable:
    def __init__(
        self, name: str, type: SymbolTableType, parent: Optional["SymbolTable"] = None
    ) -> None:
        self.__name = name
        self.__type = type
        self.__parent = parent
        self._symbols = {}

    def __repr__(self) -> str:
        if self.__type == SymbolTableType.MODULE:
            kind = "Module"
        if self.__type == SymbolTableType.FUNCTION:
            kind = "Function"
        if self.__type == SymbolTableType.CLASS:
            kind = "Class"
        return f"<{kind}{self.__class__.__name__} {self.__name}>"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> SymbolTableType:
        return self.__type

    @property
    def parent(self) -> Optional["SymbolTable"]:
        return self.__parent

    def insert(self, symbol: Symbol):
        self._symbols[symbol.name] = symbol

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        symbol = self._symbols.get(name)

        if symbol is not None or current_scope_only:
            return symbol

        if self.__parent is not None:
            return self.__parent.lookup(name)


print(Symbol("x"))
