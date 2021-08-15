from typing import Any, Callable, Optional

from kedlang.exceptions import KedSemanticError
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
        self.namespace = Namespace()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __str__(self) -> str:
        return f"[class {self.name}]"

    def __getitem__(self, key) -> Any:
        if key in self.namespace:
            return self.namespace[key]
        elif self.base is not None:
            return self.base[key]
        else:
            raise KedSemanticError(f"Static attribute {key} does not exist on {self}")

    def __setitem__(self, key, value) -> None:
        self.namespace[key] = value

    def __contains__(self, key) -> bool:
        return key in self.namespace

    def extends(self, class_type: "KedClass") -> bool:
        return (
            self == class_type
            or self.base is not None
            and self.base.extends(class_type)
        )


class KedObject:
    def __init__(self, class_type: KedClass) -> None:
        self.class_type = class_type
        self.namespace = Namespace()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.class_type.name}>"

    def __str__(self) -> str:
        return f"[thing {self.class_type.name}]"

    def __getitem__(self, key) -> Any:
        return self.namespace[key]

    def __setitem__(self, key, value) -> None:
        self.namespace[key] = value

    def __contains__(self, key) -> bool:
        return key in self.namespace

    def extends(self, class_type: KedClass) -> bool:
        return self.class_type.extends(class_type)

    @property
    def name(self):
        return self.namespace.name


class KedList:
    def __init__(self, size=0) -> None:
        self.namespace = Namespace()
        self.elements = [None] * size

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.elements}>"

    def __getitem__(self, key) -> Any:
        return self.elements[key]

    def __setitem__(self, key, value) -> None:
        self.elements[key] = value

    def __contains__(self, key) -> bool:
        return key in self.elements

    def __len__(self) -> int:
        return len(self.elements)

    def extends(self, class_type: KedClass) -> bool:
        return self.class_type.extends(class_type)

    @property
    def name(self):
        return self.namespace.name
