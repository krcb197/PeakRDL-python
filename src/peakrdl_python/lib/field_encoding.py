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
from enum import _EnumDict
from enum import Enum
from enum import EnumMeta
from typing import Optional
from collections import namedtuple

SystemRDLEnumEntry = namedtuple('SystemRDLEnumEntry', ['int_value', 'name', 'desc'])

# The code below defining a sub-type of EnumMeta and how to use it was inspired by the
# django-enumfields package
# The job of this enumeration is to extend the function of the python enumeration to include
# the system rdl `name` and `desc` properties whilst continuing to oeprate as an enumeration as
# before


class SystemRDLEnumMeta(EnumMeta):
    """
    An extension to EnumMeta necessary to implement the behaviour
    """

    # this needs to match the signature of the __call__ method on EnumMeta, event though it
    # fails some pylint checks it is assumed the authors of the python enum module know what
    # they are doing
    # pylint:disable-next=too-many-arguments,keyword-arg-before-vararg,redefined-builtin
    def __call__(cls, value, names=None, *values, module=None, qualname=None, type=None,
                 start=1, boundary=None):

        if isinstance(value, SystemRDLEnumEntry):
            return EnumMeta.__call__(cls, value, names=names, *values, module=module,
                                     qualname=qualname, type=type, start=start, boundary=boundary)

        if isinstance(value, int):

            int_mapping = { item.value:item._full_value for item in cls._member_map_.values() }

            new_value = int_mapping[value]

            return EnumMeta.__call__(cls, new_value, names=names, *values, module=module,
                                     qualname=qualname, type=type, start=start, boundary=boundary)

        raise NotImplementedError()

class SystemRDLEnum(SystemRDLEnumMeta('SystemRDLEnum', (Enum,), _EnumDict())):
    """
    A Enumeration that can also hold the system RDL properties, notably the `name` and `desc
    """

    @property
    def _full_value(self) -> SystemRDLEnumEntry:
        """ The full field value (needed to some operation) """
        return self._value_

    @property
    def value(self) -> int:
        """ The integer value used to encode the field value """
        return self._value_.int_value

    @property
    def rdl_name(self) -> Optional[str]:
        """
        The systemRDL name property for the encoding entry
        """
        return self._value_.name

    @property
    def rdl_desc(self) -> Optional[str]:
        """
        The systemRDL name property for the encoding entry
        """
        return self._value_.desc
