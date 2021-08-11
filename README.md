
# PeakRDL-python
Generate Python wrapper for a register model compiled SystemRDL input

## Installing
Install from github only at the moment.

--------------------------------------------------------------------------------

## Exporter Usage
Pass the elaborated output of the [SystemRDL Compiler](http://systemrdl-compiler.readthedocs.io)
to the exporter.

```python
import sys
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl.python.exporter import PythonExporter

rdlc = RDLCompiler()

try:
    rdlc.compile_file("path/to/my.rdl")
    root = rdlc.elaborate()
except RDLCompileError:
    sys.exit(1)

exporter = PythonExporter()
exporter.export(root, "path/to/output")
```
The exporter will create a python package in the specified output directory
consists of the python wrapper and a test bench for the wrapper which can be 
run within a unittest framework.

--------------------------------------------------------------------------------

## Reference

### `PythonExporter(**kwargs)`
Constructor for the Python Exporter class

**Optional Parameters**

* `user_template_dir`
    * Path to a directory where user-defined template overrides are stored.
* `user_template_context`
    * Additional context variables to load into the template namespace.

### `PythonExporter.export(node, path, **kwargs)`
Perform the export!

**Parameters**

* `node`
    * Top-level node to export. Can be the top-level `RootNode` or any internal `AddrmapNode`.
* `path`
    * Output directory.
* `autoformatoutputs`
    * True - All the generated code is run through autopep8 (warning this can be slow for large designs)


