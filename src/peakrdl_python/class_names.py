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
from systemrdl.rdltypes.user_enum import UserEnumMeta
from .systemrdl_node_utility_functions import HideNodeCallback

from .systemrdl_node_hashes import node_hash as calculate_node_hash


def get_fully_qualified_type_name(node: Node,
                                  udp_to_include: Optional[list[str]],
                                  hide_node_callback: HideNodeCallback,
                                  include_name_and_desc: bool = True) -> str:
    """
    Returns the fully qualified class type name, i.e. with scope prefix
    """
    scope_path = node.inst.get_scope_path(scope_separator='_')

    # the node.inst.type_name may include a suffix for the reset value, peak_rdl python passes
    # the reset value in when the component is initialised so this is not needed. Therefore,
    # the orginal_def version plus the peakrdl_python hash needs to be used
    inst_type_name = node.inst.original_def.type_name
    if inst_type_name is None:
        inst_type_name = node.inst_name

    node_hash = calculate_node_hash(node=node,
                                    udp_to_include=udp_to_include,
                                    hide_node_callback=hide_node_callback,
                                    include_name_and_desc=include_name_and_desc)

    if node_hash < 0:
        if (scope_path == '') or (scope_path is None):
            return inst_type_name + '_neg_' + hex(-node_hash)

        return scope_path + '_' + inst_type_name + '_neg_' + hex(-node_hash)

    if (scope_path == '') or (scope_path is None):
        return inst_type_name + '_' + hex(node_hash)

    return scope_path + '_' + inst_type_name + '_' + hex(node_hash)

def fully_qualified_enum_type(field_enum: UserEnumMeta) -> str:
    """
    Returns the fully qualified class type name, for an enum
    """
    return field_enum.get_scope_path('_') + '_' + field_enum.type_name