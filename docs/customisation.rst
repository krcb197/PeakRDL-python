Customisation
*************

Alternative Headers
===================

By default the header at the top of the generated code will look as follows:

.. code-block:: python

   """
   Python Wrapper for the basic register model

   This code was generated from the PeakRDL-python package version 0.3.8

   """

This can be customised by generating a new Jinja template that replaces the one that is part
of PeakRDL Python.

For example create a file called ``header.py.jinja`` as follows:

.. code-block:: jinja

   """
   Python Wrapper for the {{top_node.inst_name}} register model

   This code was generated from the PeakRDL-python package version {{version}}

   Copyright MyCompany 2023
   """

Refer to the documentation for Jinja for more details on the syntax

This can be stored in a folder, for example one called: ``my_company_headers``

The path to the folder of alternative templates must be ``PythonExporter`` is initialised

.. code-block:: python

    from systemrdl import RDLCompiler
    from peakrdl_python.exporter import PythonExporter

    # compile the systemRDL
    rdlc = RDLCompiler()
    rdlc.compile_file('basic.rdl')
    spec = rdlc.elaborate(top_def_name='basic').top

    # generate the python package register access layer
    exporter = PythonExporter(user_template_dir='my_company_headers')
    exporter.export(node=spec, path='generated_code')

alternatively it can be generated from the PeakRDL, this requires the PeakRDL TOML config options
to be setup, see `Configuring PeakRDL <https://peakrdl.readthedocs.io/en/latest/configuring.html>`_

.. code-block::

    [python]
    user_template_dir = "path/to/dir/"

command line as follows:

.. code-block:: bash

   peakrdl python basic.rdl -o .

