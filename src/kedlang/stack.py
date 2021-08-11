import enum
from typing import Any, Optional

from . import builtins


class Frame:
    def __init__(self, name: str, parent: Optional["Frame"] = None) -> None:
        self.__name = name
        self.__parent = parent
        self._members = {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__name}>"

    def __getitem__(self, key):
        if key in self._members:
            return self._members[key]
        elif self.__parent is not None:
            return self.__parent[key]
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        self._members[key] = value

    def __delitem__(self, key):
        if key in self._members:
            del self._members[key]
        elif self.__parent is not None:
            del self.__parent[key]
        else:
            raise KeyError(key)

    def __contains__(self, key):
        return key in self._members


class GlobalFrame(Frame):
    def __init__(self, name: str) -> None:
        super().__init__(name, parent=None)

        # Init global frame with builtins
        self["boolean"] = builtins.to_ked_boolean
        self["number"] = builtins.to_ked_number
        self["string"] = builtins.to_ked_string


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
