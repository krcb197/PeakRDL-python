"""
Main Classes for the PeakRDL Python
"""
import os
from pathlib import Path
from shutil import copyfile
from typing import List, NoReturn, Iterable, Tuple
from glob import glob

import jinja2 as jj
from systemrdl import RDLWalker # type: ignore

from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode # type: ignore
from systemrdl.node import FieldNode, MemNode, AddressableNode # type: ignore
from systemrdl.node import SignalNode # type: ignore
from systemrdl.rdltypes import OnReadType, OnWriteType, PropertyReference  # type: ignore
from systemrdl.rdltypes.user_enum import UserEnumMeta  # type: ignore

from .systemrdl_node_utility_functions import get_reg_readable_fields, get_reg_writable_fields, \
    get_table_block, get_dependent_component, \
    get_field_bitmask_hex_string, get_field_inv_bitmask_hex_string, \
    get_field_max_value_hex_string, get_reg_max_value_hex_string, get_fully_qualified_type_name, \
    uses_enum, uses_memory, \
    get_memory_max_entry_value_hex_string, get_memory_width_bytes, \
    get_field_default_value, get_enum_values

from .lib import get_array_typecode

from .safe_name_utility import get_python_path_segments, safe_node_name

from ._node_walkers import AddressMaps, OwnedbyAddressMap

from .__about__ import __version__

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

    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]

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
               asyncoutput: bool=False,
               skip_test_case_generation: bool=False) -> List[str]:
        """
        Generated Python Code and Testbench

        Args:
            node (str) : Top-level node to export. Can be the top-level `RootNode` or any
                  internal `AddrmapNode`.
            path (str) : Output package path.
            asyncoutput (bool) : If set this builds a register model with async callbacks
            skip_test_case_generation (bool): skip generation the generation of the test cases

        Returns:
            List[str] : modules that have been exported:
        """
        # pylint: disable=too-many-locals

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            top_block = node.top
        else:
            top_block = node

        package_path = os.path.join(path, node.inst_name)
        self._create_empty_package(package_path=package_path,
                                   skip_test_case_generation=skip_test_case_generation)

        self._build_node_type_table(top_block)

        context = {
            'print': print,
            'type': type,
            'top_node': top_block,
            'systemrdlFieldNode': FieldNode,
            'systemrdlRegNode': RegNode,
            'systemrdlRegfileNode': RegfileNode,
            'systemrdlAddrmapNode': AddrmapNode,
            'systemrdlMemNode': MemNode,
            'systemrdlAddressableNode': AddressableNode,
            'systemrdlSignalNode': SignalNode,
            'asyncoutput': asyncoutput,
            'OnWriteType': OnWriteType,
            'OnReadType': OnReadType,
            'PropertyReference': PropertyReference,
            'isinstance': isinstance,
            'uses_enum' : uses_enum(top_block),
            'uses_memory' : uses_memory(top_block),
            'get_fully_qualified_type_name': self._lookup_type_name,
            'get_dependent_component': get_dependent_component,
            'get_dependent_enum': self._get_dependent_enum,
            'get_enum_values': get_enum_values,
            'get_fully_qualified_enum_type': self._fully_qualified_enum_type,
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
            'raise_template_error' : self._raise_template_error,
            'get_python_path_segments' : get_python_path_segments,
            'safe_node_name' : safe_node_name,
            'version' : __version__
        }

        context.update(self.user_template_context)

        template = self.jj_env.get_template("addrmap.py.jinja")
        module_fqfn = os.path.join(package_path,
                                   'reg_model',
                                   top_block.inst_name + '.py')

        stream = template.stream(context)
        stream.dump(module_fqfn, encoding='utf-8')

        if not skip_test_case_generation:

            # make the top level base class for all the other test, this is what instantes
            # the register model
            template = self.jj_env.get_template("baseclass_tb.py.jinja")
            module_tb_fqfn = os.path.join(package_path,
                                          'tests',
                                          '_' + top_block.inst_name + '_test_base.py')

            context = {
                'top_node': top_block,
                'asyncoutput': asyncoutput,
                'version': __version__
            }


            stream = template.stream(context)
            stream.dump(module_tb_fqfn, encoding='utf-8')

            # make the tests themselves
            template = self.jj_env.get_template("addrmap_tb.py.jinja")

            blocks = AddressMaps()
            # running the walker populated the blocks with all the address maps in within the
            # top block, including the top_block itself
            RDLWalker(unroll=True).walk(top_block, blocks, skip_top=False)

            for block in blocks:
                owned_elements = OwnedbyAddressMap()
                # running the walker populated the blocks with all the address maps in within the
                # top block, including the top_block itself
                RDLWalker(unroll=True).walk(block, owned_elements, skip_top=True)

                fq_block_name = '_'.join(block.get_path_segments(array_suffix = '_{index:d}_'))

                module_tb_fqfn = os.path.join(package_path,
                                              'tests',
                                              'test_' + fq_block_name + '.py')

                context = {
                    'top_node': top_block,
                    'block' : block,
                    'fq_block_name' : fq_block_name,
                    'owned_elements': owned_elements,
                    'systemrdlFieldNode': FieldNode,
                    'systemrdlSignalNode': SignalNode,
                    'systemrdlRegNode': RegNode,
                    'systemrdlMemNode': MemNode,
                    'systemrdlRegfileNode': RegfileNode,
                    'systemrdlAddrmapNode': AddrmapNode,
                    'isinstance': isinstance,
                    'get_python_path_segments': get_python_path_segments,
                    'safe_node_name': safe_node_name,
                    'uses_memory': (len(owned_elements.memories) > 0),
                    'get_field_bitmask_hex_string': get_field_bitmask_hex_string,
                    'get_field_inv_bitmask_hex_string': get_field_inv_bitmask_hex_string,
                    'get_field_max_value_hex_string': get_field_max_value_hex_string,
                    'get_field_default_value': get_field_default_value,
                    'get_reg_max_value_hex_string': get_reg_max_value_hex_string,
                    'get_reg_writable_fields': get_reg_writable_fields,
                    'get_reg_readable_fields': get_reg_readable_fields,
                    'get_memory_max_entry_value_hex_string': get_memory_max_entry_value_hex_string,
                    'get_enum_values': get_enum_values,
                    'get_array_typecode': get_array_typecode,
                    'get_memory_width_bytes': get_memory_width_bytes,
                    'asyncoutput': asyncoutput,
                    'uses_enum': uses_enum(block),
                    'version': __version__
                }

                stream = template.stream(context)
                stream.dump(module_tb_fqfn, encoding='utf-8')

        return top_block.inst_name

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
    def _create_empty_package(package_path:str,
                              skip_test_case_generation: bool) -> None:
        """
        create the directories and __init__.py files associated with the exported package

        Args:
            package_path: directory for the package output
            skip_test_case_generation: skip the generation of the test folders

        Returns:
            None

        """

        Path(package_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'reg_model')).mkdir(parents=True, exist_ok=True)
        if not skip_test_case_generation:
            Path(os.path.join(package_path, 'tests')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'lib')).mkdir(parents=True, exist_ok=True)

        module_fqfn = os.path.join(package_path, 'reg_model', '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')
        if not skip_test_case_generation:
            module_fqfn = os.path.join(package_path, 'tests', '__init__.py')
            with open(module_fqfn, 'w', encoding='utf-8') as fid:
                fid.write('pass\n')
        module_fqfn = os.path.join(package_path, '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')

        template_package = os.path.join(os.path.dirname(__file__),
                                        'lib')
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

    def _fully_qualified_enum_type(self,
                                   field_enum: UserEnumMeta,
                                   root_node: AddressableNode,
                                   owning_field: FieldNode) -> str:
        """
        Returns the fully qualified class type name, for an enum
        """
        if not hasattr(field_enum, '_parent_scope'):
            # this happens if the enum is has been declared in an IPXACT file
            # which is imported
            return self._lookup_type_name(owning_field) + '_' + field_enum.__name__

        parent_scope = getattr(field_enum, '_parent_scope')

        if parent_scope is None:
            # this happens if the enum is has been declared in an IPXACT file
            # which is imported
            return self._lookup_type_name(owning_field) + '_' + field_enum.__name__

        if root_node.inst.original_def == parent_scope:
            return field_enum.__name__

        dependent_components = get_dependent_component(root_node)

        for component in dependent_components:
            if component.inst.original_def == parent_scope:
                return get_fully_qualified_type_name(component) + '_' + field_enum.__name__

        raise RuntimeError('Failed to find parent node to reference')

    def _get_dependent_enum(self, node: AddressableNode) -> \
            Iterable[Tuple[UserEnumMeta, FieldNode]]:
        """
        iterable of enums which is used by a descendant of the input node,
        this list is de-duplicated

        :param node: node to analysis
        :return: nodes that are dependent on the specified node
        """
        enum_needed = []
        for child_node in node.descendants():
            if isinstance(child_node, FieldNode):
                if 'encode' in child_node.list_properties():
                    # found an field with an enumeration

                    field_enum = child_node.get_property('encode')
                    fully_qualified_enum_name = self._fully_qualified_enum_type(field_enum,
                                                                                node,
                                                                                child_node)

                    if fully_qualified_enum_name not in enum_needed:
                        enum_needed.append(fully_qualified_enum_name)
                        yield field_enum, child_node
