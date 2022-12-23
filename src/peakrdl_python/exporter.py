"""
Main Classes for the PeakRDL Python
"""
import os
from pathlib import Path
from shutil import copyfile
from typing import List, NoReturn
from glob import glob

import autopep8 # type: ignore
import jinja2 as jj

from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode # type: ignore
from systemrdl.node import FieldNode, MemNode, AddressableNode # type: ignore
from systemrdl.rdltypes import OnReadType, OnWriteType, PropertyReference # type: ignore

from .systemrdl_node_utility_functions import get_reg_readable_fields, get_reg_writable_fields, \
    get_array_dim, get_table_block, get_dependent_enum, get_dependent_component, \
    get_field_bitmask_hex_string, get_field_inv_bitmask_hex_string, \
    get_field_max_value_hex_string, get_reg_max_value_hex_string, get_fully_qualified_type_name, \
    uses_enum, fully_qualified_enum_type, uses_memory, \
    get_memory_max_entry_value_hex_string, get_array_typecode, get_memory_width_bytes, \
    get_field_default_value

from .safe_name_utility import is_safe_field_name, is_safe_register_name, is_safe_memory_name, \
    is_safe_regfile_name, is_safe_addrmap_name, get_python_path_segments, python_field_name

file_path = os.path.dirname(__file__)

class PythonExportTemplateError(Exception):
    """
    Exception for hading errors in the templating
    """

class PythonExporter:
    """
    PeakRDL Python Exporter class

    Args:
        user_template_dir (str) : Path to a directory where user-defined
            template overrides are stored.
        user_template_context (dict) : Additional context variables to load
            into the template namespace.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):

        user_template_dir = kwargs.pop("user_template_dir", None)
        self.user_template_context = kwargs.pop("user_template_context",
                                                {})
        self.strict = False  # strict RDL rules rather than helpful implicit
                             # behaviour

        # Check for stray kwargs
        if kwargs:
            raise ValueError("got an unexpected keyword argument")

        if user_template_dir:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(user_template_dir),
                jj.FileSystemLoader(os.path.join(file_path, "templates")),
                jj.PrefixLoader({ 'user': jj.FileSystemLoader(user_template_dir),
                                  'base': jj.FileSystemLoader(os.path.join(file_path, "templates"))
                                },
                                delimiter=":")
            ])
        else:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(os.path.join(file_path, "templates")),
                jj.PrefixLoader({'base': jj.FileSystemLoader(os.path.join(file_path,
                                                                          "templates"))},
                                delimiter=":")])

        self.jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined
        )

        # Dictionary of root-level type definitions
        # key = definition type name
        # value = representative object
        #   components, this is the original_def (which can be None in some cases)
        self.namespace_db = {}

        # Dictionary used for determining the unique type names to use
        self.node_type_name = {}

    def export(self, node: Node, path: str,
               autoformatoutputs: bool=True) -> List[str]:
        """
        Generated Python Code and Testbench

        Args:
            node (str) : Top-level node to export. Can be the top-level `RootNode` or any
                  internal `AddrmapNode`.
            path (str) : Output package path.
            autoformatoutputs (bool) : If set to True the code will be run through autopep8 to
                clean it up. This can slow down large jobs or mask problems

        Returns:
            List[str] : modules that have been exported:
        """

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        package_path = os.path.join(path, node.inst_name)
        self._create_empty_package(package_path=package_path)

        modules = [node]

        for block in modules:

            self._build_node_type_table(block)

            context = {
                'print': print,
                'type': type,
                'top_node': block,
                'systemrdlFieldNode': FieldNode,
                'systemrdlRegNode': RegNode,
                'systemrdlRegfileNode': RegfileNode,
                'systemrdlAddrmapNode': AddrmapNode,
                'systemrdlMemNode': MemNode,
                'systemrdlAddressableNode': AddressableNode,
                'OnWriteType': OnWriteType,
                'OnReadType': OnReadType,
                'PropertyReference': PropertyReference,
                'isinstance': isinstance,
                'uses_enum' : uses_enum(block),
                'uses_memory' : uses_memory(block),
                'get_fully_qualified_type_name': self._lookup_type_name,
                'get_array_dim': get_array_dim,
                'get_dependent_component': get_dependent_component,
                'get_dependent_enum': get_dependent_enum,
                'get_fully_qualified_enum_type': fully_qualified_enum_type,
                'get_field_bitmask_hex_string': get_field_bitmask_hex_string,
                'get_field_inv_bitmask_hex_string': get_field_inv_bitmask_hex_string,
                'get_field_max_value_hex_string': get_field_max_value_hex_string,
                'get_reg_max_value_hex_string': get_reg_max_value_hex_string,
                'get_table_block': get_table_block,
                'get_reg_writable_fields': get_reg_writable_fields,
                'get_reg_readable_fields': get_reg_readable_fields,
                'get_memory_max_entry_value_hex_string': get_memory_max_entry_value_hex_string,
                'get_array_typecode': get_array_typecode,
                'get_memory_width_bytes': get_memory_width_bytes,
                'get_field_default_value': get_field_default_value,
                'is_safe_field_name': is_safe_field_name,
                'is_safe_register_name': is_safe_register_name,
                'is_safe_memory_name': is_safe_memory_name,
                'is_safe_regfile_name': is_safe_regfile_name,
                'is_safe_addrmap_name': is_safe_addrmap_name,
                'raise_template_error' : self._raise_template_error,
                'get_python_path_segments' : get_python_path_segments,
                'python_field_name': python_field_name,
            }

            context.update(self.user_template_context)

            template = self.jj_env.get_template("addrmap.py.jinja")
            module_fqfn = os.path.join(package_path,
                                       'reg_model',
                                       block.inst_name + '.py')
            if autoformatoutputs is True:
                module_code_str = autopep8.fix_code(template.render(context))
                with open(module_fqfn, "w", encoding='utf-8') as fid:
                    fid.write(module_code_str)
            else:
                stream = template.stream(context)
                stream.dump(module_fqfn, encoding='utf-8')

            template = self.jj_env.get_template("addrmap_tb.py.jinja")
            module_tb_fqfn = os.path.join(package_path,
                                          'tests',
                                          'test_' + block.inst_name + '.py')
            if autoformatoutputs is True:
                module_tb_code_str = autopep8.fix_code(template.render(context))
                with open(module_tb_fqfn, "w", encoding='utf-8') as fid:
                    fid.write(module_tb_code_str)
            else:
                stream = template.stream(context)
                stream.dump(module_tb_fqfn, encoding='utf-8')

        return [m.inst_name for m in modules]

    def _lookup_type_name(self, node: Node) -> str:
        """
        Retreive the unique type name from the current lookup list

        Args:
            node: node to lookup

        Returns:
            type name

        """

        return self.node_type_name[node.inst]

    def _build_node_type_table(self, node: AddressableNode) -> None:
        """
        Populate the type name lookup dictionary

        Args:
            node: top node to work down from

        Returns:
            None

        """

        self.node_type_name = {}

        for child_node in get_dependent_component(node.parent):

            child_inst = child_node.inst
            if child_inst in self.node_type_name:
                # this should not happen as the get_dependent_component function is supposed to
                # de-duplicate the values
                raise RuntimeError("node is already in the lookup dictionary")

            cand_type_name = get_fully_qualified_type_name(child_node)
            if cand_type_name in self.node_type_name.values():
                self.node_type_name[child_inst] = cand_type_name + '_0x' + hex(hash(child_inst))
            else:
                self.node_type_name[child_inst] = cand_type_name

    @staticmethod
    def _create_empty_package(package_path:str) -> None:
        """
        create the directories and __init__.py files associated with the exported package

        Args:
            package_path: directory for the package output

        Returns:
            None

        """

        Path(package_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'reg_model')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'tests')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'lib')).mkdir(parents=True, exist_ok=True)

        module_fqfn = os.path.join(package_path, 'reg_model', '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')
        module_fqfn = os.path.join(package_path, 'tests', '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')
        module_fqfn = os.path.join(package_path, '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')

        template_package = os.path.join(os.path.dirname(__file__),
                                        'templates',
                                        'peakrdl_python')
        files_in_package = glob(os.path.join(template_package,'*.py'))

        for file_in_package in files_in_package:
            filename = os.path.basename(file_in_package)
            copyfile(src=os.path.join(template_package,
                                      filename),
                     dst=os.path.join(package_path,
                                      'lib',
                                      filename))

    def _raise_template_error(self, message: str) -> NoReturn:
        """
        Helper function to raise an exception from within the templating

        Args:
            message: message to put in the exception

        Raises: PythonExportTemplateError

        """
        raise PythonExportTemplateError(message)
