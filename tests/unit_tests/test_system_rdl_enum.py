"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of 
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Test the extension to an Enum that is used in the for an systemRDL encoding, which includes
meta data in addition to a value
"""
import unittest
from peakrdl_python.lib.field_encoding import SystemRDLEnum, SystemRDLEnumEntry

class TestGoodEncoding(unittest.TestCase):
    """
    Test the case of a properly defined Enumeration
    """

    class ExampleFieldEncoding(SystemRDLEnum):
        """
        A example encoding with properly defined members
        """
        VALUE1 = SystemRDLEnumEntry(int_value=1,
                                    name=None,
                                    desc="VALUE1 desc")
        VALUE2 = SystemRDLEnumEntry(int_value=2,
                                    name=None,
                                    desc=None)
        VALUE3 = SystemRDLEnumEntry(int_value=3,
                                    name="VALUE3 name",
                                    desc=None)
        VALUE4 = SystemRDLEnumEntry(int_value=4,
                                    name="VALUE4 name",
                                    desc="VALUE4 desc")

    def test_name_value_and_meta_data(self):
        """
        Test the instance name, value and meta data are correct
        """

        inst_value1 = self.ExampleFieldEncoding.VALUE1
        self.assertEqual(inst_value1.value, 1)
        self.assertEqual(inst_value1.name, 'VALUE1')
        self.assertIsNone(inst_value1.rdl_name)
        self.assertEqual(inst_value1.rdl_desc, 'VALUE1 desc')

        inst_value2 = self.ExampleFieldEncoding.VALUE2
        self.assertEqual(inst_value2.value, 2)
        self.assertEqual(inst_value2.name, 'VALUE2')
        self.assertIsNone(inst_value2.rdl_name)

        inst_value3 = self.ExampleFieldEncoding.VALUE3
        self.assertEqual(inst_value3.value, 3)
        self.assertEqual(inst_value3.name, 'VALUE3')
        self.assertEqual(inst_value3.rdl_name, 'VALUE3 name')

        inst_value4 = self.ExampleFieldEncoding.VALUE4
        self.assertEqual(inst_value4.value, 4)
        self.assertEqual(inst_value4.name, 'VALUE4')
        self.assertEqual(inst_value4.rdl_name, 'VALUE4 name')
        self.assertEqual(inst_value4.rdl_desc, 'VALUE4 desc')

    def test_interation(self):
        """
        Test interation on the enumeration
        """

        for index, item in enumerate(self.ExampleFieldEncoding):
            self.assertEqual(item.value, index+1)
            self.assertEqual(item.name, f'VALUE{index+1:d}')

    def test_set_by_value(self):
        """
        Test setting the enumeration from an integer
        """

        for index in range(1,5):
            item = self.ExampleFieldEncoding(index)
            self.assertEqual(item.value, index)

    def test_set_by_name(self):
        """
        Test setting the enumeration from its name passed as a string
        """
        for index in range(1,5):
            item = self.ExampleFieldEncoding[f'VALUE{index}']
            self.assertEqual(item.value, index)

    def test_str_format(self):
        """
        Test the string method works correctly
        """
        for index, item in enumerate(self.ExampleFieldEncoding):
            self.assertEqual(str(item), f'VALUE{index+1}')
