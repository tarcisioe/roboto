"""Utilities from deserializing values as dataclasses."""
from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    get_type_hints,
    overload,
)

from typing_extensions import Literal
from typing_inspect import get_args, get_origin, is_optional_type

from .error import RobotoError
from .typing_util import is_new_type, is_none_type, original_type, type_name

T = TypeVar('T')

JSONPrimitives = Optional[Union[int, float, str, bool]]
JSONLike = Union[JSONPrimitives, Dict[str, Any], List[Any]]


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


def from_list(tp: Type[List[T]], v: List[Any]) -> List[T]:
    """Transform a list of JSON-like structures into JSON-compatible objects."""
    (inner_type,) = get_args(tp)
    return [_from_json_like(inner_type, value) for value in v]


def from_dict(tp: Type[T], v: Dict[str, Any]) -> T:
    """Transform a JSON-like structure into a JSON-compatible dataclass."""
    field_renames = renames(tp)

    type_hints = get_type_hints(tp)

    for k in field_renames:
        if k in v:
            v[field_renames[k]] = v.pop(k)

    return tp(  # type: ignore
        **{
            field_name: _from_json_like(type_hints[field_name], value)
            for field_name, value in v.items()
            if field_name in type_hints
        }
    )


class JSONConversionError(RobotoError):
    """Signal error trying to read JSON-like data into a given type."""

    def __init__(self, message, schema_class, value):
        super().__init__(message)
        self.schema_class = schema_class
        self.value = value


def convert_single(tp: Type[T], v: Any) -> T:
    """Convert a value into a single (non-list) type."""
    if tp in (int, float):
        if not isinstance(v, (int, float)):
            raise JSONConversionError(f'Cannot read value {v} as a number.', tp, v)

        return tp(v)  # type: ignore

    if is_dataclass(tp):
        if not isinstance(v, dict):
            raise JSONConversionError(
                f'Cannot read non-dict {v} as dataclass type {tp}.', tp, v,
            )

        return from_dict(tp, v)

    real_type = tp if not is_new_type(tp) else original_type(tp)

    if not isinstance(v, real_type):
        raise JSONConversionError(
            f'Cannot find any way to read value {v} as {tp}.', tp, v
        )

    return cast(T, v)


def _from_json_like(type_hint, value):
    optional = is_optional_type(type_hint)

    (real_type,) = (
        (t for t in get_args(type_hint) if not is_none_type(t))
        if optional
        else (type_hint,)
    )

    if real_type is Any:
        return value

    return from_json_like(real_type, value, optional)


@overload
def from_json_like(
    tp: Type[List[T]], value: List[JSONLike], optional: Literal[True],
) -> Optional[List[T]]:  # pragma: no cover
    """Overload for from_json_like, refer to implementation."""
    ...


@overload
def from_json_like(
    tp: Type[T], value: JSONLike, optional: Literal[True],
) -> Optional[T]:  # pragma: no cover
    """Overload for from_json_like, refer to implementation."""
    ...


@overload
def from_json_like(
    tp: Type[List[T]], value: List[JSONLike], optional: Literal[False] = False,
) -> List[T]:  # pragma: no cover
    """Overload for from_json_like, refer to implementation."""
    ...


@overload
def from_json_like(
    tp: Type[T], value: JSONLike, optional: Literal[False] = False,
) -> T:  # pragma: no cover
    """Overload for from_json_like, refer to implementation."""
    ...


def from_json_like(tp: Type[T], value: Any, optional: bool = False) -> Optional[T]:
    """Read a JSON-like object into a given schema type.

    `tp` must be:
        - a JSON primitive type (int, float, str, bool or NoneType),
        - a List[T] of a JSON-compatible type, or
        - a dataclass where every field is of a JSON-compatible type

    Args:
        tp: A JSON-compatible type.
        value: A JSON-compatible value to read.
        optional: Whether None should be accepted.

    Returns:
        An object of the type given by `tp`, or maybe None if `optional` is `True`.
    """

    if value is None:
        if not optional:
            raise JSONConversionError(
                'Cannot read None as a non optional value.', tp, value
            )

        return None

    if get_origin(tp) is list:
        if not isinstance(value, list):
            raise JSONConversionError(
                'Cannot read non-list value to a list type.', tp, value
            )
        return from_list(tp, value)  # type: ignore

    return convert_single(tp, value)


def to_json_like(obj: Any) -> JSONLike:
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
        return {k: to_json_like(v) for k, v in obj.items() if v is not None}
    if is_dataclass(obj):
        return {k: to_json_like(v) for k, v in asdict(obj).items() if v is not None}
    if isinstance(obj, list):
        return [to_json_like(v) for v in obj]
    if isinstance(obj, Enum):
        return to_json_like(obj.value)

    obj_type = type(obj)

    raise JSONConversionError(
        f'Failed to turn value of type {type_name(obj_type)} into a JSONLike.',
        obj_type,
        obj,
    )
