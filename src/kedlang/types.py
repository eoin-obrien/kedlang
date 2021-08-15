from typing import Any, Callable, Dict, Optional

from kedlang.exception import SemanticError
from kedlang.symbol import Namespace


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

    def __str__(self) -> str:
        return f"[function {self.impl.__name__}]"

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.impl(*args, **kwds)


class KedClass:
    def __init__(self, name, base, body) -> None:
        self.name, self.base, self.body = name, base, body
        self.statics = Namespace(self)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __str__(self) -> str:
        return f"[class {self.name}]"

    def __getitem__(self, key) -> Any:
        if key in self.statics:
            return self.statics[key]
        elif self.base is not None:
            return self.base[key]
        else:
            raise SemanticError(f"Static attribute {key} does not exist on {self}")

    def __setitem__(self, key, value) -> None:
        self.statics[key] = value

    def __contains__(self, key) -> bool:
        return key in self.statics


class KedObject:
    def __init__(self, class_type: KedClass) -> None:
        self.class_type = class_type
        self.attributes = Namespace(class_type)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.class_type.name}>"

    def __str__(self) -> str:
        return f"[thing {self.class_type.name}]"

    def __getitem__(self, key) -> Any:
        return self.attributes[key]

    def __setitem__(self, key, value) -> None:
        self.attributes[key] = value

    @property
    def name(self):
        return self.attributes.name
