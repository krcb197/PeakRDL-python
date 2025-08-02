"""
A demonstration of using overridden names for peakrdl-python

In this example there is a register which has one field. These have systemRDL names: reg_a and
field_a respectively. However the python_inst_name has been used on change the names in the
peakrdl-python register model to overridden_reg_a and overridden_field_a respectively

"""
from over_ridden_names.reg_model.over_ridden_names import over_ridden_names_cls
from over_ridden_names.lib import NormalCallbackSet
from over_ridden_names.sim_lib.dummy_callbacks import dummy_read

if __name__ == '__main__':

    # create an instance of the class
    over_ridden_names = over_ridden_names_cls(callbacks=NormalCallbackSet(read_callback=dummy_read))

    # access the field value directly
    print(over_ridden_names.overridden_reg_a.overridden_field_a.read())

    # access the field value using the original systemRDL names
    print(over_ridden_names.get_child_by_system_rdl_name('reg_a').get_child_by_system_rdl_name('field_a').read())