from user_defined_property.reg_model.user_defined_property import user_defined_property_cls
from user_defined_property.sim_lib.dummy_callbacks import dummy_read, dummy_write
from user_defined_property.lib.callbacks import NormalCallbackSet

if __name__ == '__main__':

    # create an instance of the class
    regmodel = user_defined_property_cls(callbacks=NormalCallbackSet(read_callback=dummy_read,
                                                                     write_callback=dummy_write))

    # loop through the the fields in the register access model and print out the value of the
    # component_usage property
    for field in regmodel.control_register.readable_fields:
        field_usage = field.udp['component_usage']
        print(f"Control register field:{field.inst_name} has recommend usage {field_usage.name}")

