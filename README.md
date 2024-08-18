![CI](https://github.com/krcb197/PeakRDL-python/actions/workflows/action.yaml/badge.svg)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peakrdl-python.svg)](https://pypi.org/project/peakrdl-python)
[![Documentation Status](https://readthedocs.org/projects/peakrdl-python/badge/?version=latest)](https://peakrdl-python.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://static.pepy.tech/badge/peakrdl-python)](https://pepy.tech/project/peakrdl-python)

# peakrdl-python
Generate Python Register Access Layer (RAL) from SystemRDL

## Documentation
See the [peakrdl-python Documentation](https://peakrdl-python.readthedocs.io/) for more details

## Upgrading from pre 0.9.0

In order to address a major limitation of peakrdl-python that prevented it from implementing the
full systemRDL specification, a breaking API change was needed for handling blocks:
* registers (in register array)
* memory entries in a memory

Users are encouraged to upgrade in order to avoid this limitation. However, there is a legacy mode
to support users with existing designs, see: _Legacy Block Callback and Block Access_ in the 
documentation


