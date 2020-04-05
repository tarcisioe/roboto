"""Utilities from deserializing values as dataclasses."""
import sys
from dataclasses import Field, asdict, fields, is_dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast, overload

from typing_extensions import Protocol
from typing_inspect import get_args, get_origin, is_optional_type

from .error import RobotoError
from .typing_util import (
    evaluate_type,
    is_new_type,
    is_none_type,
    original_type,
    type_name,
)

T = TypeVar('T')

Number = Union[int, float]
JSONPrimitives = Optional[Union[Number, str, bool]]
JSONLike = Union[JSONPrimitives, Dict[str, Any], List[Any]]


class Dataclass(Protocol):
    """Protocol for a dataclass instance or type."""

    __dataclass_fields__: Dict[str, Field]


def renames(cls: Type[T]) -> Dict[str, str]:
    """Get all serialization renames from a dataclass.

    `cls` is expected to be a Dataclass type.

    Args:
        cls: A dataclass type.

    Return:
        A mapping of class attribute names to the name they expect when
        deserializing.
    """
    return {
        field.metadata['rename']: field.name
        for field in fields(cls)
        if 'rename' in field.metadata
    }


def field_type(cls: Type[T], field_name: str) -> type:
    """Get the type of a field from a dataclass.

    `cls` is expected to be a dataclass type.

    Args:
        cls: A dataclass type.
        field_name: The name of the field to query the type of.

    Returns:
        The type of the requested field.
    """
    as_dataclass = cast(Dataclass, cls)

    tp = as_dataclass.__dataclass_fields__[field_name].type
    return evaluate_type(tp, vars(sys.modules[cls.__module__]))


def from_list(list_type: Type[List[T]], v: List[JSONLike]) -> List[T]:
    """Transform a list of JSON-like structures into JSON-compatible objects."""
    (inner_type,) = get_args(list_type)
    return [from_json(inner_type, value) for value in v]


def from_dict(cls: Type[T], d: Dict[str, JSONLike]):
    """Transform a JSON-like structure into a JSON-compatible dataclass."""
    field_renames = renames(cls)

    as_dataclass = cast(Dataclass, cls)

    for k in field_renames:
        if k in d:
            d[field_renames[k]] = d.pop(k)

    return cls(  # type: ignore
        **{
            k: from_json(field_type(cls, k), v)
            for k, v in d.items()
            if k in as_dataclass.__dataclass_fields__
        }
    )


class JSONConversionError(RobotoError):
    """Signal error trying to read JSON-like data into a given type."""

    def __init__(self, message, schema_class, value):
        super().__init__(message)
        self.schema_class = schema_class
        self.value = value


@overload
def from_json(schema_class: Type[List[T]], j: JSONLike) -> List[T]:
    """Overload declaration of from_json."""
    ...  # pragma: no cover


@overload
def from_json(schema_class: Type[T], j: JSONLike) -> T:
    """Overload declaration of from_json."""
    ...  # pragma: no cover


@overload
def from_json(schema_class: None, j: JSONLike) -> None:
    """Overload declaration of from_json."""
    ...  # pragma: no cover


def from_json(schema_class, j):
    """Read a JSON-like object into a given schema type.

    `schema_class` must be:
        - a JSON primitive type (int, float, str, bool or NoneType),
        - a List[T] of a JSON-compatible type, or
        - a dataclass where every field is of a JSON-compatible type, or
        - an Optional of a JSON-compatible type.

    Args:
        schema_class: A JSON-compatible type.
        j: A JSON-compatible value to read.

    Returns:
        An object of the type given by `schema_class`.
    """
    optional = is_optional_type(schema_class)

    def resolve_type(schema_class):
        (strict_type,) = (
            [t for t in get_args(schema_class) if not is_none_type(t)]
            if optional
            else (schema_class,)
        )

        if is_new_type(strict_type):
            return original_type(strict_type)

        return strict_type

    strict_type = resolve_type(schema_class)

    if strict_type is Any:
        return j

    strict_type_name = type_name(strict_type)
    schema_class_name = (
        strict_type_name if not optional else f'Optional[{strict_type_name}]'
    )

    if j is None:
        if optional:
            return None

        raise JSONConversionError(
            f'Cannot read None into non-optional type {schema_class_name}.',
            schema_class,
            j,
        )

    if isinstance(j, get_args(JSONPrimitives)):  # type: ignore
        if isinstance(j, strict_type):
            return j

        if isinstance(j, get_args(Number)):  # type: ignore
            if strict_type in get_args(Number):  # type: ignore
                return schema_class(j)

        raise JSONConversionError(
            'Cannot read primitive value {j} into non-primitive type '
            f'{schema_class_name}.',
            schema_class,
            j,
        )

    if isinstance(j, dict):
        if is_dataclass(strict_type):
            return from_dict(strict_type, j)

        raise JSONConversionError(
            f'Cannot read dictionary into non-dataclass type {schema_class_name}.',
            schema_class,
            j,
        )

    if isinstance(j, list):
        if get_origin(strict_type) is list:
            return from_list(strict_type, j)

        raise JSONConversionError(
            f'Failed to read list of types into non-list type {schema_class_name}.',
            schema_class,
            j,
        )

    raise JSONConversionError(
        f'Failed to read value into type {schema_class_name}.', schema_class, j,
    )


def to_json(obj: Any) -> JSONLike:
    """Serialize an object to a JSON-compatible representation.

    `obj` must be:
        - a JSON primitive (int, float, str, bool or None),
        - an object of a dataclass where every field is JSON-compatible, or
        - a list of JSON-compatible objects.

    Args:
        obj: The object to serialize.

    Returns:
        A representation that can be converted to JSON.
    """
    if isinstance(obj, get_args(JSONPrimitives)):  # type: ignore
        return obj
    if isinstance(obj, dict):
        return {k: to_json(v) for k, v in obj.items() if v is not None}
    if is_dataclass(obj):
        return {k: to_json(v) for k, v in asdict(obj).items() if v is not None}
    if isinstance(obj, List):
        return [to_json(v) for v in obj]
    if isinstance(obj, Enum):
        return to_json(obj.value)

    obj_type = type(obj)

    raise JSONConversionError(
        f'Failed to turn value of type {type_name(obj_type)} into a JSONLike.',
        obj_type,
        obj,
    )
