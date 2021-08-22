import os
import sys
import tempfile
import random
import string
import re
import logging.config
import logging
from itertools import combinations

import unittest
from unittest.mock import patch

from systemrdl import RDLCompiler, RegNode, FieldNode
from peakrdl.python.exporter import PythonExporter

logging_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'normal': {
                'class': 'logging.Formatter',
                'format': '%(name)-15s %(levelname)-8s %(message)s'
            },
            'root_catch': {
                'class': 'logging.Formatter',
                'format': 'ROOT_LOGGER %(name)-15s %(levelname)-8s  %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'normal',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'testcases.log',
                'mode': 'w',
                'formatter': 'normal'
            },
            'console_root': {
                            'class': 'logging.StreamHandler',
                            'formatter': 'root_catch',
                        },
        },
        'loggers': {
            'root': {
                'handlers': ['console_root'],
                'level': 'DEBUG'
            },
            __name__:  {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            },
            'reg_model':  {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }


# dummy functions to support the test cases, note that these are not used as
# they get patched
def read_addr_space(addr: int):
    assert isinstance(addr, int)
    return 0


def write_addr_space(addr: int, data: int):
    assert isinstance(addr, int)
    assert isinstance(data, int)


def read_callback(addr: int):
    return read_addr_space(addr)


def write_callback(addr: int, data: int):
    write_addr_space(addr, data)


class BaseTestContainer:
    class BaseRDLTestCase(unittest.TestCase):

        root_systemRDL_file = None
        root_node_name = None
        dut_cls = None

        @classmethod
        def setUpClass(cls):

            logging.config.dictConfig(logging_config)

            rdlc = RDLCompiler()
            rdlc.compile_file(os.path.join('testcases', cls.root_systemRDL_file))
            cls.spec = rdlc.elaborate(top_def_name=cls.root_node_name).top

            cls.tempdir = tempfile.TemporaryDirectory()

            exporter = PythonExporter()
            exporter.export(node=cls.spec, path=cls.tempdir.name)

            sys.path.append(cls.tempdir.name)
            module = __import__(cls.root_node_name+'.reg_model.' + cls.root_node_name,
                                globals(), locals(),
                                [cls.root_node_name + '_cls'], 0)
            cls.dut_cls = getattr(module, cls.root_node_name + '_cls')


        def setUp(self):
            self.dut = self.dut_cls(read_callback=read_callback,
                                    write_callback=write_callback)

        def _get_dut_object(self, node):

            # without root node as that becomes DUT
            object_tree_str_list = node.get_path_segments()[1:]

            # tranverse the tree to the object
            dut_obj = self.dut
            for object_str in object_tree_str_list:
                if object_str[-1] == ']':
                    # an array
                    re_result_name = re.match(r'(\w+)(\[\d+\])', object_str)
                    index = int(re_result_name.group(2)[1:-1])
                    dut_obj = getattr(dut_obj, re_result_name.group(1))[index]
                else:
                    dut_obj = getattr(dut_obj, object_str)

            return dut_obj

        def test_attribute_insertion(self):
            """
            test that additional attributes can not be added to the objects,
            the __slots__ on classes should prevent it
            """
            def random_string():
                """
                generate a random variable name
                """
                return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                logger.info('checking attribute insertion - node : {fqnode_path}'.format(fqnode_path=node.get_path()))

                # generate a random string and see if is used on the object or
                # not, and regenerate if that is the case
                attribute_name = random_string()
                while hasattr(dut_obj, attribute_name) is True:
                    attribute_name = random_string()

                with self.assertRaises(AttributeError):
                    setattr(dut_obj, attribute_name, None)

        def test_addresses(self):
            """
            test that each node in the structure (including all the array like
            elements) has been constructed with the correct base addresses
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, RegNode):
                    logger.info('checking address - node : {fqnode_path}'.format(fqnode_path=node.get_path()))
                    self.assertEqual(node.absolute_address, dut_obj.base_address)

        def test_field_bitmask(self):
            """
            test that the bit mask for each field is correct
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, FieldNode):

                    self.assertEqual(node.lsb, dut_obj.lsb,
                                     msg='lsb mismatch on {fqnode_path}'.format(
                                         fqnode_path=node.get_path()))
                    self.assertEqual(node.msb, dut_obj.msb,
                                     msg='msb mismatch on {fqnode_path}'.format(
                                         fqnode_path=node.get_path()))
                    self.assertEqual(node.high, dut_obj.high,
                                     msg='high mismatch on {fqnode_path}'.format(
                                         fqnode_path=node.get_path()))
                    self.assertEqual(node.low, dut_obj.low,
                                     msg='low mismatch on {fqnode_path}'.format(
                                         fqnode_path=node.get_path()))
                    self.assertEqual(node.width, dut_obj.width)

                    logger.info('checking bitmask - node : {fqnode_path}'.format(fqnode_path=node.get_path()))
                    for bit_position in range(dut_obj.register_data_width):
                        if bit_position in range(node.low, node.high+1):
                            self.assertEqual(dut_obj.bitmask & (1 << bit_position), (1 << bit_position))
                        else:
                            self.assertEqual(dut_obj.bitmask & (1 << bit_position), 0)

        def test_feild_enum(self):
            """
            test that the enum associated with a field has been correctly
            configured, it is possible to redefine an enum at a different
            scope in systemRDL (with the same name as an earlier definition),
            this needs to be caught
            :return:
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, FieldNode):

                    if 'encode' in node.list_properties():

                        node_enum = node.get_property('encode')
                        dut_enum = dut_obj.enum_cls

                        self.assertEqual(len(node_enum), len(dut_enum))

                        for node_enum_possibility in node_enum:
                            self.assertTrue(hasattr(dut_enum, node_enum_possibility.name))
                            self.assertEqual(getattr(dut_enum, node_enum_possibility.name).value,
                                             node_enum_possibility.value,
                                             msg=f'test {node.inst_name} enum name:{node_enum_possibility.name}, value mismatch')

        def test_register_read_and_write(self):
            """
            Check the ability to read and write to all registers
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, RegNode):
                    logger.info('checking read/write - node : {fqnode_path}'.format(fqnode_path=node.get_path()))
                    with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
                            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

                        expected_address = dut_obj.base_address  # test_addresses checks that this
                                                                 # has been set up correctly

                        max_value = (2**dut_obj.data_width)-1

                        if node.has_sw_readable:

                            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
                            self.assertEqual(dut_obj.read(), 1)
                            self.assertEqual(read_callback_mock.call_args[0][0], expected_address)

                            # test the read check with high value, low value and a random value in between
                            read_callback_mock.reset_mock()
                            read_callback_mock.return_value = max_value
                            self.assertEqual(dut_obj.read(), max_value)
                            read_callback_mock.assert_called_once()

                            read_callback_mock.reset_mock()
                            read_callback_mock.return_value = 0
                            self.assertEqual(dut_obj.read(), 0x0)
                            read_callback_mock.assert_called_once()

                            random_value = random.randrange(0, max_value+1)
                            read_callback_mock.reset_mock()
                            read_callback_mock.return_value = random_value
                            self.assertEqual(dut_obj.read(), random_value)
                            read_callback_mock.assert_called_once()

                            # at the end of the read tests the write should not have been called
                            read_callback_mock.reset_mock()

                        write_callback_mock.assert_not_called()

                        if node.has_sw_writable:

                            # test the write with high value, low value and a random value in between
                            dut_obj.write(max_value)
                            write_callback_mock.assert_called_once()
                            self.assertEqual(write_callback_mock.call_args[0][0], expected_address)
                            self.assertEqual(write_callback_mock.call_args[0][1], max_value)
                            write_callback_mock.reset_mock()

                            dut_obj.write(0)
                            write_callback_mock.assert_called_once()
                            self.assertEqual(write_callback_mock.call_args[0][0], expected_address)
                            self.assertEqual(write_callback_mock.call_args[0][1], 0)
                            write_callback_mock.reset_mock()

                            random_value = random.randrange(0, max_value+1)
                            dut_obj.write(random_value)
                            write_callback_mock.assert_called_once()
                            self.assertEqual(write_callback_mock.call_args[0][0], expected_address)
                            self.assertEqual(write_callback_mock.call_args[0][1], random_value)
                            write_callback_mock.reset_mock()

                            with self.assertRaises(ValueError):
                                dut_obj.write(-1)

                            with self.assertRaises(ValueError):
                                dut_obj.write(max_value+1)

                        else:
                            with self.assertRaises(AttributeError):
                                dut_obj.write(0)

                        # check the read has not been called in the write test
                        read_callback_mock.assert_not_called()

        @staticmethod
        def _reverse_bits(x: int, n: int) -> int:
            """

            Args:
                x: value to reverse

            Returns:
                reversed valued

            """
            result = 0
            for i in range(n):
                if (x >> i) & 1:
                    result |= 1 << (n - 1 - i)
            return result

        def test_reverse_bits(self):
            """
            Test that the reverse bits functions as expected
            Returns:

            """
            self.assertEqual(0x1, self._reverse_bits(0x8, 4))
            self.assertEqual(0x2, self._reverse_bits(0x4, 4))
            self.assertEqual(0x4, self._reverse_bits(0x2, 4))
            self.assertEqual(0x8, self._reverse_bits(0x1, 4))

            self.assertEqual(0x3, self._reverse_bits(0xC, 4))
            self.assertEqual(0x5, self._reverse_bits(0xA, 4))

            self.assertEqual(0x0001, self._reverse_bits(0x8000, 16))
            self.assertEqual(0x0002, self._reverse_bits(0x4000, 16))
            self.assertEqual(0x0004, self._reverse_bits(0x2000, 16))
            self.assertEqual(0x0008, self._reverse_bits(0x1000, 16))
            self.assertEqual(0x0010, self._reverse_bits(0x0800, 16))
            self.assertEqual(0x0020, self._reverse_bits(0x0400, 16))
            self.assertEqual(0x0040, self._reverse_bits(0x0200, 16))
            self.assertEqual(0x0080, self._reverse_bits(0x0100, 16))

            self.assertEqual(0x3000, self._reverse_bits(0x000C, 16))
            self.assertEqual(0x5555, self._reverse_bits(0xAAAA, 16))



        def test_int_field_read_and_write(self):
            """
            Check the ability to read and write to all registers
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, FieldNode):
                    logger.info('checking read/write - node : {fqnode_path}'.format(fqnode_path=node.get_path()))

                    if 'encode' in node.list_properties():
                        # skip the field if it is an enumerated fields
                        continue

                    with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
                            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

                        if node.is_sw_readable:

                            # read back - zero, this is achieved by setting the register to inverse bitmask
                            read_callback_mock.reset_mock()
                            read_callback_mock.return_value = dut_obj.inverse_bitmask
                            self.assertEqual(dut_obj.read(), 0)
                            read_callback_mock.assert_called_once()

                            # read back - max_value, this is achieved by setting the register to bitmask
                            read_callback_mock.reset_mock()
                            read_callback_mock.return_value = dut_obj.bitmask
                            self.assertEqual(dut_obj.read(), dut_obj.max_value)
                            read_callback_mock.assert_called_once()

                            # read back - random value
                            read_callback_mock.reset_mock()
                            random_value = random.randrange(0, dut_obj.parent_register.max_value + 1)
                            read_callback_mock.return_value = random_value
                            random_field_value = (random_value & dut_obj.bitmask) >> dut_obj.low
                            read_back_value=dut_obj.read()
                            if dut_obj.high == dut_obj.msb:
                                self.assertEqual(read_back_value,
                                                 random_field_value)
                            elif dut_obj.high == dut_obj.lsb:
                                self.assertEqual(read_back_value,
                                                 self._reverse_bits(random_field_value, node.width),
                                                 msg=f'{read_back_value=:X}, {self._reverse_bits(random_field_value, node.width)=:X} , {random_value=:X}, {random_field_value=:X}')
                            else:
                                raise RuntimeError('unhandled condition high does not equal msb or lsb')
                            read_callback_mock.assert_called_once()

                            # at the end of the read tests the write should not have been called
                            read_callback_mock.reset_mock()

                        write_callback_mock.assert_not_called()

                        # check the write
                        if node.is_sw_writable:
                            random_reg_value = random.randrange(0, dut_obj.parent_register.max_value + 1)
                            random_field_value = random.randrange(0, dut_obj.max_value + 1)
                            for reg_base_value in [0, dut_obj.parent_register.max_value, random_reg_value]:
                                for field_value in [0, dut_obj.max_value, random_field_value]:
                                    read_callback_mock.reset_mock()
                                    write_callback_mock.reset_mock()
                                    read_callback_mock.return_value = reg_base_value

                                    dut_obj.write(field_value)

                                    if (((dut_obj.high+1) - dut_obj.low) < dut_obj.parent_register.data_width) and (node.parent.has_sw_readable):
                                        read_callback_mock.assert_called_once()
                                    else:
                                        read_callback_mock.assert_not_called()
                                    write_callback_mock.assert_called_once()
                                    self.assertEqual(write_callback_mock.call_args[0][0],
                                                     dut_obj.parent_register.base_address)

                                    if dut_obj.high == dut_obj.msb:
                                        original_field_value = field_value
                                    elif dut_obj.high == dut_obj.lsb:
                                        original_field_value = field_value
                                        field_value = self._reverse_bits(field_value, node.width)
                                    else:
                                        raise RuntimeError(
                                            'unhandled condition high does not equal msb or lsb')

                                    if node.parent.has_sw_readable:
                                        writen_value = write_callback_mock.call_args[0][1]
                                        expected_value = (reg_base_value & dut_obj.inverse_bitmask) | \
                                                         (dut_obj.bitmask & (field_value << dut_obj.low))
                                        self.assertEqual(writen_value,
                                                         expected_value,
                                                         msg=f'{writen_value=:X}, {expected_value=:X}, {original_field_value=:X}, {field_value=:X}, {node.inst_name}, {reg_base_value=:X}')
                                    else:
                                        # if the register is not readable, the value is simply written
                                        self.assertEqual(write_callback_mock.call_args[0][1],
                                                         field_value << dut_obj.low)

                            # check invalid write values bounce
                            with self.assertRaises(ValueError):
                                dut_obj.write(dut_obj.max_value + 1)

                            with self.assertRaises(ValueError):
                                dut_obj.write(-1)

        def test_enum_field_read_and_write(self):
            """
            Check the ability to read and write to all registers
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, FieldNode):
                    logger.info('checking read/write - node : {fqnode_path}'.format(fqnode_path=node.get_path()))

                    if 'encode' not in node.list_properties():
                        # skip any field that is not an enum
                        continue

                    with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
                            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:
                        enum_cls = dut_obj.enum_cls

                        if node.is_sw_readable:
                            # read back test
                            legal_values = []
                            for possible_enum_value in enum_cls:
                                # set the simulated read_back value to
                                random_value = random.randrange(0, dut_obj.register_data_width + 1)
                                read_callback_mock.reset_mock()

                                if dut_obj.high == dut_obj.msb:
                                    read_callback_mock.return_value = (random_value & dut_obj.inverse_bitmask) | (dut_obj.bitmask & (possible_enum_value.value << dut_obj.low))
                                elif dut_obj.high == dut_obj.lsb:
                                    read_callback_mock.return_value = (random_value & dut_obj.inverse_bitmask) | (dut_obj.bitmask & (self._reverse_bits(x=possible_enum_value.value, n=node.width) << dut_obj.low))
                                else:
                                    raise RuntimeError(
                                        'unhandled condition high does not equal msb or lsb')

                                self.assertEqual(dut_obj.read(), possible_enum_value)
                                legal_values.append(possible_enum_value.value)
                                read_callback_mock.assert_called_once()

                            read_callback_mock.reset_mock()

                            # check that other values of the field int
                            # that don't appear in the enum generate an
                            # error
                            possible_field_values = 2 ** dut_obj.width

                            if possible_field_values != len(enum_cls):
                                for field_value in range(0, dut_obj.max_value+1):
                                    if field_value in legal_values:
                                        continue
                                    with self.assertRaises(ValueError):
                                        read_callback_mock.reset_mock()
                                        random_value = random.randrange(0, dut_obj.register_data_width + 1)
                                        if dut_obj.high == dut_obj.msb:
                                            read_callback_mock.return_value = (random_value & dut_obj.inverse_bitmask) | (dut_obj.bitmask & (field_value << dut_obj.low))
                                        elif dut_obj.high == dut_obj.lsb:
                                            read_callback_mock.return_value = (random_value & dut_obj.inverse_bitmask) | (dut_obj.bitmask & (self._reverse_bits(x=field_value,n=node.width) << dut_obj.low))
                                        else:
                                            raise RuntimeError(
                                                'unhandled condition high does not equal msb or lsb')
                                        decode_field_value = dut_obj.read()

                        write_callback_mock.assert_not_called()

                        # write back test
                        if node.is_sw_writable:
                            for possible_enum_value in enum_cls:
                                random_value = random.randrange(0, dut_obj.register_data_width + 1)
                                read_callback_mock.reset_mock()
                                write_callback_mock.reset_mock()
                                read_callback_mock.return_value = random_value

                                dut_obj.write(possible_enum_value)
                                if (((dut_obj.high + 1) - dut_obj.low) < dut_obj.parent_register.data_width) and (node.parent.has_sw_readable):
                                    read_callback_mock.assert_called_once()
                                else:
                                    read_callback_mock.assert_not_called()
                                write_callback_mock.assert_called_once()
                                self.assertEqual(write_callback_mock.call_args[0][0], dut_obj.parent_register.base_address)
                                if dut_obj.high == dut_obj.msb:
                                    field_content = possible_enum_value.value
                                elif dut_obj.high == dut_obj.lsb:
                                    field_content = self._reverse_bits(x=possible_enum_value.value, n=node.width)
                                else:
                                    raise RuntimeError('unhandled condition high does not equal msb or lsb')

                                if node.parent.has_sw_readable:
                                    self.assertEqual(write_callback_mock.call_args[0][1],
                                                     (random_value & dut_obj.inverse_bitmask) | \
                                                     (dut_obj.bitmask & (field_content << dut_obj.low)))
                                else:
                                    # if the register is not readable, the value is simply written
                                    self.assertEqual(write_callback_mock.call_args[0][1],
                                                     field_content  << dut_obj.low)

        def test_register_read_fields(self):
            """
            Check the read fields method of a register
            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, RegNode):

                    if node.has_sw_readable is False:
                        # skip this if there is software readable fields
                        continue

                    # as this test is based on random data we will repeat it
                    # 100 times to be confident that all combinations get covered

                    for i in range(100):

                        rand_reg_value = random.randrange(0, dut_obj.max_value + 1)
                        for field in dut_obj.readable_fields:
                            if hasattr(field, 'enum_cls'):
                                # enum field
                                rand_field_value = random.choice(list(field.enum_cls)).value
                            else:
                                # normal int field
                                rand_field_value = random.randrange(0, field.max_value + 1)

                            if field.msb0 is False:
                                rand_reg_value = (rand_reg_value & field.inverse_bitmask) | (rand_field_value << field.low)
                            else:
                                rand_reg_value = (rand_reg_value & field.inverse_bitmask) | \
                                                 (self._reverse_bits(x=rand_field_value,n=field.width) << field.low)

                        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value) as read_callback_mock:

                            # the read_fields method gets a dictionary back
                            # from the object with all the read back field
                            # values
                            read_fields = dut_obj.read_fields()

                            #build_reference_dict
                            reference_read_fields = {}
                            for field in node.fields():
                                if field.is_sw_readable:
                                    dut_field = getattr(dut_obj,field.inst_name)
                                    reference_read_fields[field.inst_name] = dut_field.read()

                            self.assertDictEqual(read_fields, reference_read_fields)

        def test_register_write_fields(self):
            """
            test the writable_fields on all the registers
            Returns:

            """
            logger = logging.getLogger(self.id())

            for node in self.spec.descendants(unroll=True):
                dut_obj = self._get_dut_object(node)

                if isinstance(node, RegNode):

                    logger.info('checking write_fields - node : {fqnode_path}'.format(fqnode_path=node.get_path()))

                    if node.has_sw_writable is False:
                        # skip this if there is software readable fields
                        continue

                    writable_fields = list(dut_obj.writable_fields)

                    if node.has_sw_readable is True:
                        min_range = 1
                    else:
                        # if the register is not readable it is only possible
                        # to write all the fields
                        min_range = len(writable_fields)


                    for num_parm in range(min_range,len(writable_fields)+1):

                        for fields_to_write in combinations(writable_fields, num_parm):
                            kwargs = {}
                            expected_value = 0
                            for field_to_write in fields_to_write:
                                if hasattr(field_to_write, 'enum_cls'):
                                    # enum field
                                    rand_enum_value = random.choice(list(field_to_write.enum_cls))
                                    rand_field_value = rand_enum_value.value
                                    kwargs[field_to_write.inst_name] = rand_enum_value
                                else:
                                    # normal int field
                                    rand_field_value = random.randrange(0,field_to_write.max_value + 1)
                                    kwargs[field_to_write.inst_name] = rand_field_value

                                if field_to_write.msb0 is False:
                                    expected_value = (expected_value & field_to_write.inverse_bitmask) | (rand_field_value << field_to_write.low)
                                else:
                                    expected_value = (expected_value & field_to_write.inverse_bitmask) | \
                                                     (self._reverse_bits(x=rand_field_value, n=field_to_write.width) << field_to_write.low)

                            with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
                                    patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:
                                dut_obj.write_fields(**kwargs)
                                write_callback_mock.assert_called_once()
                                self.assertEqual(write_callback_mock.call_args[0][0],
                                                 dut_obj.base_address)
                                self.assertEqual(write_callback_mock.call_args[0][1],expected_value)

        @classmethod
        def tearDownClass(cls) -> None:
            if cls.dut_cls is not None:
                cls.tempdir.cleanup()


class Test_regfiles_and_arrays(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'regfile_and_arrays.rdl'
    root_node_name = 'regfile_and_arrays'


class Test_enum_example(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'enum_example.rdl'
    root_node_name = 'enum_example'


class Test_basic(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'basic.rdl'
    root_node_name = 'basic'


class Test_field_scope(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'field_scope.rdl'
    root_node_name = 'field_scope'


class Test_addrmap(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'addr_map.rdl'
    root_node_name = 'addr_map'

class Test_field_with_overridden_reset(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'field_with_overridden_reset.rdl'
    root_node_name = 'field_with_overridden_reset'

class Test_msb0_and_lsb0(BaseTestContainer.BaseRDLTestCase):

    root_systemRDL_file = 'msb0_and_lsb0.rdl'
    root_node_name = 'msb0_and_lsb0'

if __name__ == '__main__':
    unittest.main()
