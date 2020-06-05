"""Utilities for use with the `typing` module."""

from typing import Type, TypeVar

T = TypeVar('T')


def is_none_type(tp: Type[T]) -> bool:
    """Check if a type is NoneType (type(None))."""
    return tp is type(None)  # noqa


def is_new_type(tp: Type[T]) -> bool:
    """Check if a given type is a NewType strong type alias."""
    return getattr(tp, '__supertype__', None) is not None


def original_type(tp: Type[T]) -> type:
    """Return the base type of a strong type alias.

    Args:
        tp: A NewType type-alias.

    Returns:
        The underlying type of the type-alias.
    """
    return tp.__supertype__  # type: ignore


def type_name(tp: Type[T]) -> str:
    """Get the name of a type, without <class ...>.

    Args:
        tp: A type.

    Return:
        The name of the type, without repr/str noise.
    """
    if isinstance(tp, type):
        return tp.__name__
    return str(tp)
