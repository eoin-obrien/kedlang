class SemanticError(Exception):
    pass


class Break(Exception):
    pass


class Continue(Exception):
    pass


class Return(Exception):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class Exit(Exception):
    pass
