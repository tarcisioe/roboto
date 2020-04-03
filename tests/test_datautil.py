"""Tests for the roboto.datautil module."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, NewType, Optional

from pytest import raises

from roboto.datautil import (
    JSONConversionError,
    field_type,
    from_dict,
    from_json,
    from_list,
    renames,
    to_json,
)


def test_renames() -> None:
    """Test that the `renames` function gathers all renames."""

    @dataclass
    class _Renamed:
        a: int
        b: str = field(metadata={'rename': 'x'})
        c: float = field(metadata={'rename': 'y'})
        d: int = 5

    assert renames(_Renamed) == {'x': 'b', 'y': 'c'}


def test_field_type() -> None:
    """Test that the `renames` function gathers the correct type

    The type must be properly evaluated if defined as a string (or if delayed
    evaluation is on)."""

    @dataclass
    class _DummyType:
        a: int
        b: 'str'
        c: float
        d: int = 5

    assert field_type(_DummyType, 'a') is int
    assert field_type(_DummyType, 'b') is str


def test_from_dict() -> None:
    """Test `from_list` with different types."""

    @dataclass
    class _SmallDummyType:
        a: int
        b: str

    assert from_dict(_SmallDummyType, {'a': 1, 'b': 'test'},) == _SmallDummyType(
        1, 'test'
    )

    @dataclass
    class _Renamed:
        a: int
        from_: str = field(metadata={'rename': 'from'})

    assert from_dict(_Renamed, {'a': 1, 'from': 'test'},) == _Renamed(1, 'test')


def test_from_list() -> None:
    """Test `from_list` with different types."""
    assert from_list(List[int], [1, 2, 3]) == [1, 2, 3]

    @dataclass
    class _SmallDummyType:
        a: int
        b: str

    assert from_list(
        List[_SmallDummyType],
        [{'a': 1, 'b': 'test'}, {'a': 2, 'b': 'test2'}, {'a': 42, 'b': 'test'}],
    ) == [
        _SmallDummyType(1, 'test'),
        _SmallDummyType(2, 'test2'),
        _SmallDummyType(42, 'test'),
    ]


def test_from_json_with_any():
    """Ensure `from_json` with `Any` as type simply returns the value."""
    value = {'a': 1, 'b': 'text'}

    assert from_json(Any, value) is value


def test_from_json_with_optional() -> None:
    """Ensure `from_json` accepts None with Optional and rejects otherwise."""
    assert from_json(Optional[int], None) is None
    assert from_json(Optional[int], 1) == 1

    with raises(JSONConversionError):
        from_json(int, None)


def test_from_json_with_numbers() -> None:
    """Ensure `from_json` accepts ints and floats and properly converts."""

    def _check(number_type, value, expected):
        result = from_json(number_type, value)
        assert result == expected
        assert isinstance(result, number_type)

    _check(int, 1, 1)
    _check(int, 1.0, 1)
    _check(float, 1, 1.0)
    _check(float, 1.0, 1.0)


def test_from_json_with_primitives() -> None:
    """Ensure `from_json` returns the value itself with primitives.

    On type mismatch, we expect failures.
    """

    def _check(primitive_type, value):
        assert from_json(primitive_type, value) is value

    _check(int, 1)
    _check(float, 1.0)
    _check(str, 'blabla')
    _check(bool, True)

    with raises(JSONConversionError):
        from_json(str, 1)

    with raises(JSONConversionError):
        from_json(bool, 1)

    with raises(JSONConversionError):
        from_json(int, 'text')


def test_from_json_with_a_new_type() -> None:
    """Ensure `from_json` works with `NewType`."""
    UserID = NewType('UserID', int)

    assert from_json(UserID, 1) == UserID(1)


def test_from_json_with_dict():
    """Ensure `from_json` can read a dict into a dataclass.

    Should fail if the schema class is not a compatible dataclass.
    """

    @dataclass
    class _Test:
        a: int
        b: str = 'test'

    assert from_json(_Test, {'a': 1, 'b': 'other_text'}) == _Test(1, 'other_text')

    assert from_json(_Test, {'a': 1}) == _Test(1, 'test')

    with raises(JSONConversionError):
        from_json(int, {'a': 1})

    class _NotADataclass:
        def __init__(self, a: int, b: str = 'test'):
            self.a = a
            self.b = b

    with raises(JSONConversionError):
        from_json(_NotADataclass, {'a': 1})


def test_from_json_with_list() -> None:
    """Ensure `from_json` can read a list of values.

    Should fail if the schema class is not a compatible dataclass.
    """
    assert from_json(List[int], [1, 2, 3]) == [1, 2, 3]

    @dataclass
    class _SmallDummyType:
        a: int
        b: str

    assert from_json(
        List[_SmallDummyType],
        [{'a': 1, 'b': 'test'}, {'a': 2, 'b': 'test2'}, {'a': 42, 'b': 'test'}],
    ) == [
        _SmallDummyType(1, 'test'),
        _SmallDummyType(2, 'test2'),
        _SmallDummyType(42, 'test'),
    ]

    with raises(JSONConversionError):
        assert from_json(int, [1, 2, 3],)


def test_from_json_with_optional_list() -> None:
    """Ensure `from_json` can read an optional list of values."""

    assert from_json(Optional[List[int]], None) is None
    assert from_json(Optional[List[int]], [1, 2, 3]) == [1, 2, 3]


def test_from_json_incompatible_type() -> None:
    """Ensure from_json fails in an expected way if value is unsupported."""
    with raises(JSONConversionError):
        # To be fair, mypy won't let you.
        assert from_json(  # type: ignore
            List[int], {1, 2, 3},
        )


def test_to_json_primitive_types() -> None:
    """Ensure to_json doesn't change primitive types."""
    assert to_json(1) == 1
    assert to_json(1.0) == 1.0
    assert to_json('text') == 'text'
    assert to_json(True)


def test_to_json_dataclass_type() -> None:
    """Ensure to_json doesn't change primitive types."""

    @dataclass
    class _Serializable:
        x: int
        y: str

    assert to_json(_Serializable(1, 'bla')) == {'x': 1, 'y': 'bla'}

    @dataclass
    class _Nested:
        x: int
        y: _Serializable

    print(_Nested(1, _Serializable(1, 'bla')).y)

    assert to_json(_Nested(1, _Serializable(1, 'bla')))  # == {'x': 1, 'y': 'bla'}


def test_to_json_list_type() -> None:
    """Ensure to_json doesn't change primitive types."""

    @dataclass
    class _Serializable:
        x: int
        y: str

    assert to_json([_Serializable(1, 'text'), _Serializable(2, 'other')]) == (
        [{'x': 1, 'y': 'text'}, {'x': 2, 'y': 'other'}]
    )


def test_to_json_enum_type() -> None:
    """Ensure to_json supports Enum types."""

    class _MyEnum(Enum):
        A = 1
        B = 2

    assert to_json(_MyEnum.A) == 1

    class _StrEnum(Enum):
        A = 'text'
        B = 'other'

    assert to_json(_StrEnum.A) == 'text'

    @dataclass
    class _HasEnumMembers:
        x: _MyEnum
        y: _StrEnum

    assert to_json(_HasEnumMembers(_MyEnum.B, _StrEnum.B)) == {'x': 2, 'y': 'other'}


def test_to_json_unsupported_type() -> None:
    """Ensure to_json raises with unsupported object."""

    class _NotADataclass:
        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

    with raises(JSONConversionError):
        to_json(_NotADataclass(1, 'text'))
