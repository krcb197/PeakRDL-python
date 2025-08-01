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
from typing import Optional, Union, TYPE_CHECKING
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
import sys
from logging import getLogger

from systemrdl.node import Node
from systemrdl.node import RegNode
from systemrdl.node import RootNode
from systemrdl.node import AddressableNode
from systemrdl.node import FieldNode
from systemrdl.node import MemNode
from systemrdl.node import AddrmapNode
from systemrdl.node import RegfileNode
from systemrdl import RDLListener, WalkerAction, RDLWalker

from .systemrdl_node_hashes import node_hash
from .systemrdl_node_utility_functions import HideNodeCallback
from .systemrdl_node_utility_functions import get_properties_to_include
from .class_names import get_fully_qualified_type_name_precalculated_hash
from .class_names import get_base_class_name

# pylint: disable=duplicate-code
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# pylint: enable=duplicate-code

@dataclass(frozen=True)
class PeakRDLPythonUniqueComponents:
    """
    Dataclass to hold a node that needs to be made into a python class
    """
    instance: Node
    udp_to_include: Optional[list[str]]
    hide_node_callback: HideNodeCallback

    @cached_property
    def fully_qualified_type_name(self) -> str:
        """
        Return the python class name to use with the component generated in the register model
        """
        return get_fully_qualified_type_name_precalculated_hash(
            node=self.instance,
            node_hash=self.__system_rdl_type_hash)

    def base_class(self, async_library_classes: bool) -> str:
        """
        Return the python base class name from the library to use with the component generated
        in the register model
        """
        return get_base_class_name(node=self.instance,
                                   async_library_classes=async_library_classes)

    @cached_property
    def __system_rdl_type_hash(self) -> int:
        nodal_hash_result = node_hash(node=self.instance, udp_to_include=self.udp_to_include,
                  hide_node_callback=self.hide_node_callback,
                  include_name_and_desc=True)
        if nodal_hash_result is None:
            # The hash of None is a special case where the Field can just use the baseclass,
            # therefore should not have an UniqueComponent Entry
            raise RuntimeError('hash is None')
        return nodal_hash_result

    @property
    def properties_to_include(self) -> list[str]:
        """
        Provide a list of the User Defined Properties to include in the Register Model for a given
        Node
        """
        return get_properties_to_include(node=self.instance,
                                         udp_to_include=self.udp_to_include)

    def __hash__(self) -> int:
        return self.__system_rdl_type_hash

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, PeakRDLPythonUniqueComponents):
            raise TypeError('Comparison failed')

        return hash(self) == hash(other)

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

    def __hash__(self) -> int:
        return super().__hash__()

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
        self.nodes: list[PeakRDLPythonUniqueComponents] = []
        self.__logger = getLogger('peakrdl_python.UniqueComponents')

    def __is_equivalent_node_in_list(self, node:Node) -> bool:

        provide_node = self.__build_peak_rdl_unique_component(node)
        node_to_tested_hash = hash(provide_node)
        self.__logger.debug(f'Node under test hash:{node_to_tested_hash}')

        for node_to_test in self.nodes:
            if provide_node == node_to_test:
                if provide_node.fully_qualified_type_name != node_to_test.fully_qualified_type_name:
                    raise RuntimeError(f'The fully qualified class names for items with matching '
                                       f'hashes should also match')
                return True

        return False

    def __build_peak_rdl_unique_component(self, node: Node) -> PeakRDLPythonUniqueComponents:
        return PeakRDLPythonUniqueComponents(instance=node,
                                             hide_node_callback=self.__hide_node_callback,
                                             udp_to_include=self.__udp_to_include)

    def __add_node_to_list(self, node: Node) -> None:

        self.nodes.append(self.__build_peak_rdl_unique_component(node))

    def __add_reg_node_to_list(self, node: RegNode) -> None:

        self.nodes.append(PeakRDLPythonUniqueRegisterComponents(
            instance=node,
            hide_node_callback=self.__hide_node_callback,
            udp_to_include=self.__udp_to_include))

    def enter_Reg(self, node: RegNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        if self.__is_equivalent_node_in_list(node):
            return WalkerAction.SkipDescendants

        self.__add_reg_node_to_list(node)
        return WalkerAction.Continue

    def enter_Mem(self, node: MemNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        if self.__is_equivalent_node_in_list(node):
            return WalkerAction.SkipDescendants

        self.__add_node_to_list(node)
        return WalkerAction.Continue

    def enter_Field(self, node: FieldNode) -> Optional[WalkerAction]:

        full_node_name = '.'.join(node.get_path_segments())
        self.__logger.debug(f'Analysing Field:{full_node_name}')

        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        if node_hash(node=node, udp_to_include=self.__udp_to_include,
                     hide_node_callback=self.__hide_node_callback,
                     include_name_and_desc=True) is None:
            # This is special case where the field has no attributes that need a field definition
            # to be created so it is not included in the list of things to construct
            return WalkerAction.SkipDescendants

        if self.__is_equivalent_node_in_list(node):
            return WalkerAction.SkipDescendants

        self.__add_node_to_list(node)
        return WalkerAction.Continue

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        if self.__is_equivalent_node_in_list(node):
            return WalkerAction.SkipDescendants

        self.__add_node_to_list(node)
        return WalkerAction.Continue

    def enter_Regfile(self, node: RegfileNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        if self.__is_equivalent_node_in_list(node):
            return WalkerAction.SkipDescendants

        self.__add_node_to_list(node)
        return WalkerAction.Continue

def get_dependent_component(node: Union[AddressableNode, RootNode],
                            hide_node_callback: HideNodeCallback,
                            udp_to_include: Optional[list[str]]) -> \
        Iterable[PeakRDLPythonUniqueComponents]:
    """
    iterable of nodes that have a component which is used by a
    descendant, this list is de-duplicated and reversed to components
    are declared before their parents who use them

    Args:
        node: node to be analysed
        hide_node_callback: callback to determine if the node should be hidden
    """
    unique_component_walker = UniqueComponents(hide_node_callback=hide_node_callback,
                                               udp_to_include=udp_to_include)
    # running the walker populated the blocks with all the address maps in within the
    # top block, including the top_block itself
    RDLWalker(unroll=True).walk(node, unique_component_walker, skip_top=False)

    return reversed(unique_component_walker.nodes)
