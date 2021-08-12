class Symbol:
    def __init__(self, name: str) -> None:
        self.__name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__name}>"

    def __str__(self) -> str:
        return self.__name

    @property
    def name(self) -> str:
        return self.__name
