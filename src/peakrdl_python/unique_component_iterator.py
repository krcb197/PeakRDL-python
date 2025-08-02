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

The methods for building the main iterator that is used in the templates for building the
code.
"""
from typing import Optional
from dataclasses import dataclass, field

from logging import getLogger

from systemrdl.node import Node
from systemrdl.node import RegNode
from systemrdl.node import FieldNode
from systemrdl.node import MemNode
from systemrdl.node import AddrmapNode
from systemrdl.node import RegfileNode
from systemrdl import RDLListener, WalkerAction

from .systemrdl_node_hashes import node_hash
from .systemrdl_node_utility_functions import HideNodeCallback
from .systemrdl_node_utility_functions import get_properties_to_include
from .class_names import get_base_class_name

@dataclass(frozen=True)
class PeakRDLPythonUniqueComponents:
    """
    Dataclass to hold a node that needs to be made into a python class
    """
    instance: Node
    instance_hash: int
    parent_walker: 'UniqueComponents'
    python_class_name: str = field(init=False)
    optimal_python_class_name: bool =  field(init=False)

    def __post_init__(self) -> None:
        python_class_name, optimal_python_class_name = self.__determine_python_class_name()
        object.__setattr__(self, 'python_class_name', python_class_name)
        object.__setattr__(self, 'optimal_python_class_name', optimal_python_class_name)


    def base_class(self, async_library_classes: bool) -> str:
        """
        Return the python base class name from the library to use with the component generated
        in the register model
        """
        return get_base_class_name(node=self.instance,
                                   async_library_classes=async_library_classes)

    @property
    def properties_to_include(self) -> list[str]:
        """
        Provide a list of the User Defined Properties to include in the Register Model for a given
        Node
        """
        return get_properties_to_include(node=self.instance,
                                         udp_to_include=self.parent_walker.udp_to_include)

    def __determine_python_class_name(self) -> tuple[str, bool]:
        """
        Returns the fully qualified class type name with a pre-calculated hash to save time
        """
        scope_path = self.instance.inst.get_scope_path(scope_separator='_')

        # the node.inst.type_name may include a suffix for the reset value, peak_rdl python passes
        # the reset value in when the component is initialised so this is not needed. Therefore,
        # the orginal_def version plus the peakrdl_python hash needs to be used
        if self.instance.inst.original_def is None:
            inst_type_name = self.instance.inst_name
            ideal_class_name = False
        else:
            inbound_inst_type_name = self.instance.inst.original_def.type_name
            ideal_class_name = True
            if inbound_inst_type_name is None:
                inst_type_name = self.instance.inst_name
                ideal_class_name = False
            else:
                inst_type_name = inbound_inst_type_name

        if self.instance_hash < 0:
            if (scope_path == '') or (scope_path is None):
                return (inst_type_name + '_neg_' + hex(-self.instance_hash) + '_cls',
                        ideal_class_name)

            return (scope_path + '_' + inst_type_name + '_neg_' + hex(-self.instance_hash) + '_cls',
                    ideal_class_name)

        if (scope_path == '') or (scope_path is None):
            return (inst_type_name + '_' + hex(self.instance_hash) + '_cls',
                    ideal_class_name)

        return (scope_path + '_' + inst_type_name + '_' + hex(self.instance_hash) + '_cls',
                ideal_class_name)

@dataclass(frozen=True)
class PeakRDLPythonUniqueRegisterComponents(PeakRDLPythonUniqueComponents):
    """
    Dataclass to hold a register node that needs to be made into a python class
    """
    instance: RegNode

    @property
    def read_write(self) -> bool:
        """
        Determine if the register is read-write
        """
        return self.instance.has_sw_readable and self.instance.has_sw_writable

    @property
    def read_only(self) -> bool:
        """
        Determine if the register is read-only
        """
        return self.instance.has_sw_readable and not self.instance.has_sw_writable

    @property
    def write_only(self) -> bool:
        """
        Determine if the register is write-only
        """
        return not self.instance.has_sw_readable and self.instance.has_sw_writable

class UniqueComponents(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the items
    non-hidden nodes
    """

    def __init__(self, hide_node_callback: HideNodeCallback,
                 udp_to_include: Optional[list[str]]) -> None:
        super().__init__()

        self.__hide_node_callback = hide_node_callback
        self.__udp_to_include = udp_to_include
        self.nodes: dict[int, PeakRDLPythonUniqueComponents] = {}
        self.__name_hash_cache: dict[str, Optional[int]] = {}
        self.__logger = getLogger('peakrdl_python.UniqueComponents')

    @property
    def hide_node_callback(self) -> HideNodeCallback:
        """
        Callback to determine if a node is hidden or not
        """
        return self.__hide_node_callback

    @property
    def udp_to_include(self) -> Optional[list[str]]:
        """
        List of user defined properties to include
        """
        return self.__udp_to_include

    def __test_and_add(self, potential_unique_node:PeakRDLPythonUniqueComponents) -> bool:
        """
        Tests whether a unique component is in the set of nodes to generate already and add it
        if it new.

        Args:
            potential_unique_node: A potential component to add

        Returns: True if the component has been added, False if it has not been added (which
                 allows descendants to be skipped

        """
        self.__logger.debug(f'Node under test hash:{potential_unique_node.instance_hash}')

        if potential_unique_node.instance_hash in self.nodes:
            # The node is already in the node set, however, if the new node has a better
            # python class name use the new one
            if self.nodes[potential_unique_node.instance_hash].optimal_python_class_name is False:
                if potential_unique_node.optimal_python_class_name is True:
                    self.nodes[potential_unique_node.instance_hash] = potential_unique_node

            return True

        self.nodes[potential_unique_node.instance_hash] = potential_unique_node
        return False

    def __build_peak_rdl_unique_component(self, node: Node) -> \
            Optional[PeakRDLPythonUniqueComponents]:

        nodal_hash_result = self.__calculate_or_lookup_hash(node)

        if nodal_hash_result is None:
            return None

        if isinstance(node, RegNode):
            return PeakRDLPythonUniqueRegisterComponents(instance=node,
                                                         instance_hash=nodal_hash_result,
                                                         parent_walker=self)
        return PeakRDLPythonUniqueComponents(instance=node,
                                             instance_hash=nodal_hash_result,
                                             parent_walker=self)

    def __enter_non_field_node(self, node: Node) -> Optional[WalkerAction]:
        """
        Handler for all node types other than Field
        """
        full_node_name = '.'.join(node.get_path_segments())
        self.__logger.debug(f'Analysing node:{full_node_name}')

        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        potential_unique_node = self.__build_peak_rdl_unique_component(node)

        if potential_unique_node is None:
            raise RuntimeError('This node type should not have a hash of None')

        if self.__test_and_add(potential_unique_node):
            return WalkerAction.SkipDescendants

        return WalkerAction.Continue

    def enter_Reg(self, node: RegNode) -> Optional[WalkerAction]:
        return self.__enter_non_field_node(node)

    def enter_Mem(self, node: MemNode) -> Optional[WalkerAction]:
        return self.__enter_non_field_node(node)

    def enter_Field(self, node: FieldNode) -> Optional[WalkerAction]:

        full_node_name = '.'.join(node.get_path_segments())
        self.__logger.debug(f'Analysing node:{full_node_name}')

        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        potential_unique_node = self.__build_peak_rdl_unique_component(node)

        if potential_unique_node is None:
            return WalkerAction.SkipDescendants

        if self.__test_and_add(potential_unique_node):
            return WalkerAction.SkipDescendants

        return WalkerAction.Continue

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        return self.__enter_non_field_node(node)

    def enter_Regfile(self, node: RegfileNode) -> Optional[WalkerAction]:
        return self.__enter_non_field_node(node)

    def python_class_name(self, node: Node, async_library_classes: bool) -> str:
        """
        Lookup the python class name to be used for a given node

        Args:
            node: node
            async_library_classes: whether base classes returned are async or not

        Returns: classname as a string

        """
        nodal_hash_result = self.__calculate_or_lookup_hash(node)

        if nodal_hash_result is None:
            # This is special case where the field has no attributes that need a field definition
            # to be created so it is not included in the list of things to construct, therefore the
            # base classes are directly used
            if not isinstance(node, FieldNode):
                raise TypeError(f'This code should occur for a FieldNode, got {type(node)}')
            return get_base_class_name(node,
                                       async_library_classes=async_library_classes)

        if nodal_hash_result not in self.nodes:
            raise RuntimeError(f'The node hash for {node.inst_name} is not in the table')
        python_class_name = self.nodes[nodal_hash_result].python_class_name
        return python_class_name

    def __calculate_or_lookup_hash(self, node: Node) -> Optional[int]:

        full_instance_name = '.'.join(node.get_path_segments())
        if full_instance_name in self.__name_hash_cache:
            return self.__name_hash_cache[full_instance_name]

        nodal_hash_result = node_hash(node=node, udp_to_include=self.udp_to_include,
                                      hide_node_callback=self.hide_node_callback,
                                      include_name_and_desc=True)
        self.__name_hash_cache[full_instance_name] = nodal_hash_result
        return nodal_hash_result
