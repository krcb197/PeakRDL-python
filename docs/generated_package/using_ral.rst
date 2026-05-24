Using the Register Access Layer
*******************************

The register access layer package is intended to integrated into another
piece of code. That code could be a simple test script for blinking an LED on a
GPIO or it could be a more complex application with a GUI.

The following example is a chip that has a GPIO block. The GPIO block has two
registers:

1. one register that controls the direction of the GPIO pin, at address 0x4
2. one register that controls driven state of the GPIO pin, at address 0x8

This can be described with the following systemRDL code:

.. literalinclude :: ../../example/simulating_callbacks/chip_with_a_GPIO.rdl
   :language: systemrdl

This systemRDL code can be built using the command line tool as follows (assuming it is stored in
a file called ``chip_with_a_GPIO.rdl``:

.. code-block:: bash

    peakrdl python chip_with_a_GPIO.rdl -o python_output
    python -m unittest discover -s python_output

.. tip:: It is always good practice to run the unittests on the generated code.

Once the register access layer has been generated and it can be used. The following example
does not actually use a device driver. Instead it chip simulator with a Tkinter GUI,
incorporating a RED circle to represent the LED. The chip simulator has read and write methods (
equivalent to those offered by a hardware device driver), in this case they use the simulator
provided by PeakRDL Python.

.. literalinclude :: ../../example/simulating_callbacks/flashing_the_LED.py
   :language: python

.. warning:: In most cases when writing to a read-write register, PeakRDL Python will use a read modify write operation.
             There are some cases where this is not desirable, for example in the case of a register where a read
             triggers an action in the hardware e.g. incrementing a counter.

Enumerated Fields
=================

Enumerations are a good practice to implicitly encode that have special meanings which can not be
easily understood from the field name. The SystemRDL enumerations are implemented using python

.. literalinclude :: ../../example/enumerated_fields/enumerated_fields.rdl
   :language: systemrdl

This systemRDL code can be built using the command line tool as follows (assuming it is stored in
a file called ``enumerated_fields.rdl``):

.. code-block:: bash

    peakrdl python enumerated_fields.rdl -o .

The following example shows the usage of the enumeration

.. note::
   In order to set the value of an enumerated field, using the ``write()`` method. The correct
   enumerated class is needed. This can be retrieved from the field itself with the ``enum_cls``
   property

.. literalinclude :: ../../example/enumerated_fields/demo_enumerated_fields.py
   :language: python

Array Access
============

SystemRDL supports multi-dimensional arrays, the following example shows an definition with an 1D
and 3D array with various methods to access individual elements of the array and use of the
iterators to walk through elements in loops

.. literalinclude :: ../../example/array_access/array_access.rdl
   :language: systemrdl

This systemRDL code can be built using the command line tool as follows (assuming it is stored in
a file called ``array_access.rdl``):

.. code-block:: bash

    peakrdl python array_access.rdl -o .

.. literalinclude :: ../../example/array_access/demo_array_access.py
   :language: python

Write Only Registers
====================

TBA

Optimised Access
================

Working with individual registers
---------------------------------

Each time the ``read`` or ``write`` method for a register field is accessed the hardware is read
and or written (a write to a field will normally require a preceding read). When accessing multiple
fields in the same register, it may be desirable to use one of the optimised access methods.

Consider the following example of an GPIO block with 4 GPIO pins (configured in a single register):

.. literalinclude :: ../../example/optimised_access/optimised_access.rdl
   :language: systemrdl

In the to configure gpio_0 and gpio_1 whilst leaving the other two unaffected it can be done in two
methods:

* using the ``write_fields`` method of the register, which carries out a single read and write of any field specified
  in the arguments
* using the register context manager

Both demonstrated in the following code example:

.. literalinclude :: ../../example/optimised_access/demo_optimised_access.py
   :language: python

Avoiding the Read on a Read/Write Register
------------------------------------------

TBA


Working with registers arrays
-----------------------------

In many systems it is more efficient to read and write in block operations rather than using
individual register access.

Consider the following example of an GPIO block with 8 GPIO pins (configured in a 8 registers):

.. literalinclude :: ../../example/optimised_access/optimised_array_access.rdl
   :language: systemrdl

In order to configure all the GPIOs a range of operations are shown with the use of the context
managers to make more efficient operations

.. literalinclude :: ../../example/optimised_access/demo_optimised_array_access.py
   :language: python

Walking the Structure
=====================

The following two example show how to use the generators within the register access layer
package to traverse the structure.

Both examples use the following register set which has a number of features to demonstrate the
structures

.. literalinclude :: ../../example/tranversing_address_map/chip_with_registers.rdl
   :language: systemrdl

This systemRDL code can be built using the command line tool as follows (assuming it is stored in
a file called ``chip_with_registers.rdl``):

.. code-block:: bash

   peakrdl python chip_with_registers.rdl -o chip_with_registers


Traversing without Unrolling Loops
----------------------------------

The first example is reading all the readable registers from the register map and writing them
into a JSON file. To exploit the capabilities of a JSON file the arrays of registers and
register files must be converted to python lists, therefore the loops must not be unrolled, the
array objects are accessed directly.

.. literalinclude :: ../../example/tranversing_address_map/dumping_register_state_to_json_file.py
   :language: python

This will create a JSON file as follows:

.. code-block:: json

    {
        "regfile_array": [
            {
                "single_reg": {
                    "first_field": 0,
                    "second_field": 0
                },
                "reg_array": [
                    {
                        "first_field": 0,
                        "second_field": 0
                    },
                    {
                        "first_field": 0,
                        "second_field": 0
                    },
                    {
                        "first_field": 0,
                        "second_field": 0
                    },
                    {
                        "first_field": 0,
                        "second_field": 0
                    }
                ]
            },
            {
                "single_reg": {
                    "first_field": 0,
                    "second_field": 0
                },
                "reg_array": [
                    {
                        "first_field": 0,
                        "second_field": 0
                    },
                    {
                        "first_field": 0,
                        "second_field": 0
                    },
                    {
                        "first_field": 0,
                        "second_field": 0
                    },
                    {
                        "first_field": 0,
                        "second_field": 0
                    }
                ]
            }
        ],
        "single_regfile": {
            "single_reg": {
                "first_field": 0,
                "second_field": 0
            },
            "reg_array": [
                {
                    "first_field": 0,
                    "second_field": 0
                },
                {
                    "first_field": 0,
                    "second_field": 0
                },
                {
                    "first_field": 0,
                    "second_field": 0
                },
                {
                    "first_field": 0,
                    "second_field": 0
                }
            ]
        }
    }

Traversing without Unrolling Loops
----------------------------------

The second example is setting every register in the address map back to its default values. In
this case the loops are unrolled to conveniently access all the register without needing to
worry if they are in an array or not.

.. literalinclude :: ../../example/tranversing_address_map/reseting_registers.py
   :language: python

Exposing User Defined Properties
================================

SystemRDL allows properties to be added to any component (Field, Memory, Register, Register File,
Address Map), so called *User Defined Properties (UDP)*.

There are two methods to expose user defined properties:

- A list of strings to include in the package
- A Regular Expression which will include any UDP which matches the regular expression

Consider the following systemRDL example with a user defined property: ``component_usage``

.. literalinclude :: ../../example/user_defined_properties/user_defined_properties.rdl
   :language: systemrdl

User Defined Properties are not automatically included they must be specified, as shown:

.. code-block:: bash

   peakrdl python user_defined_properties.rdl -o . --udp component_usage

Alternatively the User Defined Properties can be included with a regular expression.
In the following case all UDPs are included, except the ones used by PeakRDL python

.. code-block:: bash

   peakrdl python user_defined_properties.rdl -o . --udp_regex "^(?!python_hide$)(?!python_name$).+"

.. warning::

   Attempting to use both the list and regular expression approach is not supported and will
   generate an error

The user defined properties are stored in a ``udp`` property of all component in the generated
register access and can be accessed as follows:

.. literalinclude :: ../../example/user_defined_properties/demo_user_defined_properties.py
   :language: python

.. versionadded:: 2.0.0

    Regular Expression matching for User Defined Properties was added in version 2.0.0

Python Safe Names
=================

The systemRDL structure is converted to a python class structure, there are two concerns:

* if any systemRDL node name is a python keyname
* if any systemRDL node name clashes with part of the peakrdl_standard types, for example all
  register nodes have an ``address`` property that would clash with a field of that register
  called ``address``

consider the following example:

.. code-block:: systemrdl

   addrmap my_addr_map {

       reg {
           default sw = rw;
           default hw = r;
           field { fieldwidth=1; } in;
       } address;
   };

This would create an object attribute ``address`` which would clash with an existing property of
the ``my_addr_map`` object. The register field can not be called ``in`` as this is a python keyword.
Therefore peakrdl python will use the name ``field_in`` in the generated code to avoid the clash.
The algorithm for renaming node to avoid name clashes does not need to be known to an end user,
the names can be looked up.

User Defined Property
---------------------

PeakRDL Python recognises a SystemRDL User Defined Propery (UDP) that can be used to force the
names used in the generated python code for node. In this case following names will be overridden:

* name of the register will be ``overridden_reg_a`` rather than ``reg_a``
* the name of the field will be ``overridden_field_a`` rather than ``field_a``

.. literalinclude :: ../../example/overridden_names/overridden_names.rdl
   :language: systemrdl

Name lookup
-----------

When names have been altered (either to avoid a name clash or by the ``python_inst_name``
User Defined Property), attributes can be accessed using the ``get_child_by_system_rdl_name``
method of any object in the register model. The following example shows both methods to access the
field from the example above

.. literalinclude :: ../../example/overridden_names/demo_over_ridden_names.py
   :language: python

Hidden Elements
===============

Commonly some parts of the register map want to be hidden from some users, for example register
included to reserve space or test functions.

User Defined Property
---------------------

PeakRDL Python supports a User Defined Property (UDP): ``python_hide`` that can be used to hide
items that should not appear in the generated python wrappers.

In the following example, python wrapper generated would have the registers:

* ``explictly_visible_reg``
* ``implicitly_visible_reg``

However the ``hidden_reg`` would not be included in the python wrappers

.. code-block:: systemrdl

   property python_hide { type = boolean; component = addrmap | regfile | reg | field | mem; };

   addrmap my_addr_map {

       reg {
           default sw = rw;
           default hw = r;
           python_hide = true;
           field { fieldwidth=1; } field_a;
       } hidden_reg;

      reg {
           default sw = rw;
           default hw = r;
           python_hide = false;
           field { fieldwidth=1; } field_a;
       } explictly_visible_reg;

      reg {
           default sw = rw;
           default hw = r;
           field { fieldwidth=1; } field_a;
       } implicitly_visible_reg;

   };

The ``python_hide`` property can be overridden with the ``show_hidden`` argument to the peakrdl
command line tool or the ``export`` method.

Regular Expression
------------------

PeakRDL Python supports hiding elements of the based on a regular expression.

.. note:: The expression uses the python re.match, for example to hide all fields, registers,
          regfiles, address maps or memories  with the name ``RSVD``, the regular expression
          must match on the full name e.g. ``(?:[\w_\[\]]+\.)+RSVD``

