import tkinter
import tkinter as tk

from mychip.reg_model.mychip import mychip_cls
from mychip.sim.mychip import mychip_simulator_cls
from mychip.lib import NormalCallbackSet

class ChipSim(mychip_simulator_cls):

    def __init__(self):

        # initialise the chip simulation of the registers at base address 0
        super().__init__(address=0)
        # create an alias to the GPIO[0] (connected to LED) direction control field
        self.__gpio_pin_dir_reg_field_sim = self.node_by_full_name('mychip.GPIO.GPIO_dir.PIN_0')
        # attach a callback function to the state of the GPIO[0], which is called everytime the
        # field is written to
        self.node_by_full_name('mychip.GPIO.GPIO_state.PIN_0').write_callback = self.__update_LED

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

    def __update_LED(self, value) -> None:
        """
        Call back attached to the state field for the GPIO.

        Args:
            value: value written to register field

        Returns:
            None
        """

        if self.__gpio_pin_dir_reg_field_sim.value == 1:
            # only action the state of the GPIO (external LED if the direction is set to out)
            if value == 1:
                self.LED.itemconfig(self.LED_inner, fill='red')
            else:
                self.LED.itemconfig(self.LED_inner, fill='black')
        else:
            self.LED.itemconfig(self.LED_inner, fill='black')


def timer_event(chip: mychip_cls, sim_kt_root: tkinter.Tk) -> None:
    """
    timer event which will invert the state of the LED and then set the timer event to run
    in 2s

    Args:
        chip: RAL for the chip
        sim_kt_root: root of the tkinter object needed for setting up the next timer event

    Returns:
        None

    """

    # invert the current state of the LED
    current_state = chip.GPIO.GPIO_state.PIN_0.read()
    if current_state == 0:
        chip.GPIO.GPIO_state.PIN_0.write(1)
    elif current_state == 1:
        chip.GPIO.GPIO_state.PIN_0.write(0)
    else:
        raise ValueError(f'unhandled current state {current_state:d}')
    # set up another event to happen
    sim_kt_root.after(2000, timer_event, chip, sim_kt_root)


if __name__ == '__main__':

    # make an instance of the chip simulator and then locally defined the callbacks that will be
    # used to by the register access model
    chip_simulator = ChipSim()

    # create a callback set for the callbacks
    callbacks = NormalCallbackSet(read_callback=chip_simulator.read,
                                  write_callback=chip_simulator.write)

    # created an instance of the register model and connect the callbacks to the simulator
    mychip = mychip_cls(callbacks=callbacks)

    # configure the GPIO.PIN_0 as an output
    mychip.GPIO.GPIO_dir.PIN_0.write(mychip.GPIO.GPIO_dir.PIN_0.enum_cls.DIR_OUT)
    # set up the first event to turn the LED on in 2s. This event will then set-up a follow up
    # event such that the sequence runs forever.
    chip_simulator.root.after(2000, timer_event, mychip, chip_simulator.root)
    # start the GUI (simulator)
    chip_simulator.root.mainloop()