"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

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
from typing import Any, Union, Optional
from enum import Enum, auto
import hashlib
import json

from systemrdl.node import Node
from systemrdl.node import FieldNode
from systemrdl.node import RegNode
from systemrdl.node import RegfileNode
from systemrdl.node import AddrmapNode
from systemrdl.node import MemNode
from systemrdl.node import SignalNode
from systemrdl.rdltypes.user_enum import UserEnumMeta, UserEnum
from systemrdl.rdltypes import AccessType

from .systemrdl_node_utility_functions import get_properties_to_include
from .systemrdl_node_utility_functions import HideNodeCallback
from .systemrdl_node_utility_functions import ShowUDPCallback
from .systemrdl_node_utility_functions import get_field_default_value
from .systemrdl_node_utility_functions import get_reg_regwidth
from .systemrdl_node_utility_functions import get_reg_accesswidth
from .systemrdl_node_utility_functions import get_memory_accesswidth

class NodeHashingMethod(Enum):
    """
    Enumeration for the different hashing methods supported by this module
    """
    PYTHONHASH = auto()   # Hash nodes based on the built-in python ``hash`` function
    SHA256 = auto()   # Hash nodes based on the ```hashlib.sha256`` algorithm

def __enum_entry_content(entry: UserEnum,
                         include_name_and_desc: bool) -> dict[str, Union[str, int]]:

    value = entry.value
    if not isinstance(value, int):
        raise TypeError(f'value type should be int but got: {type(value)}')

    name = entry.name
    if not isinstance(name, str):
        raise TypeError(f'value type should be str but got: {type(name)}')

    return_dict: dict[str, Union[str, int]] = {
        'value': value,
        'name': name,
    }
    if include_name_and_desc:
        rdl_desc = entry.rdl_desc
        if rdl_desc is not None:
            if not isinstance(rdl_desc, str):
                raise TypeError(f'rdl_desc type should be str but got: {type(rdl_desc)}')
            return_dict['rdl_desc'] = rdl_desc
        rdl_name = entry.rdl_name
        if rdl_name is not None:
            if not isinstance(rdl_name, str):
                raise TypeError(f'rdl_name type should be str but got: {type(rdl_name)}')
            return_dict['rdl_name'] = rdl_name

    return return_dict


def _make_hashable(obj: Any,
                   include_name_and_desc: bool) -> Any:
    """
    Recursively convert objects to a JSON-serializable and deterministic structure for hashing.
    """
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    if isinstance(obj, (list, tuple)):
        return [_make_hashable(i, include_name_and_desc) for i in obj]

    if isinstance(obj, dict):
        # Ensure keys are sorted for determinism
        return {str(k): _make_hashable(obj[k], include_name_and_desc) for k in sorted(obj.keys())}

    if isinstance(obj, UserEnumMeta):
        # Use the enum's fully qualified name and items for deterministic hash
        return [__enum_entry_content(item, include_name_and_desc) for item in obj]

    if isinstance(obj, AccessType):
        # Use the name for determinism
        return str(obj)

    # Fallback: use the string representation
    return str(obj)


def _hash_content_sha256(content: tuple[Any],
                         include_name_and_desc: bool) -> int:
    """
    Deterministically hash a list of content using SHA256 and return an integer.
    """
    hashable_content = _make_hashable(content,
                                      include_name_and_desc=include_name_and_desc)
    json_str = json.dumps(hashable_content, sort_keys=True, separators=(',', ':'))
    sha = hashlib.sha256(json_str.encode('utf-8'), usedforsecurity=False).hexdigest()
    # Use int value of the first 16 bytes of SHA256 for a hash-like value
    return int(sha[:16], 16)

def enum_hash(enum: UserEnumMeta,
              include_name_and_desc: bool,
              method: NodeHashingMethod,
              ) -> int:
    """
    Calculate the hash of a system RDL enum type
    """
    data = [__enum_entry_content(item, include_name_and_desc) for item in enum]
    json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))

    if method is NodeHashingMethod.PYTHONHASH:
        return hash(json_str)

    if method is NodeHashingMethod.SHA256:
        # Deterministically hash the enum by its name and members
        sha = hashlib.sha256(json_str.encode('utf-8'), usedforsecurity=False).hexdigest()
        return int(sha[:16], 16)

    raise ValueError(f'Unsupported method: {method}')

def __node_hash_components(node: Node,
                           udp_include_func: ShowUDPCallback,
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

    for udp in get_properties_to_include(node, udp_include_func):
        value_to_hash.append(node.get_property(udp))

    return value_to_hash


def __field_hash(node: FieldNode,
                 udp_include_func: ShowUDPCallback,
                 include_name_and_desc: bool,
                 method: NodeHashingMethod) -> list[Any]:
    """
    Determine the hash for a node instance, which can be used to determine if it needs a unique
    class definition in the generated code or not.

    If the node has no attributes that extend beyond the base classes, this hash will return as
    None
    """
    if not isinstance(node, FieldNode):
        raise TypeError(f'{node} is not a FieldNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_include_func=udp_include_func,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.get_property('sw'))

    if 'encode' in node.list_properties():
        # determine the fully qualified enum name, using the same method as the one that
        # decides whether a enum class is needed or not
        field_enum = node.get_property('encode')
        if field_enum is None:
            raise RuntimeError('The field_enum should not None it is an encoded field')
        value_to_hash.append(enum_hash(field_enum, method=method,
                                       include_name_and_desc=include_name_and_desc))

    return value_to_hash


def __reg_hash(node: RegNode,
               udp_include_func: ShowUDPCallback,
               hide_node_callback: HideNodeCallback,
               include_name_and_desc: bool,
               method: NodeHashingMethod) -> list[Any]:
    """
    Provide a list of things to hash for a reg class definition
    """
    if not isinstance(node, RegNode):
        raise TypeError(f'{node} is not a RegNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_include_func=udp_include_func,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.has_sw_readable)
    value_to_hash.append(node.has_sw_writable)

    value_to_hash.append(get_reg_accesswidth(node))
    value_to_hash.append(get_reg_regwidth(node))

    value_to_hash.append(node.is_array)

    for field in node.fields():
        if not hide_node_callback(field):
            value_to_hash += __field_hash(node=field, udp_include_func=udp_include_func,
                                          include_name_and_desc=include_name_and_desc,
                                          method=method)
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
                        udp_include_func: ShowUDPCallback,
                        hide_node_callback: HideNodeCallback,
                        include_name_and_desc: bool,
                        method: NodeHashingMethod) -> list[Any]:
    """
    Provide a list of things to hash for a reg instance (note this include everything from the
    class definition)
    """
    if not isinstance(node, RegNode):
        raise TypeError(f'{node} is not a RegNode, got {type(node)}')

    value_to_hash = __reg_hash(node=node, udp_include_func=udp_include_func,
                               hide_node_callback=hide_node_callback,
                               include_name_and_desc=include_name_and_desc,
                               method=method)
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
                            udp_include_func: ShowUDPCallback,
                            hide_node_callback: HideNodeCallback,
                            include_name_and_desc: bool,
                            method: NodeHashingMethod) -> list[Any]:
    """
    Provide a list of things to hash for a regfile instance (note this include everything from the
    class definition)
    """
    if not isinstance(node, RegfileNode):
        raise TypeError(f'{node} is not a RegfileNode, got {type(node)}')

    value_to_hash = __regfile_hash(node=node, udp_include_func=udp_include_func,
                                   hide_node_callback=hide_node_callback,
                                   include_name_and_desc=include_name_and_desc,
                                   method=method)
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
                            udp_include_func: ShowUDPCallback,
                            hide_node_callback: HideNodeCallback,
                            include_name_and_desc: bool,
                            method: NodeHashingMethod) -> list[Any]:
    """
    Provide a list of things to hash for an address map instance (note this include everything
    from the class definition
    """
    if not isinstance(node, AddrmapNode):
        raise TypeError(f'{node} is not a AddrmapNode, got {type(node)}')

    value_to_hash = __addrmap_hash(node=node, udp_include_func=udp_include_func,
                                   hide_node_callback=hide_node_callback,
                                   include_name_and_desc=include_name_and_desc, method=method)
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
                   udp_include_func: ShowUDPCallback,
                   hide_node_callback: HideNodeCallback,
                   include_name_and_desc: bool,
                   method: NodeHashingMethod) -> list[Any]:
    if not isinstance(node, AddrmapNode):
        raise TypeError(f'{node} is not a AddrmapNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_include_func=udp_include_func,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.is_array)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(child, RegNode):
                value_to_hash += __reg_instance_hash(
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method)
            elif isinstance(child, RegfileNode):
                value_to_hash += __regfile_instance_hash(
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method)
            elif isinstance(child, MemNode):
                value_to_hash += __mem_instance_hash(
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method)
            elif isinstance(child, AddrmapNode):
                value_to_hash += __addrmap_instance_hash(
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method)
            elif isinstance(child, SignalNode):
                pass
            else:
                raise TypeError(f'Unhandled child type, {type(child)}')

    return value_to_hash


def __regfile_hash(node: RegfileNode,
                   udp_include_func: ShowUDPCallback,
                   hide_node_callback: HideNodeCallback,
                   include_name_and_desc: bool,
                   method: NodeHashingMethod) -> list[Any]:
    if not isinstance(node, RegfileNode):
        raise TypeError(f'{node} is not a RegfileNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_include_func=udp_include_func,
                                           include_name_and_desc=include_name_and_desc)

    value_to_hash.append(node.is_array)

    for child in node.children(unroll=True):
        if not hide_node_callback(child):
            if isinstance(child, RegNode):
                value_to_hash += __reg_instance_hash(
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method
                )
            elif isinstance(child, RegfileNode):
                value_to_hash += __regfile_instance_hash(
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method)
            elif isinstance(child, SignalNode):
                pass
            else:
                raise TypeError(f'Unhandled child type, {type(child)}')

    return value_to_hash


def __mem_hash(node: MemNode,
               udp_include_func: ShowUDPCallback,
               hide_node_callback: HideNodeCallback,
               include_name_and_desc: bool,
               method: NodeHashingMethod) -> list[Any]:
    if not isinstance(node, MemNode):
        raise TypeError(f'{node} is not a MemNode, got {type(node)}')

    value_to_hash = __node_hash_components(node=node,
                                           udp_include_func=udp_include_func,
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
                    node=child, udp_include_func=udp_include_func,
                    hide_node_callback=hide_node_callback,
                    include_name_and_desc=include_name_and_desc,
                    method=method)
            elif isinstance(child, SignalNode):
                pass
            else:
                raise TypeError(f'Unhandled child type, {type(child)}')

    return value_to_hash


def __mem_instance_hash(node: MemNode,
                        udp_include_func: ShowUDPCallback,
                        hide_node_callback: HideNodeCallback,
                        include_name_and_desc: bool,
                        method: NodeHashingMethod) -> list[Any]:
    """
    Provide a list of things to hash for a memory instance (note this include everything from the
    class definition)
    """
    if not isinstance(node, MemNode):
        raise TypeError(f'{node} is not a MemNode, got {type(node)}')

    value_to_hash = __mem_hash(node=node, udp_include_func=udp_include_func,
                               hide_node_callback=hide_node_callback,
                               include_name_and_desc=include_name_and_desc,
                               method=method)
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
              udp_include_func: ShowUDPCallback,
              hide_node_callback: HideNodeCallback,
              include_name_and_desc: bool,
              method: NodeHashingMethod
              ) -> Optional[int]:
    """
    Calculate the PeakRDL python has for node. This is used it determine whether a unique
    class definition is needed or not in the generated register model code or not

    Args:
        node:
        udp_include_func: a Callback function that determines whether to include a UDP ot not
        hide_node_callback: Call back to determine if a node (and its descendants) are included in
                            the hash calculation or not
        include_name_and_desc: Set to True to include the system RDL name and description in the
                               hash or not
        method: Method to calculate hashes

    Returns: A integer hash value, or None in the special case where the base class can be used
             directly from the library

    """
    if isinstance(node, FieldNode):
        hash_content = __field_hash(node=node, udp_include_func=udp_include_func,
                                    include_name_and_desc=include_name_and_desc,
                                    method=method)
        # This is a special case, if there is a two entry for type and access type, then there is
        # no need to make a special class, it is permitted to use the base classes from the
        # library
        if len(hash_content) == 2:
            if (isinstance(hash_content[0], str) and
                    hash_content[0] == 'Field' and
                    isinstance(hash_content[1], AccessType)):
                return None
            raise TypeError(f'Unexpected content in the hash_content, {type(hash_content[0])}')

    elif isinstance(node, RegNode):
        hash_content = __reg_hash(node=node, udp_include_func=udp_include_func,
                                  hide_node_callback=hide_node_callback,
                                  include_name_and_desc=include_name_and_desc,
                                  method=method)
    elif isinstance(node, AddrmapNode):
        hash_content = __addrmap_hash(node=node, udp_include_func=udp_include_func,
                                      hide_node_callback=hide_node_callback,
                                      include_name_and_desc=include_name_and_desc,
                                      method=method)
    elif isinstance(node, RegfileNode):
        hash_content = __regfile_hash(node=node, udp_include_func=udp_include_func,
                                      hide_node_callback=hide_node_callback,
                                      include_name_and_desc=include_name_and_desc,
                                      method=method)
    elif isinstance(node, MemNode):
        hash_content = __mem_hash(node=node, udp_include_func=udp_include_func,
                                  hide_node_callback=hide_node_callback,
                                  include_name_and_desc=include_name_and_desc,
                                  method=method)
    else:
        raise TypeError(f'Unhandled Node:{type(node)}')

    if method is NodeHashingMethod.PYTHONHASH:
        return hash(tuple(hash_content))

    if method is NodeHashingMethod.SHA256:
        return _hash_content_sha256(tuple(hash_content),
                                    include_name_and_desc=include_name_and_desc)

    raise ValueError(f'Unsupported method: {method}')
