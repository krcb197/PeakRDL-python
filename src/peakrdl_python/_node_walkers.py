"""
Node walkers to be used in the generated of the output code
"""
from typing import Optional, List, Union, Iterator

from systemrdl import RDLListener, WalkerAction # type: ignore
from systemrdl.node import RegNode, MemNode, FieldNode, AddrmapNode, RegfileNode # type: ignore


class AddressMaps(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the desendent
    address maps
    """
    def __init__(self) -> None:
        super().__init__()
        self.__address_maps: List[AddrmapNode] = []

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        self.__address_maps.append(node)
        return WalkerAction.Continue

    def __iter__(self) -> Iterator[AddrmapNode]:
        return self.__address_maps.__iter__()


class OwnedbyAddressMap(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the items owned
    by an address map but not the descendents of any address map
    """
    def __init__(self) -> None:
        super().__init__()

        self.registers: List[RegNode] = []
        self.fields: List[RegNode] = []
        self.memories: List[RegNode] = []
        self.addr_maps: List[AddrmapNode] = []
        self.reg_files: List[RegfileNode] = []

    def enter_Reg(self, node: RegNode) -> Optional[WalkerAction]:
        self.registers.append(node)
        return WalkerAction.Continue

    def enter_Mem(self, node: MemNode) -> Optional[WalkerAction]:
        self.memories.append(node)
        return WalkerAction.Continue

    def enter_Field(self, node: FieldNode) -> Optional[WalkerAction]:
        self.fields.append(node)
        return WalkerAction.Continue

    def enter_Addrmap(self, node: AddrmapNode) -> Optional[WalkerAction]:
        self.addr_maps.append(node)
        return WalkerAction.SkipDescendants

    def enter_Regfile(self, node: RegfileNode) -> Optional[WalkerAction]:
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

    @property
    def n_dimesional_array_nodes(self) -> List[Union[RegNode, MemNode, AddrmapNode, RegfileNode]]:
        """
        All the nodes owned by the address map which are arrays with more than 1 dimension,
        including:
        - address maps
        - register files
        - registers
        - memories

        Returns: list of nodes
        """
        def n_dimensional_node(node: Union[RegNode, MemNode, AddrmapNode, RegfileNode]) -> bool:
            return node.is_array and (len(node.array_dimensions) > 1)

        return list(filter(n_dimensional_node, self.addressable_nodes))
