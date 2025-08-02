![CI](https://github.com/krcb197/PeakRDL-python/actions/workflows/action.yaml/badge.svg)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peakrdl-python.svg)](https://pypi.org/project/peakrdl-python)
[![Documentation Status](https://readthedocs.org/projects/peakrdl-python/badge/?version=latest)](https://peakrdl-python.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://static.pepy.tech/badge/peakrdl-python)](https://pepy.tech/project/peakrdl-python)

# Introduction
PeakRDL Python is used to generate a python based Register Access Layer (RAL) from SystemRDL.

## Documentation
See the [peakrdl-python Documentation](https://peakrdl-python.readthedocs.io/) for more details

## Getting Started

### Installation

1. Install a recent version of Python 3
2. Install `peakrdl-python`
   ```console
   python3 -m pip install peakrdl-python
   ```
3. (Optional) Install `peakrdl`, this is needed if you want to use peakrdl python from the command
   line
   ```console
   python3 -m pip install peakrdl
   ```
   
### First Demo

This demonstration relies on downloading the systemRDL example from Accelera, available here: [accelera-generic_example.rdl](https://github.com/SystemRDL/systemrdl-compiler/blob/main/examples/accelera-generic_example.rdl). This demonstration also 
assumes that peakrdl has been installed.

1. Build the Register Access Layer (RAL) from the systemRDL code
   ```console
   peakrdl python accelera-generic_example.rdl -o .
   ```
   This will create a python package called `some_register_map` containing the python RAL
2. In addition to the RAL, peakrdl-python also generates a simulator that can be used to exercise 
   the RAL without connecting to real hardware. Enter the following code into a file:
   ```python
   """
   An demonstration of using peakrdl-python using the accelera generic example
   """
   # import the top level RAL class
   from some_register_map.reg_model.some_register_map import some_register_map_cls
   # import the simulator class
   from some_register_map.sim.some_register_map import some_register_map_simulator_cls
   
   from some_register_map.lib import NormalCallbackSet
   
   if __name__ == '__main__':
       # create an instance of the RAL with the callbacks directed at the hardware simulator
       hw_sim = some_register_map_simulator_cls(0)
       ral = some_register_map_cls(callbacks=NormalCallbackSet(read_callback=hw_sim.read,
                                                               write_callback=hw_sim.write))
   
       # read chip ID
       chip_id_part_number = ral.chip_id_reg.part_num.read()
       chip_id_revision_number = ral.chip_id_reg.part_num.read()
       print(f'Chip ID:{chip_id_part_number}.{chip_id_revision_number}')
   ```
   save it as `some_register_map_demo.py`
3. Run the example
   ```commandline
   python3 -m some_register_map_demo
   ```
   This will generate the following output on the console:
   ```commandline
   Chip ID:0.0
   ```
   
# Usage

To make use of the RAL with real hardware or a different simulation, the callbacks will need to be 
connected to the appropriate access function with perform a address space reads and writes 

## Upgrading from previous versions (some important changes)

### Upgrading from pre 0.9.0

In order to address a major limitation of peakrdl-python that prevented it from implementing the
full systemRDL specification, a breaking API change was needed for handling blocks:
* registers (in register array)
* memory entries in a memory

Users are encouraged to upgrade in order to avoid this limitation. However, there is a legacy mode
to support users with existing designs, see: _Legacy Block Callback and Block Access_ in the 
documentation

### Upgrading from pre 1.2.0

Version 1.2 introduced a new way to define the enumerations for the field encoding. This allows 
metadata from the systemRDL to propagate through to the generated code. This may break advanced 
usage of the python enumerations. User are encouraged to use the new feature, however, if there 
are problems with the old enumeration types (based on `IntEnum`) can be used, see 
_Legacy Enumeration Types_ in the documentation

### Upgrading from pre 2.0.0

Version 2.0 introduced a significant change to the process for building the register model python
code. This change was intended to reduce the size of the generated code by only generating 
python classes for systemRDL components that required unique classes. The previous versions were 
more conservative and tended to generate a lot of duplicate classes. 


