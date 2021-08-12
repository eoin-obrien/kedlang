from typing import Any, Optional, Union

from kedlang.exception import SemanticError
from kedlang.symbol import Symbol


class Frame:
    def __init__(self, name: str, parent: Optional["Frame"] = None) -> None:
        self.__name = name
        self.__parent = parent
        self._members = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__name}>"

    def declare(self, key: Union[Symbol, str], value=None) -> None:
        key = str(key)
        if key in self._members:
            raise SemanticError(
                f"Symbol {key} has already been declared in scope {self}"
            )
        self._members[key] = value

    def fetch(self, key: Union[Symbol, str]) -> Any:
        key = str(key)
        if key in self._members:
            return self._members[key]
        elif self.__parent is not None:
            return self.__parent.fetch(key)
        else:
            raise SemanticError(f"Symbol {key} does not exist in scope {self}")

    def assign(self, key: Union[Symbol, str], value: Any) -> None:
        key = str(key)
        if key in self._members:
            self._members[key] = value
        elif self.__parent is not None:
            self.__parent.assign(key, value)
        else:
            raise SemanticError(f"Symbol {key} does not exist in scope {self}")

    def delete(self, key: Union[Symbol, str]) -> None:
        key = str(key)
        if key in self._members:
            del self._members[key]
        elif self.__parent is not None:
            self.__parent.delete(key)
        else:
            raise SemanticError(f"Symbol {key} does not exist in scope {self}")


class CallStack:
    def __init__(self) -> None:
        self._frames = []

    def __repr__(self) -> str:
        return f"<CallStack {self._frames}>"

    def push(self, frame: Frame) -> None:
        self._frames.append(frame)

    def pop(self) -> Frame:
        return self._frames.pop()

    def peek(self) -> Frame:
        return self._frames[-1]
