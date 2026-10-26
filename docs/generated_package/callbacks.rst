Callbacks
*********

The Register Access Layer will typically interfaced to a driver that
allows accesses the chip.

.. tip:: The simulator generated with the register model can be used as an alternative to
         a hardware connection

In order to operate the register access layer typically requires the following:

- A callback for a single register write, this not required if there is no writable register in
  the register access layer
- A callback for a single register read, this not required if there is no writable register in
  the register access layer

In addition the register access layer can make use of block operations where a block of the
address space is read in a single transaction. Not all drivers support these

The examples of these two methods are included within the generated register
access layer package so that it can be used from the console:

.. code-block:: python

    def read_addr_space(addr: int, width: int, accesswidth: int) -> int:
        """
        Callback to simulate the operation of the package, everytime the read is called, it will
        request the user input the value to be read back.

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits

        Returns:
            value inputted by the used
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        return input('value to read from address:0x%X' % addr)

    def write_addr_space(addr: int, width: int, accesswidth: int, data: int) -> None:
        """
        Callback to simulate the operation of the package, everytime the write is called, it will
        print out the result.

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits
            data: value to be written to the register

        Returns:
            None
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        assert isinstance(data, int)
        print('write data:0x%X to address:0x%X' % (data, addr))

In a real system these call backs will be connected to a driver.

In addition there is also an option to use ``async`` callbacks if the package is built
``asyncoutput`` set to True.

Callback Set
============

The callbacks are passed into the register access layer using either:

* ``NormalCallbackSet`` for standard python function callbacks
* ``AsyncCallbackSet`` for async python function callbacks, these are called from the library using
  ``await``

Legacy Block Callback and Block Access
======================================

.. versionchanged:: 0.9.0

   Previous versions of PeakRDL Python used the python ``array.array`` for efficiently moving blocks
   of data. This was changed in version 0.9.0 in order to accommodate memories which were larger
   than 64 bit wide which could not be supported as the array type only support entries of up to
   64 bit.

   .. warning::
      The developers apologise for making a breaking change, however, not being able to fully the
      systemRDL specification was determined to be a major limitation that needed to be addressed.

      It could have left this as a future compatibility mode before making a breaking change but
      that would just delay the pain it was felt to be better to get as many users onto the new
      API as soon as possible whilst PeakRDL Python is in beta.

   If you really want to just keep on with the array based interface and make only minimal changes
   to existing code, there are two simple steps:

   1. The northbound interfaces that are provided by the generated package expect lists of integers
      rather than array. The old interfaces can be retained by using the ``legacy_block_access``
      build option.
   2. The southbound interfaces into the callbacks again need to use lists for the
      ``read_block_callback`` and ``write_block_callback`` methods. If you want to continue to use
      the old scheme use the following callback classes which are part of the callbacks:
      * ``NormalCallbackSetLegacy`` for standard python function callbacks
      * ``AsyncCallbackSetLegacy`` for async python function callbacks, these are called from the library using ``await``

.. versionchanged:: 3.0.0

    The ``legacy_block_access`` will now default to ``False``

.. versionchanged:: 4.0.0

    The ``legacy_block_access`` was removed, the ``NormalCallbackSetLegacy`` and ``AsyncCallbackSetLegacy`` are no longer supported