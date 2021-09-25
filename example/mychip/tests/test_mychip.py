"""
Unit Tests for the mychip register model Python Wrapper

This code was generated from the PeakRDL-python package
"""
import unittest
from unittest.mock import patch
import random
from itertools import combinations

from ..peakrdl_python import CallbackSet

from ..reg_model.mychip import mychip_cls

# dummy functions to support the test cases, note that these are not used as
# they get patched
def read_addr_space(addr: int, width: int, accesswidth: int):
    assert isinstance(addr, int)
    assert isinstance(width, int)
    assert isinstance(accesswidth, int)
    return 0


def write_addr_space(addr: int, width: int, accesswidth: int,  data: int):
    assert isinstance(addr, int)
    assert isinstance(width, int)
    assert isinstance(accesswidth, int)
    assert isinstance(data, int)


def read_callback(addr: int, width: int, accesswidth: int):
    return read_addr_space(addr=addr, width=width, accesswidth=accesswidth)


def write_callback(addr: int, width: int, accesswidth: int,  data: int):
    write_addr_space(addr=addr, width=width, accesswidth=accesswidth, data=data)


class mychip_TestCase(unittest.TestCase):

    def setUp(self):
        self.dut = mychip_cls(CallbackSet(read_callback=read_callback,
                                                          write_callback=write_callback))

    @staticmethod
    def _reverse_bits(value: int, number_bits: int) -> int:
        """

        Args:
            value: value to reverse
            number_bits: number of bits used in the value

        Returns:
            reversed valued
        """
        result = 0
        for i in range(number_bits):
            if (value >> i) & 1:
                result |= 1 << (number_bits - 1 - i)
        return result

    def test_register_properties(self):
        """
        Walk the address map and check the address, size and accesswidth of every register is
        correct
        """
        self.assertEqual(self.dut.GPIO.GPIO_dir.address, 4)
        self.assertEqual(self.dut.GPIO.GPIO_dir.width, 32)
        self.assertEqual(self.dut.GPIO.GPIO_dir.accesswidth, self.dut.GPIO.GPIO_dir.accesswidth)
        self.assertEqual(self.dut.GPIO.GPIO_state.address, 8)
        self.assertEqual(self.dut.GPIO.GPIO_state.width, 32)
        self.assertEqual(self.dut.GPIO.GPIO_state.accesswidth, self.dut.GPIO.GPIO_state.accesswidth)

    def test_field_properties(self):
        """
        walk the address map and check that the lsb and msb of every field is correct
        """
        # test field properties: mychip.GPIO.GPIO_dir.PIN_0
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.lsb,
                        0)
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.msb,
                         0)
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.low,
                        0)
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.high,
                         0)
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.bitmask,
                         0x1)
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.inverse_bitmask,
                         0xFFFFFFFE)
        self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.max_value,
                         0x1)
        # test field properties: mychip.GPIO.GPIO_state.PIN_0
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.lsb,
                        0)
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.msb,
                         0)
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.low,
                        0)
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.high,
                         0)
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.bitmask,
                         0x1)
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.inverse_bitmask,
                         0xFFFFFFFE)
        self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.max_value,
                         0x1)

    def test_register_read_and_write(self):
        """
        Walk the register map and check every register can be read and written to correctly
        """

        # test access operations (read and/or write) to register:
        # mychip.GPIO.GPIO_dir
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.GPIO.GPIO_dir.read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.GPIO.GPIO_dir.read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.GPIO.GPIO_dir.read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.GPIO.GPIO_dir.read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.GPIO.GPIO_dir.write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.GPIO.GPIO_dir.write(0)
            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.GPIO.GPIO_dir.write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.GPIO.GPIO_dir.write(-1)

            with self.assertRaises(ValueError):
                self.dut.GPIO.GPIO_dir.write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # mychip.GPIO.GPIO_state
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.GPIO.GPIO_state.read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.GPIO.GPIO_state.read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.GPIO.GPIO_state.read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.GPIO.GPIO_state.read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.GPIO.GPIO_state.write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.GPIO.GPIO_state.write(0)
            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.GPIO.GPIO_state.write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.GPIO.GPIO_state.write(-1)

            with self.assertRaises(ValueError):
                self.dut.GPIO.GPIO_state.write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

    def test_int_field_read_and_write(self):
        """
        Check the ability to read and write to integer (non-eumn) fields
        """

        # test access operations (read and/or write) to field:
        # mychip.GPIO.GPIO_state.PIN_0
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFFFFFE
            self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.PIN_0.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0x1
            self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.read(),
                             0x1)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.PIN_0.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0x1) >> 0
            self.assertEqual(self.dut.GPIO.GPIO_state.PIN_0.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.PIN_0.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0x1 + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0x1, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.GPIO.GPIO_state.PIN_0.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.PIN_0.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_state.PIN_0.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFFFFFE) | \
                                     (0x1 & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.GPIO.GPIO_state.PIN_0.write(0x1 + 1)

            with self.assertRaises(ValueError):
                self.dut.GPIO.GPIO_state.PIN_0.write(-1)

    
    def test_enum_field_read_and_write(self):
        """
        Check the ability to read and write to enum fields
        """

        # test access operations (read and/or write) to field:
        # mychip.GPIO.GPIO_dir.PIN_0
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to dir_in
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFFFFFE) | \
                                              (0x1 & (0 << 0 ))
            self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.read(),
                             self.dut.GPIO.GPIO_dir.PIN_0.enum_cls.dir_in)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.PIN_0.parent_register.accesswidth)
            # set the simulated read_back value to dir_out
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFFFFFE) | \
                                              (0x1 & (1 << 0 ))
            self.assertEqual(self.dut.GPIO.GPIO_dir.PIN_0.read(),
                             self.dut.GPIO.GPIO_dir.PIN_0.enum_cls.dir_out)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.PIN_0.parent_register.accesswidth)
            

            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.GPIO.GPIO_dir.PIN_0.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.GPIO.GPIO_dir.PIN_0.write(enum_cls.dir_in)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.PIN_0.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFFFFFE) | \
                                     (0x1 & (0 << 0)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.GPIO.GPIO_dir.PIN_0.write(enum_cls.dir_out)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.GPIO.GPIO_dir.PIN_0.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFFFFFE) | \
                                     (0x1 & (1 << 0)))
            

            
            

    def test_register_read_fields(self):
        """
        Walk the register map and check every register read_fields method
        """
        
        # test read_fields to register:
        # mychip.GPIO.GPIO_dir
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.choice(list(self.dut.GPIO.GPIO_dir.PIN_0.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFFFFFE) | (rand_field_value << 0)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'PIN_0' : self.dut.GPIO.GPIO_dir.PIN_0.read()
                                    }

            self.assertDictEqual(self.dut.GPIO.GPIO_dir.read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # mychip.GPIO.GPIO_state
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0x1 + 1)
        rand_reg_value = (rand_reg_value & 0xFFFFFFFE) | (rand_field_value << 0)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'PIN_0' : self.dut.GPIO.GPIO_state.PIN_0.read()
                                    }

            self.assertDictEqual(self.dut.GPIO.GPIO_state.read_fields(),
                                 reference_read_fields)

    def test_register_write_fields(self):
        """
        Walk the register map and check every register write_fields method
        """
        def write_field_cominbinations(reg, writable_fields):
            with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
                patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:
                for num_parm in range(1, len(writable_fields) + 1):
                    for fields_to_write in combinations(writable_fields, num_parm):
                        kwargs = {}
                        expected_value = 0
                        for field_str in fields_to_write:
                            field = getattr(reg, field_str)
                            if hasattr(field, 'enum_cls'):
                                rand_enum_value = random.choice(list(field.enum_cls))
                                rand_field_value = rand_enum_value.value
                                kwargs[field_str] = rand_enum_value
                            else:
                                rand_field_value = random.randrange(0, field.max_value + 1)
                                kwargs[field_str] = rand_field_value

                            if field.msb == field.high:
                                expected_value = ( expected_value & field.inverse_bitmask ) | (rand_field_value << field.low)
                            elif field.msb == field.low:
                                expected_value = ( expected_value & field.inverse_bitmask ) | (self._reverse_bits(value=rand_field_value, number_bits=field.width) << field.low)
                            else:
                                raise RuntimeError('invalid msb/lsb high/low combination')

                        reg.write_fields(**kwargs)
                        write_callback_mock.assert_called_once_with(
                                addr=reg.address,
                                width=reg.width,
                                accesswidth=reg.accesswidth,
                                data=expected_value)
                        read_callback_mock.assert_called_once()
                        write_callback_mock.reset_mock()
                        read_callback_mock.reset_mock()
        
        # test read_fields to register:
        # mychip.GPIO.GPIO_dir


        
        write_field_cominbinations(reg=self.dut.GPIO.GPIO_dir,
                                   writable_fields = [ 'PIN_0'
                                                       ])
        
        
        # test read_fields to register:
        # mychip.GPIO.GPIO_state


        
        write_field_cominbinations(reg=self.dut.GPIO.GPIO_state,
                                   writable_fields = [ 'PIN_0'
                                                       ])
        




if __name__ == '__main__':
    unittest.main()



