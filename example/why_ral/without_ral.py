"""
An example to turn on GPIO 0 with just read and write
"""
from hardware_sim import HardwareSimulator
# create an instance of the hardware simulator
hw = HardwareSimulator()

if __name__ == '__main__':

    # 1. Read the DIR register (to make sure you preserve the states of other pins)
    dir_reg = hw.read(0x100)
    # 2. Take the read value of the DIR register, force bit 0 to `1` then write it back
    hw.write(0x100, dir_reg | (1 << 0)) # force bit 0 with bitwise OR
    # 3. Read the DATA_OUT register (to make sure you preserve the states of other pins)
    data_out_reg = hw.read(0x104)
    # 4. Take the read value of the DATA_OUT register, force bit 0 to `1` then write it back
    hw.write(0x104, data_out_reg | (1 << 0))  # force bit 0 with bitwise OR