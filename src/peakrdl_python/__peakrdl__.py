"""
Module for integrating with PeakRDL. This module is not intended to be used directly
refer to the PeakRDL documentation
"""
from typing import TYPE_CHECKING
import pathlib

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
        arg_group.add_argument('--user_template_dir', action='store', type=pathlib.Path,
                               help='directory of user templates to override the default ones')
        arg_group.add_argument('--skip_test_case_generation', action='store_true',
                            help='skip the generation of the test cases')

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        """
        Perform the export operation

        Args:
            top_node: Top Node from the systemRDL compile
            options: Command line arguments for PeakRDL-Python

        Returns:

        """
        if options.user_template_dir is None:
            peakrdl_exporter = PythonExporter()
        else:
            peakrdl_exporter = PythonExporter(user_template_dir=options.user_template_dir)

        peakrdl_exporter.export(
            top_node,
            options.output,
            autoformatoutputs=options.autoformat,
            skip_test_case_generation=options.skip_test_case_generation
        )
