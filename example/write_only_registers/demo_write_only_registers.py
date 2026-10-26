"""
PeakRDL Python example to show the different methods to access the fields of a register
"""
from functools import partial

from write_only_registers.reg_model import RegModel
from write_only_registers.sim import Simulator

from write_only_registers.lib import NormalCallbackSet


class ChipSim(Simulator):

    def __init__(self):

        # initialise the chip simulation of the registers at base address 0
        super().__init__(address=0)

        self.__event_status_field = [ self.node_by_full_name(f'write_only_registers.status.status_event_{event_idx}') for event_idx in range(2) ]
        self.__event_clear_status_field = [ self.node_by_full_name(f'write_only_registers.status_clear.n_status_event_{event_idx}') for event_idx in range(2) ]

        for event_idx, event_clear_status_field in enumerate(self.__event_clear_status_field):
            event_clear_status_field.write_callback = partial(self.__clear_status_event, event_idx)

    def simulate_status_event(self, event: int):
        """
        method to simulate the creation of a status event
        """
        assert isinstance(event, int)
        assert event in (0, 1)

        self.__event_status_field[event].value = True

    def __clear_status_event(self, event: int, value: bool):
        """
        method to simulate the creation of a status event
        """
        assert isinstance(event, int)
        assert event in (0, 1)

        if value == 0:
            self.__event_status_field[event].value = False


if __name__ == '__main__':

    # make an instance of the chip simulator and then locally defined the callbacks that will be
    # used to by the register access model
    chip_simulator = ChipSim()
    dut = RegModel(callbacks=NormalCallbackSet(read_callback=chip_simulator.read,
                                                           write_callback=chip_simulator.write))

    # check the status are all clear
    assert not any((dut.status.status_event_0.read(), dut.status.status_event_1.read() ))

    # example 1
    # trigger a status to be set and then check it is set
    chip_simulator.simulate_status_event(0)
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == False
    # writing True to the clear should have no effect as the field is designed to have inverted logic
    dut.status_clear.n_status_event_0.write(True)
    assert dut.status.status_event_0.read() == True
    # writing False (0) to the field should clear the status as this is an inverted logic field
    dut.status_clear.n_status_event_0.write(False)
    assert dut.status.status_event_0.read() == False

    # example 2
    # trigger a status to be set on both status
    chip_simulator.simulate_status_event(0)
    chip_simulator.simulate_status_event(1)
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == True
    # writing to the clear[0] will clear both the status because it will assume by default that
    # the rest of the register is set to 0
    dut.status_clear.n_status_event_0.write(True)
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == False # the stat 1 has been cleared erroneously
    # to avoid this problem there are two approaches, so we 1st reset the statuses
    chip_simulator.simulate_status_event(0)
    chip_simulator.simulate_status_event(1)
    # approach 1 use the `write_fields` method, this explicitly shows all the register states
    # being set
    dut.status_clear.write_fields(n_status_event_0=True, n_status_event_1=True)
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == True
    # approach 2 use the `single_write` context manager,
    with dut.status_clear.single_write(initial_state=0):
        dut.status_clear.n_status_event_0.write(True)
        dut.status_clear.n_status_event_1.write(True)
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == True
    # approach 3 use the `single_write` context manager with a default value of both clear set to
    # True means that the write to `n_status_event_1` is set to True any way
    with dut.status_clear.single_write(initial_state=dut.status_clear.register_value(n_status_event_0=True, n_status_event_1=True)):
        dut.status_clear.n_status_event_0.write(True)
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == True
    # approach 4 configure the `write_initial_state` which is used to determine the default state
    # of the register, this is useful if the same register is written to multiple times as it
    # only needs to be set once
    dut.status_clear.write_initial_state = dut.status_clear.register_value(n_status_event_0=True,
                                                                           n_status_event_1=True)
    # in this case the `inferred_default_register_value()` register state can be used, as both
    # fields have a reset value of 1 configured
    assert dut.status_clear.write_initial_state == dut.status_clear.inferred_default_register_value()
    dut.status_clear.n_status_event_0.write(True)
    # in this case the assumed state of status_event_1 is True because it was taken from the
    # initial state
    assert dut.status.status_event_0.read() == True
    assert dut.status.status_event_1.read() == True




