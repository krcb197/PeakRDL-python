"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Main Classes for the peakrdl-python
"""
import os
from pathlib import Path
from shutil import copy
from typing import List, NoReturn, Iterable, Tuple, Dict, Any

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

class _PythonPackage:
    """
    Class to represent a python package
    """
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        """
        path of the package
        """
        return self._path

    def child_package(self, name: str) -> '_PythonPackage':
        """
        provide a child package within the current package

        Args:
            name: name of child package

        Returns:
            None

        """
        return _PythonPackage(path=self.path / name)

    def child_module_path(self, name: str) -> Path:
        """
        return a child module within the package

        Args:
            name: name of module

        Returns:
            None

        """
        return Path(self.path) / name

    @property
    def _init_path(self) -> Path:
        return self.child_module_path('__init__.py')

    def _make_empty_init_file(self) -> None:
        with self._init_path.open('w', encoding='utf-8') as fid:
            fid.write('pass\n')

    def create_empty_package(self, cleanup: bool) -> None:
        """
        make the package folder (if it does not already exist), populate the __init__.py and
        optionally remove any existing python files

        Args:
            cleanup (bool) : delete any existing python files in the package

        Returns:
            None
        """
        if self.path.exists():
            if cleanup:
                for file in self.path.glob('*.py'):
                    os.remove(file.resolve())
        else:
            self.path.mkdir(parents=True, exist_ok=False)
        self._make_empty_init_file()


class _CopiedPythonPackage(_PythonPackage):
    """
    Class to represent a python package, which is copied from another
    """
    def __init__(self, path: Path, ref_package: _PythonPackage):
        super().__init__(path=path)
        self._ref_package = ref_package

    def create_empty_package(self, cleanup: bool) -> None:
        """
        make the package folder (if it does not already exist), populate the __init__.py and
        optionally remove any existing python files

        Args:
            cleanup (bool) : delete any existing python files in the package

        Returns:
            None
        """
        super().create_empty_package(cleanup=cleanup)

        # copy all the python source code that is part of the library which comes as part of the
        # peakrdl-python to the lib direction of the generated package
        files_in_package = self._ref_package.path.glob('*.py')

        for file_in_package in files_in_package:
            copy(src=file_in_package, dst=self.path)


class _Package(_PythonPackage):
    """
    Class to define the package being generated

    Args:
        include_tests (bool): include the tests package
    """
    template_lib_package = _PythonPackage(Path(__file__).parent / 'lib')
    template_sim_lib_package = _PythonPackage(Path(__file__).parent / 'sim_lib')

    def __init__(self, path:str, package_name: str, include_tests: bool, include_libraries: bool):
        super().__init__(Path(path) / package_name)

        self._include_tests = include_tests
        self._include_libraries = include_libraries

        if include_libraries:
            self.lib = self.child_ref_package('lib', self.template_lib_package)
        self.reg_model = self.child_package('reg_model')

        if include_tests:
            self.tests = self.child_package('tests')

        if include_libraries:
            self.sim_lib = self.child_ref_package('sim_lib', self.template_sim_lib_package)
        self.sim = self.child_package('sim')

    def child_ref_package(self, name: str, ref_package:_PythonPackage) -> '_CopiedPythonPackage':
        """
        provide a child package within the current package

        Args:
            name: name of child package

        Returns:
            None

        """
        return _CopiedPythonPackage(path=self.path / name, ref_package=ref_package)


    def create_empty_package(self, cleanup: bool, ) -> None:
        """
        create the directories and __init__.py files associated with the exported package

        Args:
            package_path: directory for the package output
            cleanup (bool): delete existing python files

        Returns:
            None

        """

        # make the folder for this package and populate the empty __init__.py
        super().create_empty_package(cleanup=cleanup)
        # make all the child packages folders and their __init__.py
        self.reg_model.create_empty_package(cleanup=cleanup)
        if self._include_tests:
            self.tests.create_empty_package(cleanup=cleanup)
        if self._include_libraries:
            self.lib.create_empty_package(cleanup=cleanup)
            self.sim_lib.create_empty_package(cleanup=cleanup)
        self.sim.create_empty_package(cleanup=cleanup)


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

    def __stream_jinja_template(self,
                                template_name: str,
                                target_package: _PythonPackage,
                                target_name: str,
                                template_context: Dict[str, Any]) -> None:

        template = self.jj_env.get_template(template_name)
        module_path = target_package.child_module_path(target_name)

        with module_path.open('w', encoding='utf-8') as fp:
            stream = template.stream(template_context)
            stream.dump(fp)

    def __export_reg_model(self,
                           top_block: AddrmapNode,
                           package: _Package,
                           skip_lib_copy: bool,
                           asyncoutput: bool,
                           legacy_block_access: bool) -> None:

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
            'get_memory_width_bytes': get_memory_width_bytes,
            'get_field_default_value': get_field_default_value,
            'raise_template_error' : self._raise_template_error,
            'get_python_path_segments' : get_python_path_segments,
            'safe_node_name' : safe_node_name,
            'skip_lib_copy': skip_lib_copy,
            'version' : __version__,
            'legacy_block_access' : legacy_block_access,
        }
        if legacy_block_access is True:
            context['get_array_typecode'] = get_array_typecode

        context.update(self.user_template_context)

        self.__stream_jinja_template(template_name="addrmap.py.jinja",
                                     target_package=package.reg_model,
                                     target_name=top_block.inst_name + '.py',
                                     template_context=context)

    def __export_simulator(self,
                           top_block: AddrmapNode,
                           package: _Package,
                           skip_lib_copy: bool,
                           asyncoutput: bool,
                           legacy_block_access: bool) -> None:

        context = {
            'top_node': top_block,
            'systemrdlRegNode': RegNode,
            'systemrdlMemNode': MemNode,
            'isinstance': isinstance,
            'asyncoutput': asyncoutput,
            'skip_lib_copy': skip_lib_copy,
            'version': __version__,
            'legacy_block_access' : legacy_block_access,
            }

        context.update(self.user_template_context)

        self.__stream_jinja_template(template_name="sim_addrmap.py.jinja",
                                     target_package=package.sim,
                                     target_name=top_block.inst_name + '.py',
                                     template_context=context)

    def __export_example(self,
                         top_block: AddrmapNode,
                         package: _Package,
                         skip_lib_copy: bool,
                         asyncoutput: bool,
                         legacy_block_access: bool) -> None:

        context = {
            'top_node': top_block,
            'systemrdlRegNode': RegNode,
            'systemrdlMemNode': MemNode,
            'isinstance': isinstance,
            'asyncoutput': asyncoutput,
            'skip_lib_copy': skip_lib_copy,
            'version': __version__,
            'legacy_block_access' : legacy_block_access,
            }

        context.update(self.user_template_context)

        self.__stream_jinja_template(template_name="example.py.jinja",
                                     target_package=package,
                                     target_name='example.py',
                                     template_context=context)

    def __export_base_tests(self,
                            top_block: AddrmapNode,
                            package: _Package,
                            skip_lib_copy: bool,
                            asyncoutput: bool,
                            legacy_block_access: bool) -> None:
        """

        Args:
            top_block:
            package:
            asyncoutput:

        Returns:

        """

        context = {
            'top_node': top_block,
            'asyncoutput': asyncoutput,
            'skip_lib_copy': skip_lib_copy,
            'version': __version__,
            'legacy_block_access' : legacy_block_access,
        }

        context.update(self.user_template_context)

        self.__stream_jinja_template(template_name="baseclass_tb.py.jinja",
                                     target_package=package.tests,
                                     target_name='_' + top_block.inst_name + '_test_base.py',
                                     template_context=context)

        self.__stream_jinja_template(template_name="baseclass_simulation_tb.py.jinja",
                                     target_package=package.tests,
                                     target_name='_' + top_block.inst_name + '_sim_test_base.py',
                                     template_context=context)

    def __export_tests(self,
                       top_block: AddrmapNode,
                       package: _Package,
                       skip_lib_copy: bool,
                       asyncoutput: bool,
                       legacy_block_access: bool) -> None:
        """

        Args:
            top_block:
            package:
            asyncoutput:
            legacy_block_access:

        Returns:

        """
        #pylint: disable=too-many-locals

        blocks = AddressMaps()
        # running the walker populated the blocks with all the address maps in within the
        # top block, including the top_block itself
        RDLWalker(unroll=True).walk(top_block, blocks, skip_top=False)

        for block in blocks:
            owned_elements = OwnedbyAddressMap()
            # running the walker populated the blocks with all the address maps in within the
            # top block, including the top_block itself
            RDLWalker(unroll=True).walk(block, owned_elements, skip_top=True)

            # The code that generates the tests for the register array context managers needs
            # the arrays rolled up but parents within the address map e.g. a regfile unrolled
            # I have not found a way to do this with the Walker as the unroll seems to be a
            # global setting, the following code works but it is not elegant
            rolled_owned_reg: List[RegNode] = list(block.registers(unroll=False))
            for regfile in owned_elements.reg_files:
                rolled_owned_reg += list(regfile.registers(unroll=False))
            for memory in owned_elements.memories:
                rolled_owned_reg += list(memory.registers(unroll=False))

            def is_reg_array(item: RegNode) -> bool:
                return item.is_array

            rolled_owned_reg_array = list(filter(is_reg_array, rolled_owned_reg))

            fq_block_name = '_'.join(block.get_path_segments(array_suffix='_{index:d}_'))

            context = {
                'top_node': top_block,
                'block': block,
                'fq_block_name': fq_block_name,
                'owned_elements': owned_elements,
                'rolled_owned_reg_array': rolled_owned_reg_array,
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
                'get_memory_width_bytes': get_memory_width_bytes,
                'asyncoutput': asyncoutput,
                'uses_enum': uses_enum(block),
                'skip_lib_copy': skip_lib_copy,
                'version': __version__,
                'get_array_typecode' : get_array_typecode,
                'legacy_block_access': legacy_block_access,
            }


            self.__stream_jinja_template(template_name="addrmap_tb.py.jinja",
                                         target_package=package.tests,
                                         target_name='test_' + fq_block_name + '.py',
                                         template_context=context)

            self.__stream_jinja_template(template_name="addrmap_simulation_tb.py.jinja",
                                         target_package=package.tests,
                                         target_name='test_sim_' + fq_block_name + '.py',
                                         template_context=context)

    def export(self, node: Node, path: str,  # pylint: disable=too-many-arguments
               asyncoutput: bool = False,
               skip_test_case_generation: bool = False,
               delete_existing_package_content: bool = True,
               skip_library_copy: bool = False,
               legacy_block_access: bool = True) -> List[str]:
        """
        Generated Python Code and Testbench

        Args:
            node (str) : Top-level node to export. Can be the top-level `RootNode` or any
                         internal `AddrmapNode`.
            path (str) : Output package path.
            asyncoutput (bool) : If set this builds a register model with async callbacks
            skip_test_case_generation (bool): skip generation the generation of the test cases
            delete_existing_package_content (bool): delete any python files in the package
                                                    location, normally left over from previous
                                                    operations
            skip_library_copy (bool): skip copy the libraries to the generated package, this is
                                      useful to turn off when developing peakrdl python to avoid
                                      editing the wrong copy of the library. However, it is not
                                      recommended in end user cases
            legacy_block_access (bool): version 0.8 changed the block access methods from using
                                        arrays to to lists. This allows memory widths of other
                                        than 8, 16, 32, 64 to be supported which are legal in
                                        systemRDL. The legacy mode with Arrays is still in
                                        the tool and will be turned on by default for a few
                                        releases.

        Returns:
            List[str] : modules that have been exported:
        """

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            top_block = node.top
        else:
            top_block = node

        if not isinstance(path, str):
            raise TypeError(f'path should be a str but got {type(path)}')
        package = _Package(path=path,
                           package_name=node.inst_name,
                           include_tests=not skip_test_case_generation,
                           include_libraries=not skip_library_copy)
        package.create_empty_package(cleanup=delete_existing_package_content)

        self._build_node_type_table(top_block)

        self.__export_reg_model(top_block=top_block, package=package, asyncoutput=asyncoutput,
                                skip_lib_copy=skip_library_copy,
                                legacy_block_access=legacy_block_access)

        self.__export_simulator(top_block=top_block, package=package, asyncoutput=asyncoutput,
                                skip_lib_copy=skip_library_copy,
                                legacy_block_access=legacy_block_access)

        self.__export_example(top_block=top_block, package=package, asyncoutput=asyncoutput,
                                skip_lib_copy=skip_library_copy,
                                legacy_block_access=legacy_block_access)

        if not skip_test_case_generation:

            # export the baseclasses for the tests
            self.__export_base_tests(top_block=top_block, package=package, asyncoutput=asyncoutput,
                                skip_lib_copy=skip_library_copy,
                                legacy_block_access=legacy_block_access)
            # export the tests themselves, these are broken down to one file per addressmap
            self.__export_tests(top_block=top_block, package=package, asyncoutput=asyncoutput,
                                skip_lib_copy=skip_library_copy,
                                legacy_block_access=legacy_block_access)

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
