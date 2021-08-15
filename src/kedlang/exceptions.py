class BaseKedException(Exception):
    """Base class for Ked exceptions."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class KedControlFlow(Exception):
    """Implements control flow statements."""

    pass


class KedSemanticError(BaseKedException):
    """Semantic error."""

    pass


class KedSyntaxError(BaseKedException):
    """Syntax error."""

    pass


class KedImportError(BaseKedException):
    """Import error."""

    pass


class Break(KedControlFlow):
    """Break statement."""

    pass


class Continue(KedControlFlow):
    """Continue statement."""

    pass


class Return(KedControlFlow):
    """Return statement."""

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value


class Exit(KedControlFlow):
    """Exit statement."""

    pass


class KedException(BaseKedException):
    """Wrapper class for Rebels."""

    def __init__(self, message, value) -> None:
        super().__init__(message)
        self.value = value
