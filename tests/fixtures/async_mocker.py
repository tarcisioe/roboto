"""Module to ease mocking of async functions.

Code was lifted directly from comments in
https://github.com/pytest-dev/pytest-mock/issues/150.
"""
import sys

import pytest
import pytest_mock

from ..common import AsyncMock

if sys.version_info < (3, 8):
    from asynctest import mock  # pylint: disable=import-error
else:
    from unittest import mock  # pylint: disable=import-error


@pytest.fixture
def async_mocker(pytestconfig):
    """Fixture to mock async functions.

    This is a straight copy + paste from pytest_mock, but with our patched
    MockFixture
    """
    result = AsyncMockFixture(pytestconfig)
    yield result
    result.stopall()


class AsyncMockFixture(pytest_mock.MockFixture):
    """Fixture to mock async functions."""

    def __init__(self, _):  # pylint: disable=super-init-not-called
        """This is a straight copy + paste from pytest_mock."""

        self._patches = []  # list of mock._patch objects
        self._mocks = []  # list of MagicMock objects

        self.mock_module = mock_module = mock

        self.patch = self._Patcher(self._patches, self._mocks, mock_module)
        # aliases for convenience
        self.Mock = mock_module.Mock
        self.MagicMock = mock_module.MagicMock
        self.NonCallableMock = mock_module.NonCallableMock
        self.PropertyMock = mock_module.PropertyMock
        self.call = mock_module.call
        self.ANY = mock_module.ANY
        self.DEFAULT = mock_module.DEFAULT
        self.create_autospec = mock_module.create_autospec
        self.sentinel = mock_module.sentinel
        self.mock_open = mock_module.mock_open

        # CoroutineMock is from asynctest
        # AsyncMock is being added in python 3.8
        # Please use AsyncMock.
        self.AsyncMock = AsyncMock  # pylint: disable=invalid-name
