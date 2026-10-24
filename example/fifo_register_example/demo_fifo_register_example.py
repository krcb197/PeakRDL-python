"""
PeakRDL Python example to show the different methods to access the fields of a register
"""
from functools import partial

from fifo_register_example.reg_model import RegModel
from fifo_register_example.sim import Simulator

from fifo_register_example.lib import NormalCallbackSet


class ChipSim(Simulator):

    def __init__(self):

        # initialise the chip simulation of the registers at base address 0
        super().__init__(address=0)
        self.fifo = []

        self.__access_reg = self.node_by_full_name('fifo_register_example.access_reg')
        self.__pop_field = self.field_by_full_name('fifo_register_example.access_reg.pop')
        self.__push_field = self.field_by_full_name('fifo_register_example.access_reg.push')
        self.__fill_count_field = self.field_by_full_name('fifo_register_example.access_reg.fill_count')
        self.__access_reg.read_callback = partial(self.__fifo_pop)
        self.__push_field.write_callback = partial(self.__fifo_push)

    def __fifo_push(self, value):
        self.fifo.append(value)
        self.__fill_count_field.value = len(self.fifo)
        self.__pop_field.value = self.fifo[0]

    def __fifo_pop(self, value):
        if len(self.fifo) > 0:
            self.__fill_count_field.value = len(self.fifo)
            self.__pop_field.value = self.fifo[0]
            data_expected = self.fifo.pop(0)

if __name__ == '__main__':

    # make an instance of the chip simulator and then locally defined the callbacks that will be
    # used to by the register access model
    chip_simulator = ChipSim()
    dut = RegModel(callbacks=NormalCallbackSet(read_callback=chip_simulator.read,
                                                           write_callback=chip_simulator.write))

    # putting data to the register without a read fills it correctly
    dut.access_reg.write_all_fields_without_read(push=1)
    dut.access_reg.write_all_fields_without_read(push=2)
    dut.access_reg.write_all_fields_without_read(push=3)
    assert chip_simulator.fifo == [1,2,3]
    # however doing a write directly to the push register field causes a implicit read to occur
    dut.access_reg.push.write(4)
    assert chip_simulator.fifo == [2, 3, 4]
    # the implicit read can be avoided with the `single_write` context manager
    with dut.access_reg.single_write(initial_state=0):
        dut.access_reg.push.write(5)
    assert chip_simulator.fifo == [2, 3, 4, 5]

    # checking the fill level results in a rad to the whole register, so one entry is pushed out and
    # effectly silently discarded
    fill_count = dut.access_reg.fill_count.read()
    assert chip_simulator.fifo == [ 3, 4, 5]
    # in order to avoid the silent discard of the data popped off there are two approaches
    # approach 1 use the `single_read` context manager
    with dut.access_reg.single_read() as reg:
        fill_count = dut.access_reg.fill_count.read()
        popped_value = dut.access_reg.pop.read()
        print(f'popped value: {popped_value}')
    assert popped_value == 3
    assert chip_simulator.fifo == [4, 5]
    # approach 2 uses the `read_fields` methods
    register_content = dut.access_reg.read_fields()
    fill_count = register_content['fill_count']
    popped_value = register_content['pop']
    print(f'popped value: {popped_value}')
    assert popped_value == 4
    assert chip_simulator.fifo == [5, ]






