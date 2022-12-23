import warnings

# Load modules
from peakrdl_python import __about__
from peakrdl_python import exporter

# hoist internal objects
from peakrdl_python.__about__ import __version__
from peakrdl_python.exporter import PythonExporter


warnings.warn(
"""
================================================================================
Importing via namespace package 'peakrdl.python' is deprecated and will be
removed in the next release.
Change your imports to load the package using 'peakrdl_python' instead.
For more details, see: https://github.com/SystemRDL/PeakRDL/issues/4
================================================================================
""", DeprecationWarning, stacklevel=2)
