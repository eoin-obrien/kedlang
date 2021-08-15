import functools
from typing import Any, Optional, Union

from kedlang.exceptions import KedSemanticError
from kedlang.symbol import Symbol


def check_key(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = args[1]
        if not isinstance(key, Symbol):
            raise TypeError(f"Frame keys must be of type 'Symbol', got '{type(key)}'")
        return func(*args, **kwargs)

    return wrapper


class Frame:
    def __init__(self, name: str, parent: Optional["Frame"] = None) -> None:
        self.__name = name
        self.__parent = parent
        self._members = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__name}>"

    def __contains__(self, key) -> bool:
        return (
            key in self._members or self.__parent is not None and key in self.__parent
        )

    @check_key
    def declare(self, key: Union[Symbol, str], value=None) -> None:
        if key in self._members:
            raise KedSemanticError(
                f"Symbol {key} has already been declared in scope {self}"
            )
        self._members[key] = value

    @check_key
    def fetch(self, key: Union[Symbol, str]) -> Any:
        if key in self._members:
            return self._members[key]
        elif self.__parent is not None:
            return self.__parent.fetch(key)
        else:
            raise KedSemanticError(f"Symbol {key} does not exist in scope {self}")

    @check_key
    def assign(self, key: Union[Symbol, str], value: Any) -> None:
        if key in self._members:
            self._members[key] = value
        elif self.__parent is not None:
            self.__parent.assign(key, value)
        else:
            raise KedSemanticError(f"Symbol {key} does not exist in scope {self}")

    @check_key
    def delete(self, key: Union[Symbol, str]) -> None:
        if key in self._members:
            del self._members[key]
        elif self.__parent is not None:
            self.__parent.delete(key)
        else:
            raise KedSemanticError(f"Symbol {key} does not exist in scope {self}")


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
