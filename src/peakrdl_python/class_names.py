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
from systemrdl.node import Node
from systemrdl.node import FieldNode
from systemrdl.node import RegNode
from systemrdl.node import MemNode
from systemrdl.rdltypes.user_enum import UserEnumMeta
from .systemrdl_node_utility_functions import is_encoded_field
from .systemrdl_node_hashes import enum_hash

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

def fully_qualified_enum_type(field_enum: UserEnumMeta) -> str:
    """
    Returns the fully qualified class type name, for an enum
    """
    enum_hash_value = enum_hash(field_enum)
    full_scope_path = field_enum.get_scope_path('_')
    if enum_hash_value < 0:
        return full_scope_path + '_' + field_enum.type_name + '_neg_' + hex(-enum_hash_value)
    return full_scope_path + '_' + field_enum.type_name + hex(enum_hash_value)
