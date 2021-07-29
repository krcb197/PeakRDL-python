
import logging
from typing import Callable, TypeVar

read_callback_type = Callable[[int], int]
write_callback_type = Callable[[int, int], type(None)]


class _Base:

    __slots__ = ['__logger']

    def __init__(self, logger_handle):
        self.__logger = logging.getLogger(logger_handle)
        self._logger.info(f'creating instance of {self.__class__}')

    @property
    def _logger(self):
        return self.__logger


class _Node(_Base):
    __slots__ = ['__base_address', '__address_width', '__data_width']

    def __init__(self, base_address, address_width, data_width, logger_handle):
        super().__init__(logger_handle=logger_handle)
        self.__base_address = base_address
        self.__address_width = address_width
        self.__data_width = data_width

    @property
    def base_address(self) -> int:
        return self.__base_address

    @property
    def address_width(self) -> int:
        return self.__address_width

    @property
    def data_width(self) -> int:
        """
        width of the data access in bits
        """
        return self.__data_width


class AddressMap(_Node):

    __slots__ = []

    pass


class RegFile(_Node):

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
                 base_address,
                 address_width,
                 data_width,
                 logger_handle):
        super().__init__(base_address=base_address,
                         address_width=address_width,
                         data_width=data_width,
                         logger_handle=logger_handle)
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
                 base_address,
                 address_width,
                 data_width,
                 logger_handle):
        super().__init__(base_address=base_address,
                         address_width=address_width,
                         data_width=data_width,
                         logger_handle=logger_handle)
        self.__write_callback = write_callback

    def write(self, data: int):
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
                 logger_handle: str):
        super().__init__(base_address=base_address,
                         address_width=address_width,
                         data_width=data_width,
                         logger_handle=logger_handle)
        self.__write_callback = write_callback
        self.__read_callback = read_callback

    def write(self, data: int):
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

    __slots__ = ['__parent_register', '__msb', '__lsb', '__bitmask']

    def __init__(self, parent_register: Reg,
                 msb: int, lsb: int, logger_handle: str):

        super().__init__(logger_handle=logger_handle)

        if not isinstance(parent_register, Reg):
            raise TypeError('parent register must be of type reg_cls '
                            'but got %s' % type(parent_register))
        self.__parent_register = parent_register

        if msb < lsb:
            raise ValueError('field msb can not be less than the lsb')

        if lsb < 0:
            raise ValueError('field lsb cannot be less than zero')

        if msb > self.parent_register.data_width:
            raise ValueError('field msb must be less than the parent register width')

        if lsb > self.parent_register.data_width:
            raise ValueError('field lsb must be less than the parent register width')

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
    def field_width(self) -> int:
        """
        The width of the field in bits
        """
        return self.msb - self.lsb + 1

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the field

        For example:

        * 8-bit field returns 0xFF (255)
        * 16-bit field returns 0xFFFF (65535)
        * 32-bit field returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.field_width) - 1

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
        lsb: bit position of the field lsb in the register
        msb: bit position of the field lsb in the register
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ = []

    def __init__(self, parent_register: readable_reg_type,
                 msb: int, lsb: int, logger_handle: str):

        if not isinstance(parent_register, (RegReadWrite, RegReadOnly)):
            raise TypeError('parent register must be of type reg_cls but'
                            ' got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle,
                         msb=msb, lsb=lsb,
                         parent_register=parent_register)

    def read(self):
        return (self.parent_register.read() & self.bitmask) >> self.lsb

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
        lsb: bit position of the field lsb in the register
        msb: bit position of the field lsb in the register
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ = []

    def __init__(self, parent_register: writeable_reg_type,
                 msb: int, lsb: int, logger_handle: str):

        if not isinstance(parent_register, (RegReadWrite, RegWriteOnly)):
            raise TypeError('parent register must be of type reg_cls but '
                            'got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle,
                         msb=msb,
                         lsb=lsb,
                         parent_register=parent_register)

    def write(self, value):
        # TODO need to consider what makes sense here, the following special
        #      cases can be handled
        #      * field is the same width as the reg
        #      * there is only one field in the reg
        #      other case don't make that much sense
        raise NotImplementedError('Need to make a decision about what '
                                  'behaviour happens here')

    @Field.parent_register.getter
    def parent_register(self) -> writeable_reg_type:
        return super().parent_register


class FieldReadWrite(FieldReadOnly, FieldWriteOnly):
    """
    class for a read/write only register field

    Args:
        parent_register: register within which the field resides
        lsb: bit position of the field lsb in the register
        msb: bit position of the field lsb in the register
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ = []

    def __init__(self, parent_register: RegReadWrite,
                 msb: int,
                 lsb: int,
                 logger_handle: str):

        if not isinstance(parent_register, RegReadWrite):
            raise TypeError('parent register must be of type reg_cls but'
                            ' got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle,
                         msb=msb,
                         lsb=lsb,
                         parent_register=parent_register)

    def write(self, value):

        if not isinstance(value, int):
            raise TypeError('value must be an int but got %s' % type(value))

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError('value to be written to register must be less '
                             'than or equal to %d' % self.max_value)

        if (self.msb == (self.parent_register.data_width-1)) and\
                (self.lsb == 0):
            # special case where the field occupies the whole register,
            # there a straight write can be performed
            new_reg_value = value
        else:
            # do a read, modify write
            reg_value = self.parent_register.read()
            masked_reg_value = reg_value & self.inverse_bitmask

            new_reg_value = masked_reg_value | (value << self.lsb)

        self.parent_register.write(new_reg_value)

    @Field.parent_register.getter
    def parent_register(self) -> RegReadWrite:
        return super().parent_register
