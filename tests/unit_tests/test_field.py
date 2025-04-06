import unittest
from typing import Optional, Union, TypeVar
from collections.abc import Iterator
from unittest.mock import patch, MagicMock
from enum import IntEnum
from itertools import product


from peakrdl_python.lib.base_field import FieldType
from peakrdl_python.lib import FieldReadOnly, FieldWriteOnly, FieldReadWrite, Field
from peakrdl_python.lib import FieldEnumReadOnly, FieldEnumWriteOnly, FieldEnumReadWrite
from peakrdl_python.lib import RegReadOnly, RegWriteOnly, RegReadWrite, Reg
from peakrdl_python.lib import FieldSizeProps
from peakrdl_python.lib.utility_functions import swap_msb_lsb_ordering
from peakrdl_python.lib import AddressMap, CallbackSet, RegFile, Memory, RegArray, FieldMiscProps
from peakrdl_python.lib import SystemRDLEnum, SystemRDLEnumEntry

from .simple_components import CallBackTestWrapper

FieldClassType = TypeVar('FieldClassType', FieldReadWrite, FieldReadOnly, FieldWriteOnly)


class TestMsbAndLsbSwapping(unittest.TestCase):

    def test_swap_4(self):

        self.assertEqual(swap_msb_lsb_ordering(width=4, value=0), 0)
        self.assertEqual(swap_msb_lsb_ordering(width=4, value=0x1), 0x8)
        self.assertEqual(swap_msb_lsb_ordering(width=4, value=0x2), 0x4)
        self.assertEqual(swap_msb_lsb_ordering(width=4, value=0x4), 0x2)
        self.assertEqual(swap_msb_lsb_ordering(width=4, value=0x8), 0x1)

    def test_swap_long(self):
        for field_length in range(1, 512):
            for pos in range(field_length):
                self.assertEqual(swap_msb_lsb_ordering(width=field_length, value=1 << pos),
                                 1 << field_length - 1 - pos)


class TestField(CallBackTestWrapper):

    def GenerateDUT(self, field_size_properies: FieldSizeProps, field_type: type[FieldClassType],
                    field_payload: FieldType, register_type: type[Reg]) -> FieldClassType:

        class DUT(field_type):
            pass

        class DUTRegWrapper(register_type):

            def __init__(self, *,
                         address: int,
                         accesswidth: int,
                         width: int,
                         logger_handle: str,
                         inst_name: str,
                         parent: AddressMap):
                super().__init__(address=address,
                                 accesswidth=accesswidth,
                                 width=width,
                                 logger_handle=logger_handle,
                                 inst_name=inst_name,
                                 parent=parent)

                self.__dut = field_type(
                    parent_register=self,
                    size_props=field_size_properies,
                    misc_props=FieldMiscProps(
                        default=None,
                        is_volatile=False),
                    logger_handle=logger_handle + '.dut',
                    inst_name='dut',
                    field_type=field_payload)

            @property
            def readable_fields(self) -> Iterator[FieldReadOnly]:
                """
                generator that produces has all the readable fields within the register
                """
                yield self.field

            @property
            def fields(self) -> Iterator[FieldReadOnly]:
                """
                generator that produces has all the readable fields within the register
                """
                yield self.field

            # build the properties for the fields
            @property
            def dut(self) -> field_type:
                """
                Property to access field of the register
                """
                return self.__dut

            @property
            def systemrdl_python_child_name_map(self) -> dict[str, str]:
                return {
                    'dut': 'dut',
                }

        class DUTWrapper(AddressMap):
            """
            Address map to wrap the register being tested
            """

            # pylint: disable=duplicate-code
            def __init__(self, *,
                         callbacks: Optional[CallbackSet],
                         address: int,
                         logger_handle: str,
                         inst_name: str):
                super().__init__(callbacks=callbacks, address=address, logger_handle=logger_handle,
                                 inst_name=inst_name, parent=None)

                self.__dut_reg_wrapper = DUTRegWrapper(
                    logger_handle=logger_handle + '.dut_reg_wrapper',
                    inst_name='dut_reg_wrapper',
                    parent=self,
                    width=32,
                    accesswidth=32,
                    address=address)

            def get_memories(self, unroll: bool = False) -> \
                    Iterator[Union[Memory, tuple[Memory, ...]]]:
                raise NotImplementedError('Not implemented in the testing')

            def get_sections(self, unroll: bool = False) -> \
                    Iterator[Union[Union[AddressMap, RegFile],
                    tuple[Union[AddressMap, RegFile], ...]]]:
                raise NotImplementedError('Not implemented in the testing')

            def get_registers(self, unroll: bool = False) -> \
                    Iterator[Union[Reg, RegArray]]:
                """
                generator that produces all the readable_registers of this node
                """
                raise NotImplementedError('Not implemented in the testing')

            @property
            def systemrdl_python_child_name_map(self) -> dict[str, str]:
                return {
                    'dut_reg_wrapper': 'dut_reg_wrapper'
                }

            @property
            def dut_reg_wrapper(self) -> register_type:
                """
                Register under tests
                """
                return self.__dut_reg_wrapper

            @property
            def size(self) -> int:
                return self.dut_reg_wrapper.size

        dut_wrapper = DUTWrapper(callbacks=self.callbacks, address=0,
                                 logger_handle='dut_wrapper', inst_name='dut_wrapper')

        return dut_wrapper.dut_reg_wrapper.dut

    def test_read_write(self):
        for msb_high in [True, False]:
            with self.subTest(test_case=f'{msb_high=}'):
                for low in range(0, 4, 4):
                    dut = self.GenerateDUT(
                        field_size_properies=FieldSizeProps(width=4,
                                                            low=low,
                                                            high=low + 3,
                                                            msb=low + 3 if msb_high else low,
                                                            lsb=low if msb_high else low + 3),
                        field_type=FieldReadWrite,
                        register_type=RegReadWrite,
                        field_payload=int)

                    # test the read
                    for test_value in [0x1, 0x2, 0x4, 0x8]:
                        read_mock = MagicMock(return_value=test_value << low)
                        write_mock = MagicMock()
                        with patch.object(self.callbacks, 'read_callback',
                                          side_effect=read_mock) as read_patch, \
                                patch.object(self.callbacks, 'write_callback',
                                             side_effect=self.write_addr_space) as write_patch:
                            read_value = dut.read()
                            self.assertIsInstance(read_value, int)
                            if msb_high:
                                self.assertEqual(read_value, test_value)
                            else:
                                # the swap_msb_lsb_ordering has been tested above so it is known
                                # to be good
                                self.assertEqual(read_value,
                                                 swap_msb_lsb_ordering(width=4, value=test_value))
                        read_mock.assert_called_once_with(addr=0, width=32, accesswidth=32)
                        write_mock.assert_not_called()

                    # test the write
                    for test_value in [0x1, 0x2, 0x4, 0x8]:
                        read_mock = MagicMock(return_value=0)
                        with patch.object(self.callbacks, 'read_callback',
                                          side_effect=read_mock) as read_patch, \
                                patch.object(self.callbacks, 'write_callback',
                                             side_effect=self.write_addr_space) as write_patch:
                            dut.write(test_value)
                            read_mock.assert_called_once_with(addr=0, width=32, accesswidth=32)
                            if msb_high:
                                write_patch.assert_called_once_with(addr=0,
                                                                   width=32,
                                                                   accesswidth=32,
                                                                   data=test_value << low)
                            else:
                                # the swap_msb_lsb_ordering has been tested above so it is known
                                # to be good
                                write_patch.assert_called_once_with(addr=0, width=32,
                                                                   accesswidth=32,
                                                                   data=swap_msb_lsb_ordering(
                                                                       width=4,
                                                                       value=test_value) << low)

    def test_read_write_enum(self):

        for enum_type, msb_high in product([IntEnum, SystemRDLEnum], [True, False]):
            with self.subTest(test_case=f'{enum_type=}, {msb_high}'):
                class DUTEnumType(enum_type):
                    VALUE1 = 0x1 if enum_type is IntEnum else SystemRDLEnumEntry(0x1, None, None)
                    VALUE2 = 0x2 if enum_type is IntEnum else SystemRDLEnumEntry(0x2, None, None)
                    VALUE3 = 0x4 if enum_type is IntEnum else SystemRDLEnumEntry(0x3, None, None)
                    VALUE4 = 0x8 if enum_type is IntEnum else SystemRDLEnumEntry(0x8, None, None)

                for low in range(0, 4, 4):
                    dut = self.GenerateDUT(
                        field_size_properies=FieldSizeProps(width=4,
                                                            low=low,
                                                            high=low + 3,
                                                            msb=low + 3 if msb_high else low,
                                                            lsb=low if msb_high else low + 3),
                        field_type=FieldEnumReadWrite,
                        register_type=RegReadWrite,
                        field_payload=DUTEnumType)

                    # test the read
                    for test_value in DUTEnumType:
                        if msb_high:
                            read_mock = MagicMock(return_value=test_value.value)
                        else:
                            # the swap_msb_lsb_ordering has been tested above so it is known
                            # to be good
                            read_mock = MagicMock(return_value=swap_msb_lsb_ordering(
                                                                    width=4,
                                                                    value=test_value.value))
                        write_mock = MagicMock()
                        with patch.object(self.callbacks, 'read_callback',
                                          side_effect=read_mock) as read_patch, \
                                patch.object(self.callbacks, 'write_callback',
                                             side_effect=self.write_addr_space) as write_patch:
                            read_value = dut.read()
                            self.assertIsInstance(read_value, DUTEnumType)
                            self.assertIs(read_value, test_value)

                        read_mock.assert_called_once_with(addr=0, width=32, accesswidth=32)
                        write_mock.assert_not_called()

                    with self.assertRaises(TypeError):
                        dut.write(0x1)

                    # test the write
                    for test_value in DUTEnumType:
                        read_mock = MagicMock(return_value=0)
                        with patch.object(self.callbacks, 'read_callback',
                                          side_effect=read_mock) as read_patch, \
                                patch.object(self.callbacks, 'write_callback',
                                             side_effect=self.write_addr_space) as write_patch:
                            dut.write(test_value)
                            read_mock.assert_called_once_with(addr=0, width=32, accesswidth=32)
                            if msb_high:
                                write_patch.assert_called_once_with(addr=0,
                                                                   width=32,
                                                                   accesswidth=32,
                                                                   data=test_value.value << low)
                            else:
                                # the swap_msb_lsb_ordering has been tested above so it is known
                                # to be good
                                write_patch.assert_called_once_with(addr=0, width=32,
                                                                   accesswidth=32,
                                                                   data=swap_msb_lsb_ordering(
                                                                       width=4,
                                                                       value=test_value.value) << low)


if __name__ == '__main__':
    unittest.main()
