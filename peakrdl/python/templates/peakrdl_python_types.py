
import logging
from typing import Callable, TypeVar, NoReturn

read_callback_type = Callable[[int], int]
write_callback_type = Callable[[int, int], type(None)]


class _Base:

    __slots__ = ['__logger','__inst_name']

    def __init__(self, logger_handle: str, inst_name:str):
        self.__logger = logging.getLogger(logger_handle)
        self._logger.info(f'creating instance of {self.__class__}')

        self.__inst_name = inst_name

    @property
    def _logger(self) -> logging.Logger:
        return self.__logger

    @property
    def inst_name(self) -> str:
        """
        name of the instance in the parent
        """
        return self.__inst_name


class _Node(_Base):
    __slots__ = ['__base_address', '__address_width', '__data_width']

    def __init__(self,
                 base_address: int,
                 address_width: int,
                 data_width: int,
                 logger_handle: str,
                 inst_name: str):
        super().__init__(logger_handle=logger_handle, inst_name=inst_name)
        self.__base_address = base_address
        self.__address_width = address_width
        self.__data_width = data_width


    @property
    def base_address(self) -> int:
        """
        address of the node
        """
        return self.__base_address

    @property
    def address_width(self) -> int:
        """
        width of the address in bits
        """
        return self.__address_width

    @property
    def data_width(self) -> int:
        """
        width of the data access in bits
        """
        return self.__data_width




class AddressMap(_Node):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = []

    pass


class RegFile(_Node):
    """
    base class of register file wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = []

    pass


class Reg(_Node):
    """
    base class of register wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = []

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the register

        For example:

        * 8-bit register returns 0xFF (255)
        * 16-bit register returns 0xFFFF (65535)
        * 32-bit register returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.data_width) - 1


class RegReadOnly(Reg):
    """
    class for a read only register

    Args:
        read_callback: function that is called with the address of the register
            when the read method of this class is called. This will normally be
            linked to the read method of a device driver or the register
            simulator
        base_address: register address (to be pass into the read callback)
        address_width: width of the address in bits
        data_width: width of the register access in bits
        logger_handle: name to be used logging messages associate with this
            object

    Note:
        The actual width of the register may be less then the data_width, the
        width refers to the width of a "normal" read/write operation

    """

    __slots__ = ['__read_callback']

    def __init__(self,
                 read_callback: read_callback_type,
                 base_address: int,
                 address_width: int,
                 data_width: int,
                 logger_handle: str,
                 inst_name: str):
        super().__init__(base_address=base_address,
                         address_width=address_width,
                         data_width=data_width,
                         logger_handle=logger_handle,
                         inst_name=inst_name)
        self.__read_callback = read_callback

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register

        """
        return self.__read_callback(self.base_address)


class RegWriteOnly(Reg):
    """
    class for a write only register

    Args:
        write_callback: function that is called with the address of the register
            when the write method of this class is called. This will normally be
            linked to the write method of a device driver or the register
            simulator
        base_address: register address (to be pass into the read callback)
        address_width: width of the address in bits
        data_width: width of the register access in bits
        logger_handle: name to be used logging messages associate with this
            object

    Note:
        The actual width of the register may be less then the data_width, the
        width refers to the width of a "normal" read/write operation
    """

    __slots__ = ['__write_callback']

    def __init__(self, write_callback: write_callback_type,
                 base_address: int,
                 address_width: int,
                 data_width: int,
                 logger_handle: str,
                 inst_name: str):
        super().__init__(base_address=base_address,
                         address_width=address_width,
                         data_width=data_width,
                         logger_handle=logger_handle,
                         inst_name=inst_name)
        self.__write_callback = write_callback

    def write(self, data: int) -> NoReturn:
        """Writes a value to the register

        Args:
            data: data to be written

        Raises:
            ValueError: if the value provided is outside the range of the
                permissible values for the register
            TypeError: if the type of data is wrong
        """
        if not isinstance(data, int):
            raise TypeError(f'data should be an int got {type(data)=}')

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

        self._logger.info(f'Writing data:{data:X} to '
                          f'address:{self.base_address:X}')

        self.__write_callback(self.base_address, data)


class RegReadWrite(Reg):
    """
    class for a write only register

    Args:
        read_callback: function that is called with the address of the register
            when the read method of this class is called. This will normally be
            linked to the read method of a device driver or the register
            simulator
        write_callback: function that is called with the address of the register
            when the write method of this class is called. This will normally be
            linked to the write method of a device driver or the register
            simulator
        base_address: register address (to be pass into the read callback)
        address_width: width of the address in bits
        data_width: width of the register access in bits
        logger_handle: name to be used logging messages associate with this
            object

    Note:
        The actual width of the register may be less then the data_width, the
        width refers to the width of a "normal" read/write operation
    """
    __slots__ = ['__write_callback', '__read_callback']

    def __init__(self, write_callback: write_callback_type,
                 read_callback: read_callback_type,
                 base_address: int,
                 address_width: int,
                 data_width: int,
                 logger_handle: str,
                 inst_name: str):
        super().__init__(base_address=base_address,
                         address_width=address_width,
                         data_width=data_width,
                         logger_handle=logger_handle,
                         inst_name=inst_name)
        self.__write_callback = write_callback
        self.__read_callback = read_callback

    def write(self, data: int) -> NoReturn:
        """Writes a value to the register

        Args:
            data: data to be written

        Raises:
            ValueError: if the value provided is outside the range of the
                permissible values for the register
            TypeError: if the type of data is wrong
        """
        if not isinstance(data, int):
            raise TypeError(f'data should be an int got {type(data)=}')

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

        self._logger.info(f'Writing data:0x{data:X} to '
                          f'address:0x{self.base_address:X}')

        self.__write_callback(self.base_address, data)

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register

        """
        return self.__read_callback(self.base_address)


class Field(_Base):
    """
    base class of register feild wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = ['__parent_register', '__msb', '__lsb', '__bitmask', '__width']

    def __init__(self, parent_register: Reg, width: int,
                 msb: int, lsb: int, logger_handle: str, inst_name: str):

        super().__init__(logger_handle=logger_handle,
                         inst_name=inst_name)

        if not isinstance(parent_register, Reg):
            raise TypeError('parent register must be of type reg_cls '
                            'but got %s' % type(parent_register))
        self.__parent_register = parent_register

        if width < 1:
            raise ValueError('width must be greater than 0')

        if width > self.parent_register.data_width:
            raise ValueError('width can not be greater than parent width')

        self.__width = width

        if msb < lsb:
            raise ValueError('field msb can not be less than the lsb')

        if lsb < 0:
            raise ValueError('field lsb cannot be less than zero')

        if msb > self.parent_register.data_width:
            raise ValueError('field msb must be less than the parent register width')

        if lsb > self.parent_register.data_width:
            raise ValueError('field lsb must be less than the parent register width')

        if msb - lsb + 1 != width:
            raise ValueError('field width defined by lsb and msb does not match specified width')

        self.__msb = msb
        self.__lsb = lsb

        self.__bitmask = 0
        for bit_position in range(self.__lsb, self.__msb+1):
            self.__bitmask |= (1 << bit_position)

    @property
    def parent_register(self) -> Reg:
        """
        Register within which the field is located

        Note:
            This is an advanced user feature, and will not be needed in most
            normal usage
        """
        return self.__parent_register

    @property
    def lsb(self) -> int:
        """
        bit position of the least significant bit (lsb) of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__lsb

    @property
    def msb(self) -> int:
        """
        bit position of the most significant bit (msb) of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__msb

    @property
    def width(self) -> int:
        """
        The width of the field in bits
        """
        return self.__width

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the field

        For example:

        * 8-bit field returns 0xFF (255)
        * 16-bit field returns 0xFFFF (65535)
        * 32-bit field returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    @property
    def bitmask(self) -> int:
        """
        The bit mask needed to extract the field from its register

        For example a register field occupying bits 7 to 4 in a 16-bit register
        will have a bit mask of 0x00F0
        """
        return self.__bitmask

    @property
    def register_data_width(self) -> int:
        """
        The width of the register within which the field resides in bits
        """
        return self.parent_register.data_width

    @property
    def inverse_bitmask(self) -> int:
        """
        The bitwise inverse of the bitmask needed to extract the field from its
        register

        For example a register field occupying bits 7 to 4 in a 16-bit register
        will have a inverse bit mask of 0xFF0F
        """
        return self.parent_register.max_value ^ self.bitmask


readable_reg_type = TypeVar('readable_reg_type', RegReadOnly, RegReadWrite)


class FieldReadOnly(Field):
    """
    class for a read only register field

    Args:
        parent_register: register within which the field resides
        width: field width in bits
        lsb: bit position of the field lsb in the register
        msb: bit position of the field lsb in the register
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ = []

    def __init__(self, parent_register: readable_reg_type, width:int,
                 msb: int, lsb: int, logger_handle: str, inst_name: str):

        if not isinstance(parent_register, (RegReadWrite, RegReadOnly)):
            raise TypeError('parent register must be of type reg_cls but'
                            ' got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle,
                         width=width,
                         msb=msb, lsb=lsb,
                         parent_register=parent_register,
                         inst_name=inst_name)

    def decode_read_value(self, value) -> int:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value
        """
        if not isinstance(value, int):
            raise TypeError('value must be an int but got %s' % type(value))

        if value < 0:
            raise ValueError('value to be decoded must be greater '
                             'than or equal to 0')

        if value > self.parent_register.max_value:
            raise ValueError(f'value to bede coded must be less than or equal '
                             f'to {self.parent_register.max_value:d}')

        return (value & self.bitmask) >> self.lsb

    def read(self) -> int:
        """
        Reads the register that this field is located in and retries the field
        value applying the required masking and shifting

        Returns:
            field value

        """
        return self.decode_read_value(self.parent_register.read())

    @Field.parent_register.getter
    def parent_register(self) -> readable_reg_type:
        assert isinstance(super().parent_register, (RegReadOnly, RegReadWrite))
        return super().parent_register


writeable_reg_type = TypeVar('writeable_reg_type', RegWriteOnly, RegReadWrite)


class FieldWriteOnly(Field):
    """
    class for a write only register field

    Args:
        parent_register: register within which the field resides
        width: field width in bits
        lsb: bit position of the field lsb in the register
        msb: bit position of the field lsb in the register
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ = []

    def __init__(self, parent_register: writeable_reg_type, width:int,
                 msb: int, lsb: int, logger_handle: str, inst_name: str):

        if not isinstance(parent_register, (RegReadWrite, RegWriteOnly)):
            raise TypeError('parent register must be of type reg_cls but '
                            'got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle,
                         width=width,
                         msb=msb,
                         lsb=lsb,
                         parent_register=parent_register,
                         inst_name=inst_name)

    def encode_write_value(self, value: int) -> int:

        if not isinstance(value, int):
            raise TypeError('value must be an int but got %s' % type(value))

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError('value to be written to register must be less '
                             'than or equal to %d' % self.max_value)

        return value << self.lsb

    def write(self, value: int) -> NoReturn:
        """
        The behaviour of this method depends on whether the field is located in
        a readable register or not:

        If the register is readable, the method will perform a read-modify-write
        on the register updating the field with the value provided

        If the register is not writable all other field values will be written
        with zero.

        Args:
            value: field value to update to

        """

        if not isinstance(value, int):
            raise TypeError('value must be an int but got %s' % type(value))

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError('value to be written to register must be less '
                             'than or equal to %d' % self.max_value)

        if (self.msb == (self.parent_register.data_width - 1)) and \
                (self.lsb == 0):
            # special case where the field occupies the whole register,
            # there a straight write can be performed
            new_reg_value = (value << self.lsb)
        else:
            # do a read, modify write
            if isinstance(self.parent_register, RegReadWrite):
                reg_value = self.parent_register.read()
                masked_reg_value = reg_value & self.inverse_bitmask
                new_reg_value = masked_reg_value | (value << self.lsb)
            elif isinstance(self.parent_register, RegWriteOnly):
                new_reg_value = (value << self.lsb)
            else:
                raise TypeError('Unhandled parent type')

        self.parent_register.write(new_reg_value)

    @Field.parent_register.getter
    def parent_register(self) -> writeable_reg_type:
        return super().parent_register


class FieldReadWrite(FieldReadOnly, FieldWriteOnly):
    """
    class for a read/write only register field

    Args:
        parent_register: register within which the field resides
        width: field width in bits
        lsb: bit position of the field lsb in the register
        msb: bit position of the field lsb in the register
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ = []

    def __init__(self, parent_register: RegReadWrite,
                 width: int,
                 msb: int,
                 lsb: int,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, RegReadWrite):
            raise TypeError('parent register must be of type reg_cls but'
                            ' got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle,
                         width=width,
                         msb=msb,
                         lsb=lsb,
                         parent_register=parent_register,
                         inst_name=inst_name)

    @Field.parent_register.getter
    def parent_register(self) -> RegReadWrite:
        return super().parent_register
