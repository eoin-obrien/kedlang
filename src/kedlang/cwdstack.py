import os


class CWDStack:
    def __init__(self) -> None:
        self._stack = []

    def __repr__(self) -> str:
        return f"<CallStack {self._stack}>"

    def push(self, path: str) -> None:
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        self._stack.append(path)

    def pop(self) -> str:
        return self._stack.pop()

    def peek(self) -> str:
        return self._stack[-1]
