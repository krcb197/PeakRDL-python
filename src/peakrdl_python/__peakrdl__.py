"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of 
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Module for integrating with peakrdl. This module is not intended to be used directly
refer to the peakrdl documentation
"""
from typing import TYPE_CHECKING

# depending on whether peakrdl is installed or not you get a slightly different pylint error
# from the following line, therefore two errors have to be suppressed
#pylint: disable=no-name-in-module,import-error
from peakrdl.plugins.exporter import ExporterSubcommandPlugin  # type: ignore[import]
from peakrdl.config import schema  # type: ignore[import]
#pylint: enable=no-name-in-module,import-error

from .exporter import PythonExporter
from .exporter import DEFAULT_REGISTER_CLASS_PER_GENERATED_FILE
from .exporter import DEFAULT_FIELD_CLASS_PER_GENERATED_FILE
from .exporter import DEFAULT_ENUM_FIELD_CLASS_PER_GENERATED_FILE
from .exporter import DEFAULT_MEMORY_CLASS_PER_GENERATED_FILE
from .compiler_udp import PythonHideUDP, PythonInstNameUDP

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode


class Exporter(ExporterSubcommandPlugin):
    """
    PeakRDL export class, see PeakRDL for more details
    """
    short_desc = "Generate Python Wrappers"
    long_desc = "Generate Python Wrappers for the Register Model"
    udp_definitions = [PythonHideUDP, PythonInstNameUDP]
    generates_output_file = True

    cfg_schema = {
        "user_template_dir": schema.DirectoryPath(),
        "user_template_context": { "*" : schema.AnyType() }
    }

    def add_exporter_arguments(self, arg_group: 'argparse._ActionsContainer') -> None:
        """
        Added the arguments to the PeakRDL arguments

        Args:
            arg_group: from PeakRDL

        Returns:

        """
        arg_group.add_argument('--async', action='store_true', dest='is_async',
                               help='define accesses to register model as asynchronous')
        arg_group.add_argument('--skip_test_case_generation', action='store_true',
                               help='skip the generation of the test cases')
        arg_group.add_argument('--suppress_cleanup', action='store_true', dest='suppress_cleanup',
                               help='by default peakrdl_python deletes all existing python .py '
                                    'files found in the directory where the package will be'
                                    ' generated. This is normally useful if the user is '
                                    'generating over the top of an existing package and prevents '
                                    'problems when the structure of the register map changes. '
                                    'However, if additional python files are added by the user '
                                    '(not recommended) this cleanup will need to be suppressed '
                                    'and managed by the user')
        arg_group.add_argument('--legacy_block_access', action='store_true',
                               dest='legacy_block_access',
                               help='peakrdl python has two methods to hold blocks of data, the '
                                    'legacy mode based on array.array or the new mode using lists')
        arg_group.add_argument('--show_hidden', action='store_true',
                               dest='show_hidden',
                               help='show addrmap, regfile, memory, register and fields that '
                                    'have been given the python_hide user defined property and '
                                    'would be removed from the build python by default')
        udp_group = arg_group.add_mutually_exclusive_group(required=False)
        udp_group.add_argument('--udp', dest='udp', nargs='*', type=str,
                               help='any user defined properties to include in the reg_model')
        udp_group.add_argument('--udp_regex', dest='udp_regex', type=str,
                               help='a regex to define which UPD ares show in the reg model')
        arg_group.add_argument('--hide_regex', dest='hide_regex', type=str,
                               help='A regex that will cause any matching fully qualified node to '
                                    'be hidden')
        arg_group.add_argument('--skip_library_copy', action='store_true',
                               help='skip the copy of the library code into the generated package')
        arg_group.add_argument('--legacy_enum_type', action='store_true',
                               dest='legacy_enum_type',
                               help='peakrdl python has two ways to define field encoding as '
                                     'enums new method and an old method based on IntEnum. '
                                     'Setting this to true will restore the old behaviour')
        arg_group.add_argument('--skip_systemrdl_name_and_desc_properties', action='store_true',
                               dest='skip_systemrdl_name_and_desc_properties',
                               help='peakrdl python includes the system RDL name and desc '
                                    'attributes as properties of the class that is built. Setting '
                                    'this will skip this reducing the size of the python code '
                                    'generated')
        arg_group.add_argument('--skip_systemrdl_name_and_desc_in_docstring', action='store_true',
                               dest='skip_systemrdl_name_and_desc_in_docstring',
                               help='peakrdl python includes the system RDL name and desc '
                                    'attributes within the doc string of the built code. Setting '
                                    'this will skip this reducing the size of the python code '
                                    'generated')
        arg_group.add_argument('--register_class_per_generated_file',
                               dest='register_class_per_generated_file',
                               type=int,
                               default=DEFAULT_REGISTER_CLASS_PER_GENERATED_FILE,
                               help='Number of register class definitions to put in each python '
                                    'module of the generated code. Make sure this is set to '
                                    'ensure the file does not get too big otherwise the '
                                    'generation and loading is slow')
        arg_group.add_argument('--field_class_per_generated_file',
                               dest='field_class_per_generated_file',
                               type=int,
                               default=DEFAULT_FIELD_CLASS_PER_GENERATED_FILE,
                               help='Number of field class definitions to put in each python '
                                    'module of the generated code. Make sure this is set to '
                                    'ensure the file does not get too big otherwise the '
                                    'generation and loading is slow')
        arg_group.add_argument('--enum_field_class_per_generated_file',
                               dest='enum_field_class_per_generated_file',
                               type=int,
                               default=DEFAULT_ENUM_FIELD_CLASS_PER_GENERATED_FILE,
                               help='Number of enumerated field class definitions to put in each '
                                    'python module of the generated code. Make sure this is set '
                                    'to ensure the file does not get too big otherwise the '
                                    'generation and loading is slow')
        arg_group.add_argument('--memory_class_per_generated_file',
                               dest='memory_class_per_generated_file',
                               type=int,
                               default=DEFAULT_MEMORY_CLASS_PER_GENERATED_FILE,
                               help='Number of memory class definitions to put in each '
                                    'python module of the generated code. Make sure this is set '
                                    'to ensure the file does not get too big otherwise the '
                                    'generation and loading is slow')

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        """
        Perform the export operation

        Args:
            top_node: Top Node from the systemRDL compile
            options: Command line arguments for PeakRDL-Python

        Returns:

        """
        templates = self.cfg['user_template_dir']
        user_template_context = self.cfg['user_template_context']
        if user_template_context is None:
            peakrdl_exporter = \
                PythonExporter(user_template_dir=templates)  # type: ignore[no-untyped-call]
        else:
            peakrdl_exporter = \
                PythonExporter(user_template_dir=templates, # type: ignore[no-untyped-call]
                               user_template_context=user_template_context)

        peakrdl_exporter.export(
            node=top_node,
            path=options.output,
            asyncoutput=options.is_async,
            skip_test_case_generation=options.skip_test_case_generation,
            delete_existing_package_content=not options.suppress_cleanup,
            legacy_block_access=options.legacy_block_access,
            show_hidden=options.show_hidden,
            user_defined_properties_to_include=options.udp,
            user_defined_properties_to_include_regex=options.udp_regex,
            hidden_inst_name_regex=options.hide_regex,
            skip_library_copy=options.skip_library_copy,
            legacy_enum_type=options.legacy_enum_type,
            skip_systemrdl_name_and_desc_properties=
                options.skip_systemrdl_name_and_desc_properties,
            skip_systemrdl_name_and_desc_in_docstring=
                options.skip_systemrdl_name_and_desc_in_docstring,
            register_class_per_generated_file=options.register_class_per_generated_file,
            field_class_per_generated_file=options.field_class_per_generated_file,
            enum_field_class_per_generated_file=options.enum_field_class_per_generated_file,
            memory_class_per_generated_file=options.memory_class_per_generated_file
        )
