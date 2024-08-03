PeakRDL Python
##############

Introduction
============

PeakRDL Python is a python package which can be used to generate a register
access layer python package from a SystemRDL definition.

SystemRDL and control & status register (CSR) generator toolchain
=================================================================

SystemRDL, more accurately `SystemRDL 2.0 <https://www.accellera.org/images/downloads/standards/systemrdl/SystemRDL_2.0_Jan2018.pdf>`_
is a description language that describes the registers in a device, for example an FPGA or
Integrated Circuit (IC). Using this technology allows other parts of the design flow to be
automatically generated, avoiding mistakes with inconsistencies and speeding up the design flow.

The suite of tools needed for this flow are called a control & status register (CSR) generator.

.. note:: This documentation does not attempt to explain all the good reasons for wanted a
          CSR generator, other people have done a far better job.

PeakRDl Python is intended to be part of CSR generator flow.

What is a Register Access Layer (RAL)
=====================================

A Register Access Layer is a software component to make writing scripts and software to control
a device with hardware registers easier.

Hardware Abstraction Layer (HAL) versus Register Access Layer (RAL)
*******************************************************************

.. note:: The Register Access Layer (RAL) is aimed at people who understand the registers in the
           device.

At some point another software component called a Hardware Abstraction Layer (HAL) will often
get produced that abstracts the device function providing functions to do more useful things.
The RAL could be used as part of a HAL.

.. note:: The Hardware Abstraction Layer (HAL) provides abstract functionality and allows
          people to use the device without needing a full knowledge of how it works.

What does it do
***************

The use of a RAL is best shown with an example

Imagine a script to carry out a simple task on a IC, configure an GPIO Pin as an output and
set the state to `1`. The device has 8 GPIO pins controlled from two registers.

+----------+---------+-------------------------------------------------------------------------------------------------------+------------------------+
| Register | Address |                      Bit                                                                              | Function               |
|          |         +------------+------------+------------+------------+------------+------------+------------+------------+                        |
|          |         |  7         |  6         |  5         |  4         |  3         |  2         |  1         |  0         |                        |
+==========+=========+============+============+============+============+============+============+============+============+========================+
| DIR      | 0x100   | GPIO_7_DIR | GPIO_6_DIR | GPIO_5_DIR | GPIO_4_DIR | GPIO_3_DIR | GPIO_2_DIR | GPIO_1_DIR | GPIO_0_DIR | Sets direction of GPIO |
|          |         |            |            |            |            |            |            |            |            |   +-------+---------+  |
|          |         |            |            |            |            |            |            |            |            |   | Value | Meaning |  |
|          |         |            |            |            |            |            |            |            |            |   +=======+=========+  |
|          |         |            |            |            |            |            |            |            |            |   | 0     | In      |  |
|          |         |            |            |            |            |            |            |            |            |   +-------+---------+  |
|          |         |            |            |            |            |            |            |            |            |   | 1     | Out     |  |
|          |         |            |            |            |            |            |            |            |            |   +-------+---------+  |
|          |         |            |            |            |            |            |            |            |            |                        |
+----------+---------+------------+------------+------------+------------+------------+------------+------------+------------+------------------------+
| DATA_OUT | 0x104   | GPIO_7_OUT | GPIO_6_OUT | GPIO_5_OUT | GPIO_4_OUT | GPIO_3_OUT | GPIO_2_OUT | GPIO_1_OUT | GPIO_0_OUT | Sets the state of a    |
|          |         |            |            |            |            |            |            |            |            | GPIO configured as out |
+----------+---------+------------+------------+------------+------------+------------+------------+------------+------------+------------------------+

This example uses the peakrdl python simulator to mimic the behaviour of the device offering ``read`` and ``write``
methods to offer register read and write access to the device. In the real work this would likely go
via a device driver or JTAG emulator, if the software is running off chip (i.e. a PC).

To configure pin 0 and set its state you would need to do the following steps:

1. Read the DIR register (to make sure you preserve the states of other pins)
2. Take the read value of the DIR register, force bit 0 to `1` then write it back
3. Read the DATA_OUT register (to make sure you preserve the states of other pins)
4. Take the read value of the DATA_OUT register, force bit 0 to `1` then write it back

If you had a simple environment that only had register read / write function, the code would be
as follows:

.. literalinclude :: ../example/why_ral/without_ral.py
   :language: python

This code requires addresses to be hard coded, remembering to do read/modify/writes and bit
manipulations

.. warning:: A Register Access Layer (RAL) is not for everyone. Some engineers like to see the
             address of each register and the content of a register as a hex word. You may be quite
             happy with this, if that is you please stop, the overhead of an extra
             layer, its opaque nature and inefficiency will annoy you.

In order to move on the systemRDL code for the registers needs to exist

.. literalinclude :: ../example/why_ral/gpio.rdl
   :language: systemrdl

In order to build the code (assuming you have everything installed), use the following

.. code-block:: bash

   peakrdl python gpio.rdl -o .

Once built, a set of test cases can be run on the code to confirm its integrity, this is using the
``unittest`` framework that comes with python

.. code-block:: bash

   python -m unittest discover -s gpio\tests -t .

Using the RAL allows for much simpler to understand code that does the function that was intended

.. literalinclude :: ../example/why_ral/with_ral.py
   :language: python

The final part of this example shows a Hardware Abstraction Layer (HAL), in this case the GPIO pins
are abstracted to look like an array and the direction is automatically configured when the user
attempts to set the output state.

.. literalinclude :: ../example/why_ral/with_hal.py
   :language: python


.. toctree::
   :hidden:
   :caption: Overview

   self

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: usage

   installation
   generated_package
   api_components
   api
   command_line
   customisation

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: developer notes

   design_decisions
   design_tools

.. toctree::
   :hidden:
   :caption: other

   genindex







