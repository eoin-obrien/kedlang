from typing import Any, Callable, Dict, Optional


class KedBoolean:
    def __init__(self, value: Optional[Any]) -> None:
        self.value = bool(value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.value}>"

    def __str__(self) -> str:
        return "gospel" if self.value else "bull"

    def __int__(self, other):
        return int(self.value)

    def __and__(self, other):
        return self.value and other

    def __or__(self, other):
        return self.value or other


class KedFunction:
    def __init__(self, impl: Callable) -> None:
        self.impl = impl

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.impl.__name__}>"

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.impl(args, kwds)


class KedClass:
    def __init__(self, name, base, body) -> None:
        self.name, self.base, self.body = name, base, body


class KedObject:
    def __init__(self, class_type: KedClass, members: Optional[Dict] = None) -> None:
        self.class_type = class_type
        self.members = members or {}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.class_type.name} {self.members}>"

    def __getitem__(self, key) -> Any:
        return self.members[key]

    def __setitem__(self, key, value) -> None:
        self.members[key] = value
