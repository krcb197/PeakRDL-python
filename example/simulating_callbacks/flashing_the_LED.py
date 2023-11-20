import tkinter as tk

from mychip.reg_model.mychip import mychip_cls
from mychip.lib import NormalCallbackSet

class ChipSim:

    def __init__(self):

        # simulator state variables
        self.PIN_output = False
        self.PIN_state = False

        # basic GUI components
        self.root = tk.Tk()
        self.root.title("My Chip Simulator")
        self.LED_label = tk.Label(master=self.root,
                                  text="LED_0",
                                  foreground="black")  # Set the background color to black
        self.LED_label.pack(fill=tk.X, side=tk.TOP)
        window_frame = tk.Frame(master=self.root, width=400, height=400,bg="black")
        window_frame.pack(fill=tk.BOTH, side=tk.TOP)
        self.LED = tk.Canvas(master=window_frame, width=300, height=300, bg='black')
        self.LED.pack()
        self.LED_inner = self.LED.create_oval(25, 25, 275, 275, fill='black')

    def read_addr_space(self, addr: int, width: int, accesswidth: int) -> int:
        """
        Callback to for the simulation of the chip

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits

        Returns:
            simulated register value
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)

        if addr == 0x4:
            if self.PIN_output is True:
                return 0x1
            else:
                return 0x0
        elif addr == 0x8:
            if self.PIN_state is True:
                return 0x1
            else:
                return 0x0

    def write_addr_space(self, addr: int, width: int, accesswidth: int, data: int) -> None:
        """
        Callback to for the simulation of the chip

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits
            data: value to be written to the register

        Returns:
            None
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        assert isinstance(data, int)

        if addr == 0x4:
            if (data & 0x1) == 0x1:
                self.PIN_output = True
            else:
                self.PIN_output = False
        elif addr == 0x8:
            if (data & 0x1) == 0x1:
                self.PIN_state = True
            else:
                self.PIN_state = False

        self.update_LED()

    def update_LED(self):

        if self.PIN_output is True:
            # LED is enabled
            if self.PIN_state is True:
                self.LED.itemconfig(self.LED_inner, fill='red')
            else:
                self.LED.itemconfig(self.LED_inner, fill='black')
        else:
            self.LED.itemconfig(self.LED_inner, fill='black')

# these two methods can be put in the simulator Tkinter event queue to perform register writes on
# the register access layer (in turn causing the state of the simulator to change)

def turn_LED_on(chip: mychip_cls, sim_kt_root):

    # write a '1' to the LED state field
    chip.GPIO.GPIO_state.PIN_0.write(1)
    # set up another event to happen
    sim_kt_root.after(2000, turn_LED_off, chip, sim_kt_root)

def turn_LED_off(chip: mychip_cls, sim_kt_root):

    # write a '0' to the LED state field
    chip.GPIO.GPIO_state.PIN_0.write(0)
    # set up another event to happen
    sim_kt_root.after(2000, turn_LED_on, chip, sim_kt_root)


if __name__ == '__main__':

    # make an instance of the chip simulator and then locally defined the callbacks that will be
    # used to by the register access model
    chip_simulator = ChipSim()

    def read_call_back(addr: int, width: int, accesswidth: int):
        return chip_simulator.read_addr_space(addr=addr,
                                              width=width,
                                              accesswidth=accesswidth)
    def write_call_back(addr: int, width: int, accesswidth: int, data: int):
        chip_simulator.write_addr_space(addr=addr,
                                        width=width,
                                        accesswidth=accesswidth,
                                        data=data)

    # create a callback set for the callbacks
    callbacks = NormalCallbackSet(read_callback=read_call_back,
                                  write_callback=write_call_back)

    # created an instance of the register model and connect the callbacks to the simulator
    mychip = mychip_cls(callbacks=callbacks)

    # configure the GPIO.PIN_0 as an output
    mychip.GPIO.GPIO_dir.PIN_0.write(mychip.GPIO.GPIO_dir.PIN_0.enum_cls.dir_out)

    # set up the first event to turn the LED on after 2s (this event will then set-up a follow up
    # event to turn it off. This sequencer repeats forever.
    chip_simulator.root.after(2000, turn_LED_on, mychip, chip_simulator.root)
    # start the GUI (simulator)
    chip_simulator.root.mainloop()