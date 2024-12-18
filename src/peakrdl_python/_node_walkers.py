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

Node walkers to be used in the generated of the output code
"""
from typing import Optional, List, Union, Iterator

from systemrdl import RDLListener, WalkerAction
from systemrdl.node import RegNode, MemNode, FieldNode, AddrmapNode, RegfileNode

from .systemrdl_node_utility_functions import HideNodeCallback


class AddressMaps(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the descendant
    address maps
    """
    def __init__(self, hide_node_callback: HideNodeCallback) -> None:
        super().__init__()
        self.__address_maps: List[AddrmapNode] = []
        self.__hide_node_callback = hide_node_callback

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            return WalkerAction.SkipDescendants

        self.__address_maps.append(node)
        return WalkerAction.Continue

    def __iter__(self) -> Iterator[AddrmapNode]:
        return self.__address_maps.__iter__()


# pylint: disable=too-many-instance-attributes
class OwnedbyAddressMap(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the items owned
    by an address map but not the descendents of any address map
    """
    def __init__(self, hide_node_callback: HideNodeCallback) -> None:
        super().__init__()

        self.registers: List[RegNode] = []
        self.fields: List[FieldNode] = []
        self.memories: List[MemNode] = []
        self.addr_maps: List[AddrmapNode] = []
        self.reg_files: List[RegfileNode] = []
        self._hidden_registers: List[RegNode] = []
        self._hidden_fields: List[FieldNode] = []
        self._hidden_memories: List[MemNode] = []
        self._hidden_addr_maps: List[AddrmapNode] = []
        self._hidden_reg_files: List[RegfileNode] = []
        self.__hide_node_callback = hide_node_callback

    def enter_Reg(self, node: RegNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            self._hidden_registers.append(node)
            return WalkerAction.SkipDescendants

        self.registers.append(node)
        return WalkerAction.Continue

    def enter_Mem(self, node: MemNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            self._hidden_memories.append(node)
            return WalkerAction.SkipDescendants

        self.memories.append(node)
        return WalkerAction.Continue

    def enter_Field(self, node: FieldNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            self._hidden_fields.append(node)
            return WalkerAction.SkipDescendants

        self.fields.append(node)
        return WalkerAction.Continue

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        if not self.__hide_node_callback(node):
            self.addr_maps.append(node)
        else:
            self._hidden_addr_maps.append(node)
        return WalkerAction.SkipDescendants

    def enter_Regfile(self, node: RegfileNode) -> Optional[WalkerAction]:
        if self.__hide_node_callback(node):
            self._hidden_reg_files.append(node)
            return WalkerAction.SkipDescendants

        self.reg_files.append(node)
        return WalkerAction.Continue

    @property
    def nodes(self) -> List[Union[RegNode, MemNode, FieldNode, AddrmapNode, RegfileNode]]:
        """
        All the nodes owned by the address map, including:
        - address maps
        - register files
        - registers
        - memories
        - fields

        Returns: list of nodes

        """
        return self.addr_maps + self.reg_files + self.memories + self.registers + self.fields

    @property
    def hidden_nodes(self) -> List[Union[RegNode, MemNode, FieldNode, AddrmapNode, RegfileNode]]:
        """
        All the 1st tier nodes owned by the address map which are hidden, including:
        - address maps
        - register files
        - registers
        - memories
        - fields

        Returns: list of nodes

        """
        return self._hidden_addr_maps + self._hidden_reg_files + self._hidden_memories + \
               self._hidden_registers + self._hidden_fields

    @property
    def has_hidden_nodes(self) -> bool:
        """
        If there are 1st tier hidden nodes in the address map
        """
        return len(self.hidden_nodes) > 0

    @property
    def addressable_nodes(self) -> List[Union[RegNode, MemNode, AddrmapNode, RegfileNode]]:
        """
        All the nodes owned by the address map, including:
        - address maps
        - register files
        - registers
        - memories

        Returns: list of nodes

        """
        return self.addr_maps + self.reg_files + self.memories + self.registers
# pylint: enable=too-many-instance-attributes
