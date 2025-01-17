"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This module is intended to distributed as part of automatically generated code by the
peakrdl-python tool.  It provides a set of types used by the autogenerated code to callbacks
"""
from typing import Protocol


class RegisterReadCallback(Protocol):
    """
    Callback definition software read to a field, register or memory
    """

    # pylint: disable=too-few-public-methods
    def __call__(self, value: int) -> None:
        pass


class RegisterWriteCallback(Protocol):
    """
    Callback definition software write to a field, register or memory
    """

    # pylint: disable=too-few-public-methods
    def __call__(self, value: int) -> None:
        pass

class FieldReadCallback(Protocol):
    """
    Callback definition software read to a field, register or memory
    """

    # pylint: disable=too-few-public-methods
    def __call__(self, value: int) -> None:
        pass


class FieldWriteCallback(Protocol):
    """
    Callback definition software write to a field, register or memory
    """

    # pylint: disable=too-few-public-methods
    def __call__(self, value: int) -> None:
        pass

class MemoryReadCallback(Protocol):
    """
    Callback definition software read to a field, register or memory
    """

    # pylint: disable=too-few-public-methods
    def __call__(self, offset: int, value: int) -> None:
        pass


class MemoryWriteCallback(Protocol):
    """
    Callback definition software write to a field, register or memory
    """

    # pylint: disable=too-few-public-methods
    def __call__(self, offset: int, value: int) -> None:
        pass
