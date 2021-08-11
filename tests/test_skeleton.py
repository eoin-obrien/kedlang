# -*- coding: utf-8 -*-

import pytest
from kedlang.skeleton import fib

__author__ = "Eoin O'Brien"
__copyright__ = "Eoin O'Brien"
__license__ = "gpl3"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
