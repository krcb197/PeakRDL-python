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
from systemrdl.node import AddrmapNode
from systemrdl.node import RegfileNode
from systemrdl.rdltypes.user_enum import UserEnumMeta
from systemrdl.rdltypes import AccessType

from .systemrdl_node_utility_functions import get_properties_to_include
from .systemrdl_node_utility_functions import HideNodeCallback
from .systemrdl_node_utility_functions import get_field_default_value

def enum_hash(enum: UserEnumMeta):

    return hash(enum)


def __node_hash_components(node: Node,
                           udp_to_include: Optional[list[str]],
                           include_name_and_desc: bool = True) -> list[Any]:
    value_to_hash = []
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
        value_to_hash.append(enum_hash(node.get_property('encode')))

    return value_to_hash


def __reg_hash(node: RegNode,
               udp_to_include: Optional[list[str]],
               hide_node_callback: HideNodeCallback,
               include_name_and_desc: bool = True) -> list[Any]:
    if not isinstance(node, RegNode):
        raise TypeError(f'{node} is not a RegNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

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

def __addrmap_node_hash(node: AddrmapNode,
                        udp_to_include: Optional[list[str]],
                        hide_node_callback: HideNodeCallback,
                        include_name_and_desc: bool = True) -> list[Any]:
    if not isinstance(node, AddrmapNode):
        raise TypeError(f'{node} is not a AddrmapNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(node, RegNode):
                value_to_hash += __reg_hash(node=child, udp_to_include=udp_to_include,
                                            include_name_and_desc=include_name_and_desc)

    return value_to_hash

def __regfile_node_hash(node: RegNode,
                        udp_to_include: Optional[list[str]],
                        hide_node_callback: HideNodeCallback,
                        include_name_and_desc: bool = True) -> list[Any]:
    if not isinstance(node, RegfileNode):
        raise TypeError(f'{node} is not a RegfileNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_to_include=udp_to_include,
                                           include_name_and_desc=include_name_and_desc)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(node, RegNode):
                value_to_hash += __reg_hash(node=child, udp_to_include=udp_to_include,
                                            include_name_and_desc=include_name_and_desc)

    return value_to_hash

def node_hash(node: Node,
              udp_to_include: Optional[list[str]],
              hide_node_callback: HideNodeCallback,
              include_name_and_desc: bool = True) -> Optional[int]:

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
        hash_content = __addrmap_node_hash(node=node, udp_to_include=udp_to_include,
                                           hide_node_callback=hide_node_callback,
                                           include_name_and_desc=include_name_and_desc)
    elif isinstance(node, RegfileNode):
        hash_content = __regfile_node_hash(node=node, udp_to_include=udp_to_include,
                                           hide_node_callback=hide_node_callback,
                                           include_name_and_desc=include_name_and_desc)
    else:
        raise TypeError(f'Unhandled Node:{type(node)}')



    return hash( tuple(hash_content) )
