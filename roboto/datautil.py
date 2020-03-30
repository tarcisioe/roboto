"""Utilities from deserializing values as dataclasses."""
import sys
from dataclasses import Field, fields, is_dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, overload

from typing_extensions import Protocol, runtime_checkable
from typing_inspect import get_args, get_origin, is_optional_type

from .error import RobotoError

T = TypeVar('T')

Number = Union[int, float]
JSONPrimitives = Optional[Union[Number, str, bool, None]]
JSONLike = Union[JSONPrimitives, Dict[str, Any], List[Any]]


@runtime_checkable
class Dataclass(Protocol):
    """A class that is a dataclass."""

    __dataclass_fields__: Dict[str, Field]


def renames(cls: Type[Dataclass]) -> Dict[str, str]:
    """Get all renames from a dataclass."""
    return {
        field.name: field.metadata['rename']
        for field in fields(cls)
        if 'rename' in field.metadata
    }


def is_new_type(tp) -> bool:
    """Check if a given type is a NewType strong type alias."""
    return getattr(tp, '__supertype__', None) is not None


def original_type(tp) -> type:
    """Return the base type of a strong type alias.

    Args:
        tp: A NewType type-alias.

    Returns:
        The underlying type of the type-alias.
    """
    return tp.__supertype__


TypeHint = Union[str, type]


def field_type(cls: Type[Dataclass], field_name: str) -> type:
    """Get the type of a field from a dataclass."""
    candidate: TypeHint = cls.__dataclass_fields__[field_name].type

    def evaluate_type(type_annotation: str) -> type:
        return eval(  # pylint: disable=eval-used
            type_annotation, vars(sys.modules[cls.__module__]),
        )

    return evaluate_type(candidate) if isinstance(candidate, str) else candidate


def from_list(list_type: Type[List[T]], v: List[JSONLike]) -> List[T]:
    """Transform a list of JSON-like structures into JSON-compatible objects."""
    (inner_type,) = get_args(list_type)
    return [from_json(inner_type, value) for value in v]


def from_dict(cls: Type[Dataclass], d: Dict[str, JSONLike]):
    """Transform a JSON-like structure into a JSON-compatible dataclass."""
    field_renames = renames(cls)

    for k in d:
        if k in field_renames:
            d[field_renames[k]] = d.pop(k)

    return cls(
        **{
            k: from_json(field_type(cls, k), v)
            for k, v in d.items()
            if k in cls.__dataclass_fields__
        }
    )  # type: ignore


class JSONConversionError(RobotoError):
    """Signal error trying to read JSON-like data into a given type."""

    def __init__(self, message, schema_class, value):
        super().__init__(message)
        self.schema_class = schema_class
        self.value = value


@overload
def from_json(schema_class: Type[List[T]], j: JSONLike) -> List[T]:
    """Overload declaration of from_json."""
    ...


@overload
def from_json(schema_class: Type[T], j: JSONLike) -> T:
    """Overload declaration of from_json."""
    ...


@overload
def from_json(schema_class: None, j: JSONLike) -> None:
    """Overload declaration of from_json."""
    ...


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
    if schema_class is Any:
        return j

    optional = is_optional_type(schema_class)

    def resolve_type(schema_class):
        (strict_type,) = (
            [t for t in get_args(schema_class) if not isinstance(None, t)]
            if optional
            else (schema_class,)
        )

        if is_new_type(strict_type):
            return original_type(strict_type)

        return strict_type

    strict_type = resolve_type(schema_class)

    strict_type_name = strict_type.__name__
    type_name = strict_type_name if not optional else f'Optional[{strict_type_name}]'

    if j is None:
        if optional:
            return None

        raise JSONConversionError(
            f'Cannot read None into non-optional type {type_name}.', schema_class, j,
        )

    if isinstance(j, get_args(JSONPrimitives)):  # type: ignore
        if isinstance(j, strict_type):
            return j

        if isinstance(j, get_args(Number)):  # type: ignore
            if strict_type in get_args(Number):  # type: ignore
                return schema_class(j)

        raise JSONConversionError(
            f'Cannot read primitive value {j} into non-primitive type {type_name}.',
            schema_class,
            j,
        )

    if isinstance(j, dict):
        if is_dataclass(schema_class):
            return from_dict(strict_type, j)

        raise JSONConversionError(
            f'Cannot read dictionary into non-dataclass type {type_name}.',
            schema_class,
            j,
        )

    if isinstance(j, list):
        if get_origin(strict_type) is list:
            return from_list(strict_type, j)

        raise JSONConversionError(
            f'Failed to read value into type {type_name}.', schema_class, j,
        )

    raise JSONConversionError(
        f'Failed to read value into type {type_name}.', schema_class, j,
    )
