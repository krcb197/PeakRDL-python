from typing import TYPE_CHECKING
import re

from .exporter import PythonExporter


if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode


class Exporter:
    short_desc = "Export the register model to Python Wrappers"

    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        arg_group.add_argument('--autoformat', action='store_true',
                        help='use autopep8 on generated code')

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:

        x = PythonExporter()
        x.export(
            top_node,
            options.output,
            autoformatoutputs=options.autoformat
        )
