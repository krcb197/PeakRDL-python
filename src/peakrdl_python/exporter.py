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
# pylint:disable=too-many-lines
import os
import re

from typing import NoReturn, Any, Optional, Union, TextIO
from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
import sys
from itertools import filterfalse

import jinja2 as jj
from systemrdl import RDLWalker

from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode
from systemrdl.node import SignalNode
from systemrdl.rdltypes.user_enum import UserEnum, UserEnumMeta
from systemrdl.rdltypes.user_struct import UserStruct

from .systemrdl_node_utility_functions import get_reg_writable_fields, \
    get_table_block,  \
    get_field_bitmask_hex_string, get_field_inv_bitmask_hex_string, \
    get_field_max_value_hex_string, get_reg_max_value_hex_string, \
    uses_enum, uses_memory, \
    get_memory_max_entry_value_hex_string, get_memory_width_bytes, \
    get_field_default_value, get_enum_values, get_properties_to_include, \
    HideNodeCallback, hide_based_on_property,  \
    is_encoded_field
from .unique_component_iterator import UniqueComponents
from .unique_component_iterator import PeakRDLPythonUniqueRegisterComponents
from .unique_component_iterator import PeakRDLPythonUniqueMemoryComponents
from .class_names import fully_qualified_enum_type, get_field_get_base_class_name
from .systemrdl_node_hashes import enum_hash

from .lib import get_array_typecode

from .safe_name_utility import get_python_path_segments, safe_node_name

from ._node_walkers import AddressMaps, OwnedbyAddressMap

from ._deploy_package import GeneratedPackage, PythonPackage

from .__about__ import __version__

file_path = os.path.dirname(__file__)

# same bit of code exists in base so flags as duplicate
# pylint: disable=duplicate-code
if sys.version_info >= (3, 10):
    # type guarding was introduced in python 3.10
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard
# pylint: enable=duplicate-code

# same bit of code exists in base so flags as duplicate
# pylint: disable=duplicate-code
if sys.version_info >= (3, 13):
    # the batched iterator was introduced in the python standard library at version 3.13
    # 3.12 did have a version without strict but to make this more consistent stick with this
    # full implementation even though this module does not use the strict option
    from itertools import batched
else:
    from more_itertools import batched
# pylint: enable=duplicate-code

DEFAULT_ENUM_FIELD_CLASS_PER_GENERATED_FILE = 50
DEFAULT_FIELD_CLASS_PER_GENERATED_FILE = 25
DEFAULT_REGISTER_CLASS_PER_GENERATED_FILE = 25
DEFAULT_MEMORY_CLASS_PER_GENERATED_FILE = 50

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
        self.strict = False  # strict RDL rules rather than helpful implicit behaviour

        # Check for stray kwargs
        if kwargs:
            raise ValueError("got an unexpected keyword argument")

        if user_template_dir:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(user_template_dir),
                jj.FileSystemLoader(os.path.join(file_path, "templates")),
                jj.PrefixLoader({'user': jj.FileSystemLoader(user_template_dir),
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

    def __stream_jinja_template(self,
                                template_name: str,
                                target_package: PythonPackage,
                                target_name: str,
                                template_context: dict[str, Any]) -> None:

        template_context.update(self.user_template_context)
        template_context['version'] = __version__

        template = self.jj_env.get_template(template_name)
        module_path = target_package.child_path(target_name)

        with module_path.open('w', encoding='utf-8') as fp:
            stream = template.stream(template_context)
            stream.dump(fp)

    def __insert_header(self, file_stream: TextIO, top_block: AddrmapNode) -> None:
        """
        Insert the header template block into a file stream, this is intended to be used for the
        __init__.py files which are built incrementally with the batches of files

        Args:
            file_stream: File Stream to be added to
            top_block: top address map

        Returns: None

        """

        template_context = {'top_node': top_block,
                            'version': __version__, }
        template_context.update(self.user_template_context)
        template = self.jj_env.get_template('header.py.jinja')
        stream = template.stream(template_context)
        stream.dump(file_stream)
        file_stream.write('\n')

    # pylint: disable-next=too-many-arguments,too-many-locals
    def __export_reg_model(self, *,
                           top_block: AddrmapNode,
                           package: GeneratedPackage,
                           skip_lib_copy: bool,
                           asyncoutput: bool,
                           legacy_block_access: bool,
                           udp_to_include: Optional[list[str]],
                           hide_node_func: HideNodeCallback,
                           legacy_enum_type: bool,
                           skip_systemrdl_name_and_desc_properties: bool,
                           register_class_per_generated_file: int,
                           field_class_per_generated_file: int,
                           enum_field_class_per_generated_file: int,
                           memory_class_per_generated_file: int) -> None:

        def visible_nonsignal_node(node: Node) -> int:
            count = 0
            for child_node in node.children(unroll=False):
                if not isinstance(child_node, SignalNode):
                    if not hide_node_func(child_node):
                        count +=1
            return count

        unique_component_walker = UniqueComponents(hide_node_callback=hide_node_func,
                                                   udp_to_include=udp_to_include)
        RDLWalker(unroll=True).walk(top_block.parent, unique_component_walker,
                                    skip_top=False)

        top_file_components = filterfalse(
            lambda component: isinstance(component.instance, (FieldNode, RegNode, MemNode)),
            reversed(unique_component_walker.nodes.values()))

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
            'systemrdlUserEnum': UserEnum,
            'systemrdlUserStruct': UserStruct,
            'asyncoutput': asyncoutput,
            'isinstance': isinstance,
            'str': str,
            'uses_enum': uses_enum(top_block),
            'get_fully_qualified_type_name': partial(
                unique_component_walker.python_class_name,
                async_library_classes=asyncoutput),
            'unique_components': top_file_components,
            'dependent_registers': unique_component_walker.register_nodes(),
            'dependent_memories': unique_component_walker.memory_nodes(),
            'unique_enums': self._get_dependent_enum(unique_component_walker),
            'get_enum_values': get_enum_values,
            'get_table_block': get_table_block,
            'raise_template_error': self._raise_template_error,
            'safe_node_name': safe_node_name,
            'skip_lib_copy': skip_lib_copy,
            'legacy_block_access': legacy_block_access,
            'udp_to_include': udp_to_include,
            'get_properties_to_include': get_properties_to_include,
            'unique_property_enums':
                self._get_dependent_property_enum(unique_component_walker),
            'hide_node_func': hide_node_func,
            'visible_nonsignal_node' : visible_nonsignal_node,
            'legacy_enum_type': legacy_enum_type,
            'skip_systemrdl_name_and_desc_properties': skip_systemrdl_name_and_desc_properties,
        }
        if legacy_block_access is True:
            context['get_array_typecode'] = get_array_typecode

        self.__stream_jinja_template(template_name="addrmap.py.jinja",
                                     target_package=package.reg_model,
                                     target_name=top_block.inst_name + '.py',
                                     template_context=context)

        if uses_memory(top_block):
            self.__export_reg_model_memories(
                top_block=top_block,
                package=package,
                skip_lib_copy=skip_lib_copy,
                asyncoutput=asyncoutput,
                legacy_block_access=legacy_block_access,
                hide_node_func=hide_node_func,
                legacy_enum_type=legacy_enum_type,
                skip_systemrdl_name_and_desc_properties=skip_systemrdl_name_and_desc_properties,
                unique_component_walker=unique_component_walker,
                visible_nonsignal_node=visible_nonsignal_node,
                memory_class_per_generated_file=memory_class_per_generated_file,
            )

        self.__export_reg_model_registers(
            top_block=top_block,
            package=package,
            skip_lib_copy=skip_lib_copy,
            asyncoutput=asyncoutput,
            legacy_block_access=legacy_block_access,
            hide_node_func=hide_node_func,
            legacy_enum_type=legacy_enum_type,
            skip_systemrdl_name_and_desc_properties=skip_systemrdl_name_and_desc_properties,
            unique_component_walker=unique_component_walker,
            visible_nonsignal_node=visible_nonsignal_node,
            register_class_per_generated_file=register_class_per_generated_file,
        )

        self.__export_reg_model_fields(
            top_block=top_block,
            package=package,
            skip_lib_copy=skip_lib_copy,
            asyncoutput=asyncoutput,
            legacy_enum_type=legacy_enum_type,
            skip_systemrdl_name_and_desc_properties=skip_systemrdl_name_and_desc_properties,
            unique_component_walker=unique_component_walker,
            field_class_per_generated_file=field_class_per_generated_file)


        # field enumerations
        if uses_enum(top_block):
            self.__export_reg_model_field_enums(
                top_block=top_block,
                package=package,
                skip_lib_copy=skip_lib_copy,
                legacy_enum_type=legacy_enum_type,
                skip_systemrdl_name_and_desc_properties=skip_systemrdl_name_and_desc_properties,
                unique_component_walker=unique_component_walker,
                enum_field_class_per_generated_file=enum_field_class_per_generated_file)

        # property enumerations
        context = {
            'top_node': top_block,
            'unique_property_enums':
                self._get_dependent_property_enum(unique_component_walker),
            'skip_lib_copy': skip_lib_copy,
            'legacy_enum_type': legacy_enum_type,
        }

        self.__stream_jinja_template(template_name="property_enums.py.jinja",
                                     target_package=package.reg_model,
                                     target_name=top_block.inst_name + '_property_enums.py',
                                     template_context=context)

    # pylint: disable-next=too-many-arguments,too-many-locals
    def __export_reg_model_registers(self, *,
                                     top_block: AddrmapNode,
                                     package: GeneratedPackage,
                                     skip_lib_copy: bool,
                                     asyncoutput: bool,
                                     legacy_block_access: bool,
                                     hide_node_func: HideNodeCallback,
                                     legacy_enum_type: bool,
                                     skip_systemrdl_name_and_desc_properties: bool,
                                     unique_component_walker: UniqueComponents,
                                     visible_nonsignal_node: Callable[[Node], int],
                                     register_class_per_generated_file: int) -> None:
        """
        Sub function of the __export_reg_model which exports the register class definitions into
        a batch of files within the registers sub-package of the main reg_model package
        """

        def init_line_entry(module_name: str,
                            register: PeakRDLPythonUniqueRegisterComponents) -> str:
            base_entry = f'from .{module_name} import {register.python_class_name}'
            array_entry = base_entry + '_array'

            if register.instance.is_array:
                return f'{base_entry}\n{array_entry}\n'

            return f'{base_entry}\n'

        # registers which are broken up to multiple files to prevent anything getting too big
        with package.reg_model.registers.init_file_stream() as init_fid:
            # put the header on the field package __init__.py
            self.__insert_header(file_stream=init_fid,
                                 top_block=top_block)

            for index, unique_register_subset in enumerate(
                    batched(
                        unique_component_walker.register_nodes(),
                        n=register_class_per_generated_file)
            ):

                # make list of all the field and field enum class names that need to be pulled into
                # the module associated with this batch of registers
                dependent_field_cls = []
                dependent_field_enum_cls = []
                for register in unique_register_subset:
                    for field in register.fields():
                        field_cls = unique_component_walker.python_class_name(
                            async_library_classes=asyncoutput,
                            node=field)
                        field_cls_base = get_field_get_base_class_name(
                            node=field,
                            async_library_classes=asyncoutput)
                        if field_cls_base != field_cls and field_cls not in dependent_field_cls:
                            dependent_field_cls.append(field_cls)
                        if is_encoded_field(field):
                            encoding_enum = field.get_property('encode')
                            if encoding_enum is None:
                                raise RuntimeError('This should never happen')
                            field_enum_cls = fully_qualified_enum_type(
                                encoding_enum) + '_enumcls'
                            if field_enum_cls not in dependent_field_enum_cls:
                                dependent_field_enum_cls.append(field_enum_cls)

                context = {
                    'top_node': top_block,
                    'systemrdlRegNode': RegNode,
                    'systemrdlFieldNode': FieldNode,
                    'systemrdlSignalNode': SignalNode,
                    'systemrdlUserStruct': UserStruct,
                    'systemrdlUserEnum': UserEnum,
                    'isinstance': isinstance,
                    'type': type,
                    'str': str,
                    'asyncoutput': asyncoutput,
                    'unique_registers': unique_register_subset,
                    'unique_property_enums':
                        self._get_dependent_property_enum(unique_component_walker),
                    'get_table_block': get_table_block,
                    'get_fully_qualified_type_name': partial(
                        unique_component_walker.python_class_name,
                        async_library_classes=asyncoutput),
                    'get_fully_qualified_enum_type': fully_qualified_enum_type,
                    'get_field_default_value': get_field_default_value,
                    'is_encoded_field': is_encoded_field,
                    'skip_lib_copy': skip_lib_copy,
                    'uses_enum': uses_enum(top_block),
                    'legacy_enum_type': legacy_enum_type,
                    'legacy_block_access': legacy_block_access,
                    'skip_systemrdl_name_and_desc_properties':
                        skip_systemrdl_name_and_desc_properties,
                    'raise_template_error': self._raise_template_error,
                    'safe_node_name': safe_node_name,
                    'dependent_enums': dependent_field_enum_cls,
                    'dependent_fields': dependent_field_cls,
                    'hide_node_func': hide_node_func,
                    'visible_nonsignal_node': visible_nonsignal_node,
                }

                module_name = top_block.inst_name + f'_registers{index}'
                self.__stream_jinja_template(template_name="addrmap_register.py.jinja",
                                             target_package=package.reg_model.registers,
                                             target_name=module_name + '.py',
                                             template_context=context)

                init_fid.writelines((init_line_entry(module_name, register)
                                     for register in unique_register_subset))

    # pylint: disable-next=too-many-arguments,too-many-locals
    def __export_reg_model_memories(self, *,
                                     top_block: AddrmapNode,
                                     package: GeneratedPackage,
                                     skip_lib_copy: bool,
                                     asyncoutput: bool,
                                     legacy_block_access: bool,
                                     hide_node_func: HideNodeCallback,
                                     legacy_enum_type: bool,
                                     skip_systemrdl_name_and_desc_properties: bool,
                                     unique_component_walker: UniqueComponents,
                                     visible_nonsignal_node: Callable[[Node], int],
                                     memory_class_per_generated_file: int) -> None:
        """
        Sub function of the __export_reg_model which exports the memory class definitions into
        a batch of files within the memories sub-package of the main reg_model package
        """
        def init_line_entry(module_name:str,
                            memory:PeakRDLPythonUniqueMemoryComponents) -> str:
            base_entry = f'from .{module_name} import {memory.python_class_name}'
            array_entry = base_entry + '_array'

            if memory.instance.is_array:
                return f'{base_entry}\n{array_entry}\n'

            return f'{base_entry}\n'

        # registers which are broken up to multiple files to prevent anything getting too big
        with package.reg_model.memories.init_file_stream() as init_fid:
            # put the header on the field package __init__.py
            self.__insert_header(file_stream=init_fid,
                                 top_block=top_block)

            for index, unique_memory_subset in enumerate(
                    batched(
                        unique_component_walker.memory_nodes(),
                        n=memory_class_per_generated_file)
            ):

                # make list of all the register class names that need to be pulled into
                # the module associated with this batch of memories
                dependent_reg_cls = []
                for memory in unique_memory_subset:
                    for register in memory.registers(unroll=False):
                        register_cls = unique_component_walker.python_class_name(
                            async_library_classes=asyncoutput,
                            node=register)
                        if register.is_array:
                            register_cls += '_array'
                        if register_cls not in dependent_reg_cls:
                            dependent_reg_cls.append(register_cls)

                context = {
                    'top_node': top_block,
                    'systemrdlMemNode': MemNode,
                    'systemrdlFieldNode': FieldNode,
                    'systemrdlSignalNode': SignalNode,
                    'systemrdlUserStruct': UserStruct,
                    'systemrdlUserEnum': UserEnum,
                    'isinstance': isinstance,
                    'type': type,
                    'str': str,
                    'asyncoutput': asyncoutput,
                    'unique_memories': unique_memory_subset,
                    'unique_property_enums':
                        self._get_dependent_property_enum(unique_component_walker),
                    'get_table_block': get_table_block,
                    'get_fully_qualified_type_name': partial(
                        unique_component_walker.python_class_name,
                        async_library_classes=asyncoutput),
                    'get_fully_qualified_enum_type': fully_qualified_enum_type,
                    'get_field_default_value': get_field_default_value,
                    'is_encoded_field': is_encoded_field,
                    'skip_lib_copy': skip_lib_copy,
                    'uses_enum': uses_enum(top_block),
                    'legacy_enum_type': legacy_enum_type,
                    'legacy_block_access': legacy_block_access,
                    'skip_systemrdl_name_and_desc_properties':
                        skip_systemrdl_name_and_desc_properties,
                    'raise_template_error': self._raise_template_error,
                    'safe_node_name': safe_node_name,
                    'hide_node_func': hide_node_func,
                    'visible_nonsignal_node': visible_nonsignal_node,
                    'dependent_registers': dependent_reg_cls,
                }

                module_name = top_block.inst_name + f'_memories{index}'
                self.__stream_jinja_template(template_name="addrmap_memory.py.jinja",
                                             target_package=package.reg_model.memories,
                                             target_name=module_name + '.py',
                                             template_context=context)

                init_fid.writelines( (init_line_entry(module_name,memory)
                                      for memory in unique_memory_subset))

    # pylint: disable-next=too-many-arguments
    def __export_reg_model_fields(self, *,
                                  top_block: AddrmapNode,
                                  package: GeneratedPackage,
                                  skip_lib_copy: bool,
                                  asyncoutput: bool,
                                  legacy_enum_type: bool,
                                  skip_systemrdl_name_and_desc_properties: bool,
                                  unique_component_walker: UniqueComponents,
                                  field_class_per_generated_file: int
                                  ) -> None:
        """
        Sub function of the __export_reg_model which exports the field class definitions into
        a batch of files within the registers.fields sub-package of the main reg_model package
        """
        with package.reg_model.registers.fields.init_file_stream() as init_fid:
            # put the header on the field package __init__.py
            self.__insert_header(file_stream=init_fid,
                                 top_block=top_block)

            for index, unique_fields_subset in enumerate(
                    batched(
                        filter(
                            lambda component: isinstance(component.instance, FieldNode),
                            unique_component_walker.nodes.values()),
                        n=field_class_per_generated_file)
            ):

                context = {
                    'top_node': top_block,
                    'systemrdlFieldNode': FieldNode,
                    'systemrdlUserStruct': UserStruct,
                    'systemrdlUserEnum': UserEnum,
                    'isinstance': isinstance,
                    'type': type,
                    'str': str,
                    'asyncoutput': asyncoutput,
                    'unique_fields': unique_fields_subset,
                    'unique_property_enums':
                        self._get_dependent_property_enum(unique_component_walker),
                    'get_table_block': get_table_block,
                    'skip_lib_copy': skip_lib_copy,
                    'uses_enum': uses_enum(top_block),
                    'legacy_enum_type': legacy_enum_type,
                    'skip_systemrdl_name_and_desc_properties':
                        skip_systemrdl_name_and_desc_properties,
                    'raise_template_error': self._raise_template_error,
                }

                module_name = top_block.inst_name + f'_fields{index}'
                self.__stream_jinja_template(template_name="addrmap_field.py.jinja",
                                             target_package=package.reg_model.registers.fields,
                                             target_name=module_name + '.py',
                                             template_context=context)

                init_fid.writelines((f'from .{module_name} import {field.python_class_name}\n'
                                     for field in unique_fields_subset))

    # pylint: disable-next=too-many-arguments
    def __export_reg_model_field_enums(self, *,
                                       top_block: AddrmapNode,
                                       package: GeneratedPackage,
                                       skip_lib_copy: bool,
                                       legacy_enum_type: bool,
                                       skip_systemrdl_name_and_desc_properties: bool,
                                       unique_component_walker: UniqueComponents,
                                       enum_field_class_per_generated_file: int) -> None:
        """
        Sub function of the __export_reg_model which exports the field enumeration class
        definitions into a batch of files within the registers.field_enus sub-packaage of the main
        reg_model package
        """
        def init_line_entry(module_name:str, field_enum:UserEnumMeta) -> str:
            return f'from .{module_name} import {fully_qualified_enum_type(field_enum)}_enumcls\n'

        with package.reg_model.registers.field_enum.init_file_stream() as init_fid:
            # put the header on the field package __init__.py
            self.__insert_header(file_stream=init_fid,
                                 top_block=top_block)

            for index, unique_enums_subset in enumerate(
                    batched(
                        self._get_dependent_enum(unique_component_walker),
                        n=enum_field_class_per_generated_file)
            ):
                context = {
                    'top_node': top_block,
                    'unique_enums': unique_enums_subset,
                    'get_fully_qualified_enum_type': fully_qualified_enum_type,
                    'skip_lib_copy': skip_lib_copy,
                    'legacy_enum_type': legacy_enum_type,
                    'skip_systemrdl_name_and_desc_properties':
                        skip_systemrdl_name_and_desc_properties
                }

                field_enum_module_name = top_block.inst_name + f'_fields_enums{index}'
                self.__stream_jinja_template(template_name="field_enums.py.jinja",
                                             target_package=package.reg_model.registers.field_enum,
                                             target_name=field_enum_module_name + '.py',
                                             template_context=context)

                init_fid.writelines(
                    (init_line_entry(module_name=field_enum_module_name, field_enum=field_enum)
                     for field_enum in unique_enums_subset))

    def __export_simulator(self, *,
                           top_block: AddrmapNode,
                           package: GeneratedPackage,
                           skip_lib_copy: bool,
                           asyncoutput: bool,
                           legacy_block_access: bool) -> None:

        # as a result of issue 202, where two registers existed at that same address,
        # rather than iterating through the registers within the Jinja template
        # we iterate through them in advance so that cases of two registers at that same
        # address can be identified
        reg_dict:dict[int, Union[list[RegNode],RegNode]] = {}
        for node in filter(lambda x : isinstance(x, RegNode),  top_block.descendants(unroll=True)):
            if not isinstance(node, RegNode):
                raise TypeError(f'node should be a register, got {type(node)}')
            reg_addr = node.absolute_address
            if reg_addr in reg_dict:
                existing_entry = reg_dict[reg_addr]
                # if the entry is already list simply append to it
                if isinstance(existing_entry, list):
                    existing_entry.append(node)
                elif isinstance(existing_entry, RegNode):
                    reg_dict[reg_addr] = [existing_entry, node]
                else:
                    raise TypeError(f'exiting entry of unexpected type: {type(existing_entry)}')
            else:
                reg_dict[reg_addr] = node


        context = {
            'top_node': top_block,
            'reg_dict': reg_dict,
            'systemrdlRegNode': RegNode,
            'systemrdlMemNode': MemNode,
            'isinstance': isinstance,
            'asyncoutput': asyncoutput,
            'skip_lib_copy': skip_lib_copy,
            'legacy_block_access': legacy_block_access,
            'list': list
        }

        self.__stream_jinja_template(template_name="sim_addrmap.py.jinja",
                                     target_package=package.sim,
                                     target_name=top_block.inst_name + '.py',
                                     template_context=context)

    def __export_example(self, *,
                         top_block: AddrmapNode,
                         package: GeneratedPackage,
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
            'legacy_block_access': legacy_block_access,
        }

        self.__stream_jinja_template(template_name="example.py.jinja",
                                     target_package=package,
                                     target_name='example.py',
                                     template_context=context)

    # pylint: disable-next=too-many-arguments
    def __export_base_tests(self, *,
                            top_block: AddrmapNode,
                            package: GeneratedPackage,
                            skip_lib_copy: bool,
                            asyncoutput: bool,
                            legacy_block_access: bool,
                            legacy_enum_type: bool) -> None:

        context = {
            'top_node': top_block,
            'asyncoutput': asyncoutput,
            'skip_lib_copy': skip_lib_copy,
            'legacy_block_access': legacy_block_access,
            'legacy_enum_type': legacy_enum_type
        }

        self.__stream_jinja_template(template_name="baseclass_tb.py.jinja",
                                     target_package=package.tests,
                                     target_name='_' + top_block.inst_name + '_test_base.py',
                                     template_context=context)

        self.__stream_jinja_template(template_name="baseclass_simulation_tb.py.jinja",
                                     target_package=package.tests,
                                     target_name='_' + top_block.inst_name + '_sim_test_base.py',
                                     template_context=context)

    # pylint: disable-next=too-many-arguments
    def __export_tests(self, *,
                       top_block: AddrmapNode,
                       package: GeneratedPackage,
                       skip_lib_copy: bool,
                       asyncoutput: bool,
                       legacy_block_access: bool,
                       udp_to_include: Optional[list[str]],
                       hide_node_func: HideNodeCallback,
                       legacy_enum_type: bool,
                       skip_systemrdl_name_and_desc_properties: bool,
                       ) -> None:

        # pylint: disable=too-many-locals

        blocks = AddressMaps(hide_node_callback=hide_node_func)
        # running the walker populated the blocks with all the address maps in within the
        # top block, including the top_block itself
        RDLWalker(unroll=True).walk(top_block, blocks, skip_top=False)

        for block in blocks:
            owned_elements = OwnedbyAddressMap(hide_node_callback=hide_node_func)
            # running the walker populated the blocks with all the address maps in within the
            # top block, including the top_block itself
            RDLWalker(unroll=True).walk(block, owned_elements, skip_top=True)

            # The code that generates the tests for the register array context managers needs
            # the arrays rolled up but parents within the address map e.g. a regfile unrolled
            # I have not found a way to do this with the Walker as the unroll seems to be a
            # global setting, the following code works but it is not elegant
            rolled_owned_reg: list[RegNode] = list(block.registers(unroll=False))
            for regfile in owned_elements.reg_files:
                rolled_owned_reg += list(regfile.registers(unroll=False))
            for memory in owned_elements.memories:
                rolled_owned_reg += list(memory.registers(unroll=False))

            def is_reg_array(item: RegNode) -> bool:
                return item.is_array and not hide_node_func(item)

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
                'systemrdlUserEnum': UserEnum,
                'systemrdlUserStruct': UserStruct,
                'isinstance': isinstance,
                'type': type,
                'str': str,
                'get_python_path_segments': get_python_path_segments,
                'safe_node_name': safe_node_name,
                'uses_memory': (len(owned_elements.memories) > 0),
                'get_field_bitmask_hex_string': get_field_bitmask_hex_string,
                'get_field_inv_bitmask_hex_string': get_field_inv_bitmask_hex_string,
                'get_field_max_value_hex_string': get_field_max_value_hex_string,
                'get_field_default_value': get_field_default_value,
                'get_reg_max_value_hex_string': get_reg_max_value_hex_string,
                'get_reg_writable_fields': partial(get_reg_writable_fields,
                                                   hide_node_callback=hide_node_func),
                'get_memory_max_entry_value_hex_string': get_memory_max_entry_value_hex_string,
                'get_enum_values': get_enum_values,
                'get_memory_width_bytes': get_memory_width_bytes,
                'asyncoutput': asyncoutput,
                'uses_enum': uses_enum(block),
                'skip_lib_copy': skip_lib_copy,
                'get_array_typecode': get_array_typecode,
                'legacy_block_access': legacy_block_access,
                'udp_to_include': udp_to_include,
                'get_properties_to_include': get_properties_to_include,
                'hide_node_func': hide_node_func,
                'legacy_enum_type': legacy_enum_type,
                'skip_systemrdl_name_and_desc_properties': skip_systemrdl_name_and_desc_properties
            }

            self.__stream_jinja_template(template_name="addrmap_tb.py.jinja",
                                         target_package=package.tests,
                                         target_name='test_' + fq_block_name + '.py',
                                         template_context=context)

            self.__stream_jinja_template(template_name="addrmap_simulation_tb.py.jinja",
                                         target_package=package.tests,
                                         target_name='test_sim_' + fq_block_name + '.py',
                                         template_context=context)

    def _validate_udp_to_include(self, udp_to_include: Optional[list[str]]) -> None:
        if udp_to_include is not None:
            # the list of user defined properties may not include the names used by peakrdl python
            # for control behaviours
            if not isinstance(udp_to_include, list):
                raise TypeError(f'The user_defined_properties_to_include must be a list, got '
                                f'{type(udp_to_include)}')
            for entry in udp_to_include:
                if not isinstance(entry, str):
                    raise TypeError('The entries in the user_defined_properties_to_include must '
                                    f'be a str, got {type(entry)}')
            reserved_names = ['python_hide', 'python_name']
            for reserved_name in reserved_names:
                if reserved_name in udp_to_include:
                    raise RuntimeError('It is not permitted to expose a property name used to'
                                       ' build the peakrdl-python wrappers: ' + reserved_name)

    # pylint: disable-next=too-many-arguments,too-many-locals
    def export(self, node: Union[RootNode, AddrmapNode], path: str, *,
               asyncoutput: bool = False,
               skip_test_case_generation: bool = False,
               delete_existing_package_content: bool = True,
               skip_library_copy: bool = False,
               legacy_block_access: bool = True,
               show_hidden: bool = False,
               user_defined_properties_to_include: Optional[list[str]] = None,
               hidden_inst_name_regex: Optional[str] = None,
               legacy_enum_type: bool = True,
               skip_systemrdl_name_and_desc_properties: bool = False,
               register_class_per_generated_file: int =
                   DEFAULT_REGISTER_CLASS_PER_GENERATED_FILE,
               field_class_per_generated_file: int =
                   DEFAULT_FIELD_CLASS_PER_GENERATED_FILE,
               enum_field_class_per_generated_file: int =
                   DEFAULT_ENUM_FIELD_CLASS_PER_GENERATED_FILE,
               memory_class_per_generated_file: int =
                   DEFAULT_MEMORY_CLASS_PER_GENERATED_FILE,
               ) -> str:
        """
        Generated Python Code and Testbench

        Args:
            node: Top-level node to export. Can be the top-level `RootNode` or any
                  internal `AddrmapNode`.
            path: Output package path.
            asyncoutput: If set this builds a register model with async callbacks
            skip_test_case_generation: skip generation the generation of the test cases
            delete_existing_package_content: delete any python files in the package
                                             location, normally left over from previous
                                             operations
            skip_library_copy: skip copy the libraries to the generated package, this is
                               useful to turn off when developing peakrdl python to avoid
                               editing the wrong copy of the library. It also avoids the
                               GPL code being part of the package for distribution,
                               However, this means the end-user is responsible for
                               installing the libraries.
            legacy_block_access: version 0.8 changed the block access methods from using
                                 arrays to lists. This allows memory widths of other
                                 than 8, 16, 32, 64 to be supported which are legal in
                                 systemRDL. The legacy mode with Arrays is still in
                                 the tool and will be turned on by default for a few
                                 releases.
            show_hidden: By default any item (Address Map, Regfile, Register, Memory or
                         Field) with the systemRDL User Defined Property (UDP)
                         ``python_hide`` set to true will not be included in the generated
                         python code. This behaviour can be overridden by setting this
                         property to true.
            user_defined_properties_to_include : A list of strings of the names of user-defined
                                                 properties to include. Set to None for nothing
                                                 to appear.
            hidden_inst_name_regex: A regular expression which will hide any fully
                                    qualified instance name that matches, set to None to
                                    for this to have no effect
            legacy_enum_type: version 1.2 introduced a new Enum type that allows system
                              rdl ``name`` and ``desc`` properties on field encoding
                              to be included. The legacy mode uses python IntEnum.
            skip_systemrdl_name_and_desc_properties (bool) : version 1.2 introduced new properties
                                                             that include the systemRDL name and
                                                             desc as properties of the built
                                                             python. Setting this option to
                                                             ``True`` will exclude them.
            register_class_per_generated_file : Number of register class definitions to put in
                                                each python module of the generated code.
                                                Make sure this is set to ensure the file does not
                                                get too big otherwise the generation and loading
                                                is slow.
            field_class_per_generated_file  : Number of register class definitions to put in
                                              each python module of the generated code.
                                              Make sure this is set to ensure the file does not
                                              get too big otherwise the generation and loading
                                              is slow.
            enum_field_class_per_generated_file : Number of register class definitions to put in
                                                  each python module of the generated code.
                                                  Make sure this is set to ensure the file does not
                                                  get too big otherwise the generation and loading
                                                  is slow.
            memory_class_per_generated_file : Number of memory class definitions to put in
                                              each python module of the generated code.
                                              Make sure this is set to ensure the file does not
                                              get too big otherwise the generation and loading
                                              is slow.

        Returns:
            modules that have been exported:
        """

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            top_block = node.top
        else:
            if not isinstance(node, AddrmapNode):
                raise TypeError(f'node must be an AddrmapNode got {type(node)}')
            top_block = node

        if not isinstance(path, str):
            raise TypeError(f'path should be a str but got {type(path)}')
        package = GeneratedPackage(path=path,
                                   package_name=node.inst_name,
                                   include_tests=not skip_test_case_generation,
                                   include_libraries=not skip_library_copy)
        package.create_empty_package(cleanup=delete_existing_package_content)

        self._validate_udp_to_include(udp_to_include=user_defined_properties_to_include)

        if hidden_inst_name_regex is not None:
            hidden_inst_name_regex_re = re.compile(hidden_inst_name_regex)

            def hide_node_func(node: Node) -> bool:
                """
                Returns True if the node should be hidden based on either the python property or
                regex match to the name
                """
                if hide_based_on_property(node=node, show_hidden=show_hidden):
                    return True

                result = hidden_inst_name_regex_re.match('.'.join(node.get_path_segments()))
                return result is not None
        else:
            def hide_node_func(node: Node) -> bool:
                """
                Returns True if the node should be hidden based on either the python property
                """
                return hide_based_on_property(node=node, show_hidden=show_hidden)

        # if the top level node is hidden the wrapper will be meaningless, rather then try to
        # handle a special case this is treated as an error
        if hide_node_func(top_block):
            raise RuntimeError('PeakRDL Python can not export if the node is hidden')

        self.__export_reg_model(
            top_block=top_block, package=package, asyncoutput=asyncoutput,
            skip_lib_copy=skip_library_copy,
            legacy_block_access=legacy_block_access,
            udp_to_include=user_defined_properties_to_include,
            hide_node_func=hide_node_func,
            legacy_enum_type=legacy_enum_type,
            skip_systemrdl_name_and_desc_properties=skip_systemrdl_name_and_desc_properties,
            register_class_per_generated_file=register_class_per_generated_file,
            field_class_per_generated_file=field_class_per_generated_file,
            enum_field_class_per_generated_file=enum_field_class_per_generated_file,
            memory_class_per_generated_file=memory_class_per_generated_file,
        )

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
                                     legacy_block_access=legacy_block_access,
                                     legacy_enum_type=legacy_enum_type)
            # export the tests themselves, these are broken down to one file per addressmap
            self.__export_tests(
                top_block=top_block, package=package, asyncoutput=asyncoutput,
                skip_lib_copy=skip_library_copy,
                legacy_block_access=legacy_block_access,
                udp_to_include=user_defined_properties_to_include,
                hide_node_func=hide_node_func,
                legacy_enum_type=legacy_enum_type,
                skip_systemrdl_name_and_desc_properties=skip_systemrdl_name_and_desc_properties)

        return top_block.inst_name

    def _raise_template_error(self, message: str) -> NoReturn:
        """
        Helper function to raise an exception from within the templating

        Args:
            message: message to put in the exception

        Raises: PythonExportTemplateError

        """
        raise PythonExportTemplateError(message)

    @staticmethod
    def _get_dependent_enum(unique_components: UniqueComponents) -> Iterable[UserEnumMeta]:
        """
        iterable of enums which is used by a descendant of the input node,
        this list is de-duplicated
        """
        def is_encoded_field_filter(node: Node) -> TypeGuard[FieldNode]:
            if isinstance(node, FieldNode):
                return is_encoded_field(node)
            return False

        unique_field_components = \
            filter(is_encoded_field_filter,
                   [component.instance for component in unique_components.nodes.values()])

        enum_needed = []
        for encoded_field in unique_field_components:
            field_enum = encoded_field.get_property('encode')
            if field_enum is None:
                raise RuntimeError('All field found here should be encoded (due to prefilter)')

            field_enum_hash = enum_hash(field_enum)

            if field_enum_hash not in enum_needed:
                enum_needed.append(field_enum_hash)
                yield field_enum

    @staticmethod
    def _get_dependent_property_enum( unique_components: UniqueComponents) -> \
            list[UserEnumMeta]:
        """
        iterable of enums which is used by a descendant of the input node,
        this list is de-duplicated
        """
        enum_needed: list[UserEnumMeta] = []

        def walk_property_struct_node(value: Any) -> None:
            if isinstance(value, UserEnum) and type(value) not in enum_needed:
                enum_type = type(value)
                if not isinstance(enum_type, UserEnumMeta):
                    raise TypeError(f'enum type should be UserEnumMeta, got {type(enum_type)}')
                enum_needed.append(enum_type)

            if isinstance(value, UserStruct):
                for sub_value in value.members.values():
                    walk_property_struct_node(sub_value)

        for node in unique_components.nodes.values():
            for node_property_name in node.properties_to_include:
                node_property = node.instance.get_property(node_property_name)
                if isinstance(node_property, UserEnum) and type(node_property) not in enum_needed:
                    enum_type = type(node_property)
                    if not isinstance(enum_type, UserEnumMeta):
                        raise TypeError(f'enum type should be UserEnumMeta, got {type(enum_type)}')
                    enum_needed.append(enum_type)

                if isinstance(node_property, UserStruct):
                    for sub_value in node_property.members.values():
                        walk_property_struct_node(sub_value)

        return enum_needed
