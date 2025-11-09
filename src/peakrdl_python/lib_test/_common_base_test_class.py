"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

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

This package is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provide the base class common to both the async and non-async versions
"""
import unittest
from abc import ABC
from typing import Union
from unittest.mock import patch
from itertools import product

from ..lib import FieldReadWrite, FieldReadOnly, FieldWriteOnly
from ..lib import FieldEnumReadWrite, FieldEnumReadOnly, FieldEnumWriteOnly
from ..sim_lib.dummy_callbacks import dummy_read
from ..sim_lib.dummy_callbacks import dummy_write

from .utilities import reverse_bits, expected_reg_write_data
from .utilities import reg_value_for_field_read_with_random_base
from .utilities import random_field_value, random_field_parent_reg_value

class CommonTestBase(unittest.TestCase, ABC):
    ...
