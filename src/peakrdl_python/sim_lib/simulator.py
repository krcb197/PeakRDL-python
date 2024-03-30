from abc import ABC, abstractmethod

class Simulator(ABC):

    def __init__(self, address: int):
        self._register_dict:dict[int, Register] = {}
        self._build_register_dict()
        self.address = address

    @abstractmethod
    def _build_register_dict(self) -> None:
        """

        """

    def read(self, addr: int, width: int = 32, accesswidth: int = 32) -> int:
        """
        function to simulate a device read
        """
        # TODO deal with address not in the dictionary
        return self._register_dict[addr].read()


    def write(self, addr: int, data: int, width: int=32, accesswidth: int=32) -> None:
        """
        function to simulate a device read
        """
        # TODO deal with address not in the dictionary
        self._register_dict[addr].write(data)

