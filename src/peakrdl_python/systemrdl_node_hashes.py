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

A set of utility functions that determine the class hash, for a systemRDL node.

This can be used to determine if it needs a unique class definition in the generated python or
not
"""
from typing import Optional, Any
from systemrdl.node import Node
from systemrdl.node import FieldNode
from systemrdl.node import RegNode
from systemrdl.node import RegfileNode
from systemrdl.node import AddrmapNode
from systemrdl.node import MemNode
from systemrdl.node import SignalNode
from systemrdl.rdltypes.user_enum import UserEnumMeta
from systemrdl.rdltypes import AccessType

from .systemrdl_node_utility_functions import get_properties_to_include
from .systemrdl_node_utility_functions import HideNodeCallback
from .systemrdl_node_utility_functions import get_field_default_value
from .systemrdl_node_utility_functions import get_reg_regwidth
from .systemrdl_node_utility_functions import get_reg_accesswidth
from .systemrdl_node_utility_functions import get_memory_accesswidth


def enum_hash(enum: UserEnumMeta) -> int:
    """
    Calculate the hash of a system RDL enum type
    """
    return hash(enum)


def __node_hash_components(node: Node,
                           udp_to_include: Optional[list[str]],
                           include_name_and_desc: bool = True) -> list[Any]:

    value_to_hash = []

    if isinstance(node, FieldNode):
        value_to_hash.append('Field')
    elif isinstance(node, RegNode):
        value_to_hash.append('Register')
    elif isinstance(node, RegfileNode):
        value_to_hash.append('Register File')
    elif isinstance(node, AddrmapNode):
        value_to_hash.append('Address Map')
    elif isinstance(node, MemNode):
        value_to_hash.append('Memory')
    else:
        raise TypeError(f'Unhandled node type: {type(node)}')


    if include_name_and_desc:
        name = node.get_property('name', default=None)
        if name is not None:
            value_to_hash.append(name)
        desc = node.get_property('desc', default=None)
        if desc is not None:
            value_to_hash.append(desc)

    for udp in get_properties_to_include(node, udp_to_include):
        value_to_hash.append(node.get_property(udp))

    return value_to_hash


def __field_hash(node: FieldNode,
                 udp_to_include: Optional[list[str]],
                 include_name_and_desc: bool = True) -> list[Any]:
    """
    Determine the hash for a node instance, which can be used to determine if it needs a unique
    class definition in the generated code or not.

    If the node has no attributes that extend beyond the base classes, this hash will return as
    None
    """
    if not isinstance(node, FieldNode):
        raise TypeError(f'{node} is not a FieldNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.get_property('sw'))

    if 'encode' in node.list_properties():
        # determine the fully qualified enum name, using the same method as the one that
        # decides whether a enum class is needed or not
        field_enum = node.get_property('encode')
        if field_enum is None:
            raise RuntimeError('The field_enum should not None it is an encoded field')
        value_to_hash.append(enum_hash(field_enum))

    return value_to_hash


def __reg_hash(node: RegNode,
               udp_to_include: Optional[list[str]],
               hide_node_callback: HideNodeCallback,
               include_name_and_desc: bool = True) -> list[Any]:
    """
    Provide a list of things to hash for a reg class definition
    """
    if not isinstance(node, RegNode):
        raise TypeError(f'{node} is not a RegNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.has_sw_readable)
    value_to_hash.append(node.has_sw_writable)

    value_to_hash.append(get_reg_accesswidth(node))
    value_to_hash.append(get_reg_regwidth(node))

    value_to_hash.append(node.is_array)

    for field in node.fields():
        if not hide_node_callback(field):
            value_to_hash += __field_hash(node=field, udp_to_include=udp_to_include,
                                          include_name_and_desc=include_name_and_desc)
            value_to_hash.append(field.lsb)
            value_to_hash.append(field.msb)
            value_to_hash.append(field.low)
            value_to_hash.append(field.high)
            value_to_hash.append(get_field_default_value(field))
            value_to_hash.append(field.is_hw_writable)
            value_to_hash.append(field.inst_name)
            # no need to include the enum class as that is already included

    return value_to_hash

def __reg_instance_hash(node: RegNode,
                        udp_to_include: Optional[list[str]],
                        hide_node_callback: HideNodeCallback,
                        include_name_and_desc: bool = True) -> list[Any]:
    """
    Provide a list of things to hash for a reg instance (note this include everything from the
    class definition)
    """
    if not isinstance(node, RegNode):
        raise TypeError(f'{node} is not a RegNode, got {type(node)}')

    value_to_hash = __reg_hash(node=node, udp_to_include=udp_to_include,
                               hide_node_callback=hide_node_callback,
                               include_name_and_desc=include_name_and_desc)
    value_to_hash.append(node.inst_name)
    if node.is_array:
        value_to_hash.append(node.array_stride)
        array_dimensions = node.array_dimensions
        if array_dimensions is None:
            raise RuntimeError('The Array Dimensions must be present')
        value_to_hash.append(tuple(array_dimensions))
        value_to_hash.append(node.raw_address_offset)
    else:
        value_to_hash.append(node.address_offset)

    return value_to_hash


def __regfile_instance_hash(node: RegfileNode,
                            udp_to_include: Optional[list[str]],
                            hide_node_callback: HideNodeCallback,
                            include_name_and_desc: bool = True) -> list[Any]:
    """
    Provide a list of things to hash for a regfile instance (note this include everything from the
    class definition)
    """
    if not isinstance(node, RegfileNode):
        raise TypeError(f'{node} is not a RegfileNode, got {type(node)}')

    value_to_hash = __regfile_hash(node=node, udp_to_include=udp_to_include,
                                   hide_node_callback=hide_node_callback,
                                   include_name_and_desc=include_name_and_desc)
    value_to_hash.append(node.inst_name)
    if node.is_array:
        value_to_hash.append(node.array_stride)
        array_dimensions = node.array_dimensions
        if array_dimensions is None:
            raise RuntimeError('The Array Dimensions must be present')
        value_to_hash.append(tuple(array_dimensions))
        value_to_hash.append(node.raw_address_offset)
    else:
        value_to_hash.append(node.address_offset)

    return value_to_hash


def __addrmap_instance_hash(node: AddrmapNode,
                            udp_to_include: Optional[list[str]],
                            hide_node_callback: HideNodeCallback,
                            include_name_and_desc: bool = True) -> list[Any]:
    """
    Provide a list of things to hash for an address map instance (note this include everything
    from the class definition
    """
    if not isinstance(node, AddrmapNode):
        raise TypeError(f'{node} is not a AddrmapNode, got {type(node)}')

    value_to_hash = __addrmap_hash(node=node, udp_to_include=udp_to_include,
                                   hide_node_callback=hide_node_callback,
                                   include_name_and_desc=include_name_and_desc)
    value_to_hash.append(node.inst_name)
    if node.is_array:
        value_to_hash.append(node.array_stride)
        array_dimensions = node.array_dimensions
        if array_dimensions is None:
            raise RuntimeError('The Array Dimensions must be present')
        value_to_hash.append(tuple(array_dimensions))
        value_to_hash.append(node.raw_address_offset)
    else:
        value_to_hash.append(node.address_offset)

    return value_to_hash


def __addrmap_hash(node: AddrmapNode,
                   udp_to_include: Optional[list[str]],
                   hide_node_callback: HideNodeCallback,
                   include_name_and_desc: bool = True) -> list[Any]:
    if not isinstance(node, AddrmapNode):
        raise TypeError(f'{node} is not a AddrmapNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.is_array)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(child, RegNode):
                value_to_hash += __reg_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, RegfileNode):
                value_to_hash += __regfile_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, MemNode):
                value_to_hash += __mem_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, AddrmapNode):
                value_to_hash += __addrmap_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, SignalNode):
                pass
            else:
                raise TypeError(f'Unhandled child type, {type(child)}')

    return value_to_hash


def __regfile_hash(node: RegfileNode,
                   udp_to_include: Optional[list[str]],
                   hide_node_callback: HideNodeCallback,
                   include_name_and_desc: bool = True) -> list[Any]:
    if not isinstance(node, RegfileNode):
        raise TypeError(f'{node} is not a RegfileNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.is_array)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(child, RegNode):
                value_to_hash += __reg_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, RegfileNode):
                value_to_hash += __regfile_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, SignalNode):
                pass
            else:
                raise TypeError(f'Unhandled child type, {type(child)}')

    return value_to_hash


def __mem_hash(node: MemNode,
               udp_to_include: Optional[list[str]],
               hide_node_callback: HideNodeCallback,
               include_name_and_desc: bool = True) -> list[Any]:
    if not isinstance(node, MemNode):
        raise TypeError(f'{node} is not a MemNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.is_sw_readable)
    value_to_hash.append(node.is_sw_writable)

    value_to_hash.append(node.get_property('mementries'))
    value_to_hash.append(get_memory_accesswidth(node))
    value_to_hash.append(node.get_property('memwidth'))

    value_to_hash.append(node.is_array)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(child, RegNode):
                value_to_hash += __reg_instance_hash(
                    node=child, udp_to_include=udp_to_include,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc)
            elif isinstance(child, SignalNode):
                pass
            else:
                raise TypeError(f'Unhandled child type, {type(child)}')

    return value_to_hash


def __mem_instance_hash(node: MemNode,
                        udp_to_include: Optional[list[str]],
                        hide_node_callback: HideNodeCallback,
                        include_name_and_desc: bool = True) -> list[Any]:
    """
    Provide a list of things to hash for a memory instance (note this include everything from the
    class definition)
    """
    if not isinstance(node, MemNode):
        raise TypeError(f'{node} is not a MemNode, got {type(node)}')

    value_to_hash = __mem_hash(node=node, udp_to_include=udp_to_include,
                               hide_node_callback=hide_node_callback,
                               include_name_and_desc=include_name_and_desc)
    value_to_hash.append(node.inst_name)
    if node.is_array:
        value_to_hash.append(node.array_stride)
        array_dimensions = node.array_dimensions
        if array_dimensions is None:
            raise RuntimeError('The Array Dimensions must be present')
        value_to_hash.append(tuple(array_dimensions))
        value_to_hash.append(node.raw_address_offset)
    else:
        value_to_hash.append(node.address_offset)

    return value_to_hash


def node_hash(node: Node,
              udp_to_include: Optional[list[str]],
              hide_node_callback: HideNodeCallback,
              include_name_and_desc: bool = True) -> Optional[int]:
    """
    Calculate the PeakRDL python has for node. This is used it determine whether a unique
    class definition is needed or not in the generated register model code or not

    Args:
        node:
        udp_to_include: List of User Defined Properties to consider in the hash calculation
        hide_node_callback: Call back to determine if a node (and its descendants) are included in
                            the hash calculation or not
        include_name_and_desc: Set to True to include the system RDL name and description in the
                               hash or not

    Returns: A integer hash value, or None in the special case where the base class can be used
             directly from the library

    """
    if isinstance(node, FieldNode):
        hash_content = __field_hash(node=node, udp_to_include=udp_to_include,
                                    include_name_and_desc=include_name_and_desc)
        # This is a special case, if there is a single entry for access type, then there is no
        # need to make a special class, it is permitted to use the base classes from the
        # library
        if len(hash_content) == 1:
            if isinstance(hash_content[0], AccessType):
                return None
            raise TypeError(f'Unexpected content in the hash_content, {type(hash_content[0])}')

    elif isinstance(node, RegNode):
        hash_content = __reg_hash(node=node, udp_to_include=udp_to_include,
                                  hide_node_callback=hide_node_callback,
                                  include_name_and_desc=include_name_and_desc)
    elif isinstance(node, AddrmapNode):
        hash_content = __addrmap_hash(node=node, udp_to_include=udp_to_include,
                                      hide_node_callback=hide_node_callback,
                                      include_name_and_desc=include_name_and_desc)
    elif isinstance(node, RegfileNode):
        hash_content = __regfile_hash(node=node, udp_to_include=udp_to_include,
                                      hide_node_callback=hide_node_callback,
                                      include_name_and_desc=include_name_and_desc)
    elif isinstance(node, MemNode):
        hash_content = __mem_hash(node=node, udp_to_include=udp_to_include,
                                  hide_node_callback=hide_node_callback,
                                  include_name_and_desc=include_name_and_desc)
    else:
        raise TypeError(f'Unhandled Node:{type(node)}')

    return hash(tuple(hash_content))
