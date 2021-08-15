from typing import Dict, Optional


class Symbol:
    def __init__(self, name: str) -> None:
        self.__name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, o: object) -> bool:
        return self.name == o.name

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def name(self) -> str:
        return self.__name


class Namespace:
    NamespaceDict = Dict[str, Symbol]

    def __init__(self, class_type, members: Optional[NamespaceDict] = None) -> None:
        self.class_type = class_type
        self.members = members or {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.members}>"

    def __getitem__(self, key: str) -> Symbol:
        return self.members[key]

    def __setitem__(self, key: str, value: Symbol) -> None:
        self.members[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.members

    def __iter__(self):
        return self.members.__iter__()

    @property
    def name(self) -> str:
        return hex(id(self))


class NamespacedSymbol(Symbol):
    def __init__(self, name: str, namespace: Namespace) -> None:
        self.__name = f"{namespace.name}:{name}"

    @property
    def name(self) -> str:
        return self.__name
