from typing import Dict, Optional, Union


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
    NamespaceDict = Dict[Union[str, int], Symbol]

    __next_unique_id = 0

    @classmethod
    def get_unique_id(cls) -> int:
        unique_id = cls.__next_unique_id
        cls.__next_unique_id += 1
        return unique_id

    def __init__(self, members: Optional[NamespaceDict] = None) -> None:
        self.members = members or {}
        self.unique_id = self.get_unique_id()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.members}>"

    def __getitem__(self, key) -> Symbol:
        return self.members[key]

    def __setitem__(self, key, value: Symbol) -> None:
        self.members[key] = value

    def __contains__(self, key) -> bool:
        return key in self.members

    def __iter__(self):
        return self.members.__iter__()

    @property
    def name(self) -> str:
        return hex(self.unique_id)


class NamespacedSymbol(Symbol):
    def __init__(self, name: str, namespace: Namespace) -> None:
        self.__name = f"{namespace.name}:{name}"

    @property
    def name(self) -> str:
        return self.__name
