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
peakrdl-python tool. It provides the base types of field enumerations
"""
from enum import Enum
from typing import Optional, Self
from collections import namedtuple
from json import JSONEncoder

SystemRDLEnumEntry = namedtuple('SystemRDLEnumEntry', ['int_value', 'name', 'desc'])

class SystemRDLEnum(Enum):
    """
    A Enumeration that can also hold the system RDL properties, notably the `name` and `desc
    """
    def __new__(cls, value: int, rdl_name: Optional[str], rdl_desc: Optional[str]) -> 'SystemRDLEnum':
        obj = object.__new__(cls)
        obj._value_ = value
        obj.__rdl_name = rdl_name  # type: ignore[attr-defined]
        obj.__rdl_desc = rdl_desc  # type: ignore[attr-defined]
        return obj

    @property
    def rdl_name(self) -> Optional[str]:
        """
        The systemRDL name property for the encoding entry
        """
        return self.__rdl_name  # type: ignore[attr-defined]

    @property
    def rdl_desc(self) -> Optional[str]:
        """
        The systemRDL name property for the encoding entry
        """
        return self.__rdl_desc  # type: ignore[attr-defined]

    def __str__(self) -> str:
        return self.name

class RegisterFieldJSONEncoder(JSONEncoder):
    """
    JSON Encoder that supports SystemRDLEnum
    """
    def default(self, o):   # type: ignore[no-untyped-def]
        if isinstance(o, SystemRDLEnum):
            return o.name
        # Let the base class default method raise the TypeError
        return super().default(o)
