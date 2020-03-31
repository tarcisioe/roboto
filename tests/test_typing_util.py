"""Tests for the roboto.typing_util module."""
from dataclasses import dataclass
from typing import List, NewType

from roboto.typing_util import is_new_type, original_type, type_name

Alias = NewType('Alias', int)


def test_is_new_type():
    """Ensure `is_new_type` correctly detects `NewType`s."""
    assert is_new_type(Alias)
    assert not is_new_type(int)


def test_original_type():
    """Ensure `original_type` can get the original type of a NewType."""
    assert original_type(Alias) is int


def test_type_name():
    """Ensure `original_type` can get the original type of a NewType."""

    @dataclass
    class _Named:
        pass

    assert type_name(int) == 'int'
    assert type_name(List[int]) == 'typing.List[int]'
    assert type_name(_Named) == '_Named'
