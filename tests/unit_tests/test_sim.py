"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Test the simulator callbacks
"""
import unittest
from unittest.mock import Mock
import os
import tempfile
import random
import sys
from contextlib import contextmanager
from pathlib import Path
from collections import namedtuple
from typing import Union

from peakrdl_python import PythonExporter
from peakrdl_python import compiler_with_udp_registers
from peakrdl_python.lib import NormalCallbackSet
from peakrdl_python.sim_lib.register import Register as SimRegister
from peakrdl_python.sim_lib.field import Field as SimField
from peakrdl_python.sim_lib.field import ReadOnlyField as SimReadOnlyField
from peakrdl_python.sim_lib.field import WriteOnlyField as SimWriteOnlyField
from peakrdl_python.sim_lib.field import ReadWriteField as SimReadWriteField

# this assumes the current file is in the unit_test folder under tests
test_path = Path(__file__).parent.parent
test_cases = test_path / 'testcases'

RegModelAndSim = namedtuple('RegModelAndSim', ['reg_model', 'sim'])


class TestSimCallback(unittest.TestCase):
    """
    Tests for including the UDPs in the generated RAL
    """

    test_case_path = test_cases
    test_case_name = 'overlapping_registers_and_fields.rdl'
    test_case_top_level = 'overlapping_registers_and_fields'
    test_case_reg_model_cls = test_case_top_level + '_cls'
    test_case_sim_cls = test_case_top_level + '_simulator_cls'

    @contextmanager
    def build_wrappers_and_import(self):
        """
        Context manager to build the python wrappers with the specified UDPs included then import
        them and clean up afterwards
        """
        # pylint:disable=duplicate-code

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons

            temp_package_name = 'dir_' + str(random.randint(0, (2**32) -1))
            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            skip_library_copy=True,)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__( temp_package_name + '.' + self.test_case_top_level +
                '.reg_model.' + self.test_case_top_level,
                globals(), locals(), [self.test_case_reg_model_cls], 0)
            dut_cls = getattr(reg_model_module, self.test_case_reg_model_cls)

            sim_module = __import__(temp_package_name + '.' + self.test_case_top_level +
                                          '.sim.' + self.test_case_top_level,
                                          globals(), locals(), [self.test_case_sim_cls], 0)
            sim_cls = getattr(sim_module, self.test_case_sim_cls)

            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            sim_inst = sim_cls(0)
            yield RegModelAndSim(
                reg_model=dut_cls(callbacks=NormalCallbackSet(read_callback=sim_inst.read,
                                                              write_callback=sim_inst.write)),
                sim=sim_inst)

            sys.path.remove(tmpdirname)

    def _configure_callbacks(self, node: Union[SimRegister, SimField]) -> tuple[Mock, Mock]:
        read_call_back = Mock()
        write_call_back = Mock()
        if isinstance(node, (SimReadOnlyField, SimReadWriteField, SimRegister)):
            node.read_callback = read_call_back
        if isinstance(node, (SimWriteOnlyField, SimReadWriteField, SimRegister)):
            node.write_callback = write_call_back

        return read_call_back, write_call_back

    def test_overlapping_reg(self):
        """
        The test works on address 4 which has two registers tx and rx that share the same space
        """
        with self.build_wrappers_and_import() as reg_model_sim:

            # setup the mocks:
            tx_reg_sim = reg_model_sim.sim.register_by_full_name(
                'overlapping_registers_and_fields.tx')
            tx_data_sim = reg_model_sim.sim.field_by_full_name(
                'overlapping_registers_and_fields.tx.data')
            rx_reg_sim = reg_model_sim.sim.register_by_full_name(
                'overlapping_registers_and_fields.rx')
            rx_data_sim = reg_model_sim.sim.field_by_full_name(
                'overlapping_registers_and_fields.rx.data')

            tx_reg_sim_read_call_back, tx_reg_sim_write_call_back =\
                self._configure_callbacks(tx_reg_sim)
            rx_reg_sim_read_call_back, rx_reg_sim_write_call_back =\
                self._configure_callbacks(rx_reg_sim)
            tx_data_sim_read_call_back, tx_data_sim_write_call_back =\
                self._configure_callbacks(tx_data_sim)
            rx_data_sim_read_call_back, rx_data_sim_write_call_back =\
                self._configure_callbacks(rx_data_sim)

            # do a write test
            reg_model_sim.reg_model.tx.data.write(1)

            tx_reg_sim_read_call_back.assert_not_called()
            rx_reg_sim_read_call_back.assert_not_called()
            rx_reg_sim_write_call_back.assert_not_called()
            tx_data_sim_read_call_back.assert_not_called()
            rx_data_sim_read_call_back.assert_not_called()
            rx_data_sim_write_call_back.assert_not_called()

            tx_reg_sim_write_call_back.assert_called_once_with(value=1)
            tx_data_sim_write_call_back.assert_called_once_with(value=1)

            tx_reg_sim_write_call_back.reset_mock()
            tx_data_sim_write_call_back.reset_mock()

            # do a read test
            next_rx_data_value = random.randint(0,reg_model_sim.reg_model.rx.data.max_value)
            rx_data_sim.value = next_rx_data_value

            self.assertEqual(reg_model_sim.reg_model.rx.data.read(), next_rx_data_value)

            tx_reg_sim_read_call_back.assert_not_called()
            rx_reg_sim_write_call_back.assert_not_called()
            tx_data_sim_read_call_back.assert_not_called()
            rx_data_sim_write_call_back.assert_not_called()
            tx_reg_sim_write_call_back.assert_not_called()
            tx_data_sim_write_call_back.assert_not_called()

            rx_reg_sim_read_call_back.assert_called_once_with(value=next_rx_data_value)
            rx_data_sim_read_call_back.assert_called_once_with(value=next_rx_data_value)

    def test_overlapping_field(self):
        """
        The test works on address 4 which has two registers tx and rx that share the same space
        """
        with self.build_wrappers_and_import() as reg_model_sim:

            # setup the mocks:
            reg_sim = reg_model_sim.sim.register_by_full_name(
                'overlapping_registers_and_fields.mixed_overlapping_and_noneoverlapping')
            ro_field_sim = reg_model_sim.sim.field_by_full_name(
                'overlapping_registers_and_fields.mixed_overlapping_and_noneoverlapping.ro_field')
            wo_field_sim = reg_model_sim.sim.field_by_full_name(
                'overlapping_registers_and_fields.mixed_overlapping_and_noneoverlapping.wo_field')
            rw_field_sim = reg_model_sim.sim.field_by_full_name(
                'overlapping_registers_and_fields.mixed_overlapping_and_noneoverlapping.rw_field')



            reg_sim_read_call_back, reg_sim_write_call_back = self._configure_callbacks(reg_sim)
            ro_field_sim_read_call_back, ro_field_sim_write_call_back =\
                self._configure_callbacks(ro_field_sim)
            wo_field_sim_read_call_back, wo_field_sim_write_call_back =\
                self._configure_callbacks(wo_field_sim)
            rw_field_sim_read_call_back, rw_field_sim_write_call_back =\
                self._configure_callbacks(rw_field_sim)


            # do a write test
            reg_model_sim.reg_model.mixed_overlapping_and_noneoverlapping.wo_field.write(1)

            reg_sim_read_call_back.assert_called_once_with(value=0)
            reg_sim_read_call_back.reset_mock()
            reg_sim_write_call_back.assert_called_once_with(value=1)
            reg_sim_write_call_back.reset_mock()
            ro_field_sim_read_call_back.assert_called_once_with(value=0)
            ro_field_sim_read_call_back.reset_mock()
            ro_field_sim_write_call_back.assert_not_called()
            wo_field_sim_read_call_back.assert_not_called()
            wo_field_sim_write_call_back.assert_called_once_with(value=1)
            wo_field_sim_write_call_back.reset_mock()
            rw_field_sim_read_call_back.assert_called_once_with(value=0)
            rw_field_sim_read_call_back.reset_mock()
            rw_field_sim_write_call_back.assert_called_once_with(value=0)
            rw_field_sim_write_call_back.reset_mock()

            # do a read test
            next_ro_field_value = random.randint(
                0,
                reg_model_sim.reg_model.mixed_overlapping_and_noneoverlapping.ro_field.max_value)
            ro_field_sim.value = next_ro_field_value
            self.assertEqual(
                reg_model_sim.reg_model.mixed_overlapping_and_noneoverlapping.ro_field.read(),
                next_ro_field_value)

            reg_sim_read_call_back.assert_called_once_with(value=next_ro_field_value)
            reg_sim_write_call_back.assert_not_called()
            ro_field_sim_read_call_back.assert_called_once_with(value=next_ro_field_value)
            ro_field_sim_write_call_back.assert_not_called()
            wo_field_sim_read_call_back.assert_not_called()
            wo_field_sim_write_call_back.assert_not_called()
            rw_field_sim_read_call_back.assert_called_once_with(value=0)
            rw_field_sim_write_call_back.assert_not_called()


    # add a read/write to an undefined address of the simulator









if __name__ == '__main__':
    unittest.main()
