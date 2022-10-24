"""
Module for integrating with PeakRDL. This module is not intended to be used directly
refer to the PeakRDL documentation
"""
from typing import TYPE_CHECKING

from .exporter import PythonExporter

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode  # type: ignore


class Exporter:
    """
    PeakRDL export class, see PeakRDL for more details
    """
    short_desc = "Export the register model to Python Wrappers"

    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        """
        Added the arguments to the PeakRDL arguments

        Args:
            arg_group: from PeakRDL

        Returns:

        """
        arg_group.add_argument('--autoformat', action='store_true',
                        help='use autopep8 on generated code')

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        """
        Perform the export operation

        Args:
            top_node: Top Node from the systemRDL compile
            options: Command line arguments for PeakRDL-Python

        Returns:

        """

        peakrdl_exporter = PythonExporter()
        peakrdl_exporter.export(
            top_node,
            options.output,
            autoformatoutputs=options.autoformat
        )
