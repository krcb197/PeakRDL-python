Design Decisions
****************

A collection of notes to explain some of the design decisions to potential developers and
advanced users

'Pure' Python
=============

The peakrdl-python RAL was designed to have very limited dependencies on other packages once
deployed, this includes the peakrdl-python packages itself, so the library classes are copied
into the generated package.

It does need a few packages inorder to build it:

* systemrdl-compiler
* jinja2

Integer Data Types
===================

All the APIs present memory, register and field entries as python integers. This abstracts, the
complexity of byte ordering and reversed registers.

Blocks of Data
==============

.. versionchanged:: 0.9.0

    blocks of data (for example memories were accessed as python array.array previously. This
    did not support width of larger than 128 bits therefore this was changed to list.