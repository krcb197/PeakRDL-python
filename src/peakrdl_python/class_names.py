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

A module for determining the classes names to use
"""
from typing import Optional
from systemrdl.node import Node
from systemrdl.node import FieldNode
from systemrdl.node import RegNode
from systemrdl.node import MemNode
from systemrdl.rdltypes.user_enum import UserEnumMeta
from .systemrdl_node_utility_functions import HideNodeCallback
from .systemrdl_node_utility_functions import is_encoded_field

from .systemrdl_node_hashes import node_hash as calculate_node_hash

def __get_field_get_base_class_name(node: FieldNode, async_library_classes: bool) -> str:
    if not isinstance(node, FieldNode):
        raise TypeError(f'node should be FieldNode, got: {type(node)}')

    name = 'Field'
    if is_encoded_field(node):
        name += 'Enum'
    if async_library_classes:
        name += 'Async'

    if node.is_sw_readable and node.is_sw_writable:
        name += 'ReadWrite'
    elif node.is_sw_readable and not node.is_sw_writable:
        name += 'ReadOnly'
    elif not node.is_sw_readable and node.is_sw_writable:
        name += 'WriteOnly'
    else:
        raise ValueError('Unhandled field access mode')

    return name


def __get_reg_get_base_class_name(node: RegNode, async_library_classes: bool) -> str:
    if not isinstance(node, RegNode):
        raise TypeError(f'node should be RegNode, got: {type(node)}')

    name = 'Reg'
    if async_library_classes:
        name += 'Async'
    if node.has_sw_readable and node.has_sw_writable:
        name += 'ReadWrite'
    elif node.has_sw_readable and not node.has_sw_writable:
        name += 'ReadOnly'
    elif not node.has_sw_readable and node.has_sw_writable:
        name += 'WriteOnly'
    else:
        raise ValueError('Unhandled field access mode')

    return name

def __get_mem_get_base_class_name(node: MemNode, async_library_classes: bool) -> str:
    if not isinstance(node, MemNode):
        raise TypeError(f'node should be MemNode, got: {type(node)}')

    name = 'Memory'
    if async_library_classes:
        name += 'Async'

    if node.is_sw_readable and node.is_sw_writable:
        name += 'ReadWrite'
    elif node.is_sw_readable and not node.is_sw_writable:
        name += 'ReadOnly'
    elif not node.is_sw_readable and node.is_sw_writable:
        name += 'WriteOnly'
    else:
        raise ValueError('Unhandled field access mode')

    return name

def get_base_class_name(node: Node, async_library_classes: bool) -> str:
    """
    Returns the base class from the library to use with the node instance
    """
    if isinstance(node, FieldNode):
        return __get_field_get_base_class_name(node, async_library_classes=async_library_classes)

    if isinstance(node, RegNode):
        return __get_reg_get_base_class_name(node, async_library_classes=async_library_classes)

    if isinstance(node, MemNode):
        return __get_mem_get_base_class_name(node, async_library_classes=async_library_classes)

    raise TypeError(f'Unhandled node type: {type(node)}')


def get_fully_qualified_type_name_precalculated_hash(
        node: Node,
        node_hash: Optional[int]) -> str:
    """
    Returns the fully qualified class type name with a pre-calculated hash to save time
    """
    if not isinstance(node, Node):
        raise TypeError(f'Expected a System RDL Node from the complier, got {type(node)}')

    scope_path = node.inst.get_scope_path(scope_separator='_')

    # the node.inst.type_name may include a suffix for the reset value, peak_rdl python passes
    # the reset value in when the component is initialised so this is not needed. Therefore,
    # the orginal_def version plus the peakrdl_python hash needs to be used
    inst_type_name = node.inst.original_def.type_name
    if inst_type_name is None:
        inst_type_name = node.inst_name

    if node_hash is None:
        # This is special case where the field has no attributes that need a field definition
        # to be created so it is not included in the list of things to construct, therefore the
        # base classes are directly used
        if not isinstance(node, FieldNode):
            raise TypeError(f'This code should occur for a FieldNode, got {type(node)}')
        return get_base_class_name(node, False)


    if node_hash < 0:
        if (scope_path == '') or (scope_path is None):
            return inst_type_name + '_neg_' + hex(-node_hash) + '_cls'

        return scope_path + '_' + inst_type_name + '_neg_' + hex(-node_hash) + '_cls'

    if (scope_path == '') or (scope_path is None):
        return inst_type_name + '_' + hex(node_hash) + '_cls'

    return scope_path + '_' + inst_type_name + '_' + hex(node_hash) + '_cls'

def get_fully_qualified_type_name(node: Node,
                                  udp_to_include: Optional[list[str]],
                                  hide_node_callback: HideNodeCallback,
                                  include_name_and_desc: bool = True) -> str:
    """
    Returns the fully qualified class type name, i.e. with scope prefix
    """

    node_hash = calculate_node_hash(node=node,
                                    udp_to_include=udp_to_include,
                                    hide_node_callback=hide_node_callback,
                                    include_name_and_desc=include_name_and_desc)

    return get_fully_qualified_type_name_precalculated_hash(
        node=node,
        node_hash=node_hash, )

def fully_qualified_enum_type(field_enum: UserEnumMeta) -> str:
    """
    Returns the fully qualified class type name, for an enum
    """
    return field_enum.get_scope_path('_') + '_' + field_enum.type_name
