Command Line Interface
**********************

PeakRDL Python can either be run from within another Python script or using the
command line program.

.. code-block:: bash

    peakpython basic.rdl --outdir peakpython_output --lint --test


Detailed Arguments
==================

.. argparse::
   :module: peakrdl.python.peakpython
   :func: build_command_line_parser
   :prog: peakpython