"""Utilities for use with the `typing` module."""

from typing import Any, Dict, Type, TypeVar, Union

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


TypeHint = Union[str, Type[T]]


def evaluate_type(type_hint: TypeHint[T], context: Dict[str, Any]) -> Type[T]:
    """Evaluate a type hint even if it is given as a string.

    """
    if not isinstance(type_hint, str):
        return type_hint

    return eval(type_hint, context)  # pylint: disable=eval-used
