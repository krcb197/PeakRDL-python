"""Python Wrapper for the mychip register model

This code was generated from the PeakRDL-python package

"""
from enum import IntEnum, unique
from typing import Tuple, NoReturn
from typing import Iterable

from ..peakrdl_python import AddressMap, RegFile
from ..peakrdl_python import RegReadOnly, RegWriteOnly, RegReadWrite
from ..peakrdl_python import FieldReadOnly, FieldWriteOnly, FieldReadWrite
from ..peakrdl_python import FieldSizeProps, Field
from ..peakrdl_python import CallbackSet







# root level enum definitions
@unique
class mychip_GPIO_block_GPIO_direction_enumcls(IntEnum):

    dir_in = 0# GPIO direction into chip
    dir_out = 1# GPIO direction out of chip
    



# regfile, register and field definitions
        
    
class mychip_GPIO_block_GPIO_direction_field_type_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """
    __enum_cls = mychip_GPIO_block_GPIO_direction_enumcls
    

    __slots__ = []
    @property
    def enum_cls(self):
        """
        The enumeration class for this field
        """
        return self.__enum_cls
    def decode_read_value(self, reg_value: int) -> mychip_GPIO_block_GPIO_direction_enumcls:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed and conversion to the enum associated with the
        field

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value

        Raises:
            ValueError - if the value read back for the field can not be matched to the enum
        """
        field_value = super().decode_read_value(reg_value)

        return self.enum_cls(field_value)

    def read(self) -> mychip_GPIO_block_GPIO_direction_enumcls:
        """
        read the register and then perform the necessary actions, to report the
        value as the enumeration including:

        * application of bit mask
        * bit shifting
        * converting integer value to enum

        Returns:
            field value
        """
        reg_value = self.parent_register.read()
        return self.decode_read_value(reg_value=reg_value)
        
    def encode_write_value(self, value: mychip_GPIO_block_GPIO_direction_enumcls) -> int:

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an mychip_GPIO_block_GPIO_direction_enumcls but got %s' % type(value))

        return super().encode_write_value(value.value)

    def write(self, value : mychip_GPIO_block_GPIO_direction_enumcls) -> NoReturn:

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an mychip_GPIO_block_GPIO_direction_enumcls but got %s' % type(value))

        super().write(value.value)
        
    
    

        
class mychip_GPIO_block_GPIO_dir_cls(RegReadWrite):
    """
    Class to represent a register in the register model

    +--------------+-------------------------------------------------------------------------+
    | SystemRDL    | Value                                                                   |
    | Field        |                                                                         |
    +==============+=========================================================================+
    | Name         | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      GPIO Direction                                                     |
    +--------------+-------------------------------------------------------------------------+
    | Description  | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      <p>Register to set the direction of each GPIO pin</p>              |
    +--------------+-------------------------------------------------------------------------+
    """

    __slots__ = ['__PIN_0']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str):

        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name)

        # build the field attributes
        self.__PIN_0 = mychip_GPIO_block_GPIO_direction_field_type_cls(parent_register=self,
                                                                                 size_props=FieldSizeProps( width=1,
                                                                                                             lsb=0,
                                                                                                             msb=0,
                                                                                                             low=0,
                                                                                                             high=0),
                                                                                 logger_handle=logger_handle+'.PIN_0',
                                                                                 inst_name='PIN_0')

    
    def read_fields(self):
        """
        read the register and return a dictionary of the field values
        """
        reg_value = self.read()

        return_dict = {
                        'PIN_0' : self.PIN_0.decode_read_value(reg_value)
                      }

        return return_dict

    @property
    def readable_fields(self) -> Iterable[Field]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.PIN_0
        

    

    
    @property
    def writable_fields(self) -> Iterable[Field]:
        """
        generator that produces has all the writable fields within the register
        """
        yield self.PIN_0
        

    
    def write_fields(self, **kwargs) -> NoReturn:
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """

        if len(kwargs) == 0:
            raise ValueError('no command args')

        bit_mask = 0
        reg_value = 0
        if 'PIN_0' in kwargs:
            reg_value |= self.PIN_0.encode_write_value(kwargs['PIN_0'])
            bit_mask |= self.PIN_0.bitmask
            kwargs.pop('PIN_0')
        if len(kwargs) != 0:
            # left over unhandled arguments
            raise ValueError('unrecognised arguments in field')

        inverse_bit_mask = self.max_value ^ bit_mask

        self.write((self.read() & inverse_bit_mask) | reg_value)

    
    

    # build the properties for the fields
    @property
    def PIN_0(self) -> mychip_GPIO_block_GPIO_direction_field_type_cls:
        return self.__PIN_0
        
    

        
    
class mychip_GPIO_block_GPIO_output_field_type_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """

    __slots__ = []
    

        
class mychip_GPIO_block_GPIO_state_cls(RegReadWrite):
    """
    Class to represent a register in the register model

    +--------------+-------------------------------------------------------------------------+
    | SystemRDL    | Value                                                                   |
    | Field        |                                                                         |
    +==============+=========================================================================+
    | Name         | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      GPIO Set State                                                     |
    +--------------+-------------------------------------------------------------------------+
    | Description  | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      <p>Register to set the state of a GPIO Pin</p>                     |
    +--------------+-------------------------------------------------------------------------+
    """

    __slots__ = ['__PIN_0']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str):

        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name)

        # build the field attributes
        self.__PIN_0 = mychip_GPIO_block_GPIO_output_field_type_cls(parent_register=self,
                                                                                 size_props=FieldSizeProps( width=1,
                                                                                                             lsb=0,
                                                                                                             msb=0,
                                                                                                             low=0,
                                                                                                             high=0),
                                                                                 logger_handle=logger_handle+'.PIN_0',
                                                                                 inst_name='PIN_0')

    
    def read_fields(self):
        """
        read the register and return a dictionary of the field values
        """
        reg_value = self.read()

        return_dict = {
                        'PIN_0' : self.PIN_0.decode_read_value(reg_value)
                      }

        return return_dict

    @property
    def readable_fields(self) -> Iterable[Field]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.PIN_0
        

    

    
    @property
    def writable_fields(self) -> Iterable[Field]:
        """
        generator that produces has all the writable fields within the register
        """
        yield self.PIN_0
        

    
    def write_fields(self, **kwargs) -> NoReturn:
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """

        if len(kwargs) == 0:
            raise ValueError('no command args')

        bit_mask = 0
        reg_value = 0
        if 'PIN_0' in kwargs:
            reg_value |= self.PIN_0.encode_write_value(kwargs['PIN_0'])
            bit_mask |= self.PIN_0.bitmask
            kwargs.pop('PIN_0')
        if len(kwargs) != 0:
            # left over unhandled arguments
            raise ValueError('unrecognised arguments in field')

        inverse_bit_mask = self.max_value ^ bit_mask

        self.write((self.read() & inverse_bit_mask) | reg_value)

    
    

    # build the properties for the fields
    @property
    def PIN_0(self) -> mychip_GPIO_block_GPIO_output_field_type_cls:
        return self.__PIN_0
        
    

        
class mychip_GPIO_block_cls(AddressMap):
    """
    Class to represent a address map in the register model

    +--------------+-------------------------------------------------------------------------+
    | SystemRDL    | Value                                                                   |
    | Field        |                                                                         |
    +==============+=========================================================================+
    | Name         | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      GPIO Block                                                         |
    +--------------+-------------------------------------------------------------------------+
    | Description  | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      <p>GPIO Block with configurable direction pins</p>                 |
    +--------------+-------------------------------------------------------------------------+
    """

    __slots__ = ['__GPIO_dir', '__GPIO_state']

    def __init__(self,
                 callbacks: CallbackSet,
                 address:int,
                 logger_handle:str,
                 inst_name):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name)

        
        self.__GPIO_dir = mychip_GPIO_block_GPIO_dir_cls(callbacks=callbacks,
                                                                     address=self.address+4,
                                                                     logger_handle=logger_handle+'.GPIO_dir',
                                                                                       inst_name='GPIO_dir')
        
        self.__GPIO_state = mychip_GPIO_block_GPIO_state_cls(callbacks=callbacks,
                                                                     address=self.address+8,
                                                                     logger_handle=logger_handle+'.GPIO_state',
                                                                                       inst_name='GPIO_state')
        
    @property
    def GPIO_dir(self) ->  mychip_GPIO_block_GPIO_dir_cls:
        return self.__GPIO_dir
        
    @property
    def GPIO_state(self) ->  mychip_GPIO_block_GPIO_state_cls:
        return self.__GPIO_state
        
    

        
class mychip_cls(AddressMap):
    """
    Class to represent a address map in the register model

    +--------------+-------------------------------------------------------------------------+
    | SystemRDL    | Value                                                                   |
    | Field        |                                                                         |
    +==============+=========================================================================+
    | Name         | .. raw:: html                                                           |
    |              |                                                                         |
    |              |      My Chip                                                            |
    +--------------+-------------------------------------------------------------------------+
    """

    __slots__ = ['__GPIO']

    def __init__(self,
                 callbacks: CallbackSet,
                 address:int=0,
                 logger_handle:str='reg_model.mychip',
                 inst_name='mychip'):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name)

        self.__GPIO = mychip_GPIO_block_cls(callbacks=callbacks,
                                                                                address=self.address+0,
                                                                                logger_handle=logger_handle+'.GPIO',
                                                                                inst_name='GPIO')
        
    @property
    def GPIO(self) ->  mychip_GPIO_block_cls:
        return self.__GPIO
        
    



if __name__ == '__main__':
    # dummy functions to demonstrate the class
    def read_addr_space(addr: int, width: int, accesswidth: int) -> int:
        """
        Callback to simulate the operation of the package, everytime the read is called, it will
        request the user input the value to be read back.

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimium access width of the register in bits

        Returns:
            value inputted by the used
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        return input('value to read from address:0x%X'%addr)

    def write_addr_space(addr: int, width: int, accesswidth: int, data: int) -> NoReturn:
        """
        Callback to simulate the operation of the package, everytime the read is called, it will
        request the user input the value to be read back.

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimium access width of the register in bits
            data: value to be written to the register

        Returns:
            None
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        assert isinstance(data, int)
        print('write data:0x%X to address:0x%X'%(data, addr))

    # create an instance of the class
    mychip = mychip_cls(read_callback=read_addr_space, write_callback=write_addr_space)