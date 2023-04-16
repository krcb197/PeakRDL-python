"""
Node walkers to be used in the generated of the output code
"""
from typing import Optional, List, Union

from systemrdl import RDLListener, WalkerAction
from systemrdl import RegNode, MemNode, FieldNode, AddrmapNode, RegfileNode


class AddressMaps(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the desendent
    address maps
    """
    def __init__(self):
        super().__init__()
        self.__address_maps: List[AddrmapNode] = []

    def enter_Addrmap(self, node):
        if not isinstance(node, AddrmapNode):
            raise ValueError(f'node:{node.inst_name} is not an Address Map')
        self.__address_maps.append(node)
        return WalkerAction.Continue

    def __iter__(self):
        return self.__address_maps.__iter__()


class OwnedbyAddressMap(RDLListener):
    """
    class intended to be used as part of the walker/listener protocol to find all the items owned
    by an address map but not the descendents of any address map
    """
    def __init__(self):
        super().__init__()

        self.registers: List[RegNode] = []
        self.fields: List[RegNode]  = []
        self.memories: List[RegNode]  = []
        self.addr_maps: List[AddrmapNode]  = []
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

    def enter_Addrmap(self, node) -> Optional[WalkerAction]:
        self.addr_maps.append(node)
        return WalkerAction.SkipDescendants

    def enter_Regfile(self, node: RegfileNode) -> Optional[WalkerAction]:
        self.reg_files.append(node)
        return WalkerAction.Continue

    @property
    def nodes(self) -> List[Union[RegNode, MemNode, FieldNode, AddrmapNode, RegfileNode]]:
        return self.addr_maps + self.reg_files + self.memories + self.registers + self.fields