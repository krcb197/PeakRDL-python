"""
Test that it is possible to build an addrmap inside the compiled structure and compare it to
a result of the top level
"""
import unittest
import os
import tempfile
import sys

from pathlib import Path

from contextlib import contextmanager

from peakrdl_python import PythonExporter
from peakrdl_python.lib import NormalCallbackSet
from peakrdl_python.lib import AddressMap
from peakrdl_python.sim_lib.dummy_callbacks import dummy_write_block, dummy_read_block
from peakrdl_python import compiler_with_udp_registers


# this assumes the current file is in the unit_test folder under tests
test_path = Path(__file__).parent.parent
test_cases = test_path / 'testcases'

class TestTopAndInner(unittest.TestCase):
    """
    Test class building both the top level address map and one of the inner address maps
    """
    test_case_path = test_cases


    @contextmanager
    def build_python_wrappers_and_make_instance(self):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """
        test_case = 'addr_map'
        test_case_file = test_case +'.rdl'
        test_case_reg_model_cls = test_case + '_cls'
        inner_addr_map = 'child_c'
        inner_case_reg_model_cls = inner_addr_map + '_cls'

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, test_case_file))
        spec = rdlc.elaborate(top_def_name=test_case)

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:

            exporter.export(node=spec.top,
                            path=tmpdirname,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=True,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False)
            exporter.export(node=spec.top.get_child_by_name(inner_addr_map),
                            path=tmpdirname,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=True,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False)


            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            def generate_instance(regmodel_name: str, regmodel_cls: str) -> AddressMap:
                """
                Import the register model python code and make an instance of the address map
                """

                reg_model_module = __import__(
                    regmodel_name + '.reg_model.' + regmodel_name,
                    globals(), locals(), [regmodel_cls],
                    0)
                dut_cls = getattr(reg_model_module, regmodel_cls)

                return dut_cls(callbacks=NormalCallbackSet(
                    read_block_callback=dummy_read_block,
                    write_block_callback=dummy_write_block))


            yield (generate_instance(test_case, test_case_reg_model_cls),
                   generate_instance(inner_addr_map, inner_case_reg_model_cls))

            sys.path.remove(tmpdirname)

    def test_top_and_inner(self):
        """
        Test that the inner address map generated separately from the full stack are the same
        """

        def compare_addrmap_instances(a: AddressMap, b: AddressMap):
            """
            Walk all the sections of two address maps to make sure they are the same
            """
            self.assertEqual(a.inst_name, b.inst_name)
            for a_child, b_child in zip(a.get_sections(unroll=True), b.get_sections(unroll=True)):
                compare_addrmap_instances(a_child, b_child)

            for a_child, b_child in zip(a.get_registers(unroll=True), b.get_registers(unroll=True)):
                self.assertEqual(a_child.inst_name, b_child.inst_name)
                self.assertEqual(a_child.address, b_child.address)

                for a_child_field, b_child_field in zip(a_child.fields, b_child.fields):
                    self.assertEqual(a_child_field.inst_name, b_child_field.inst_name)
                    self.assertEqual(a_child_field.lsb, b_child_field.lsb)
                    self.assertEqual(a_child_field.msb, b_child_field.msb)


        with self.build_python_wrappers_and_make_instance() as \
                (top_reg_model, inner_reg_model):
            compare_addrmap_instances(top_reg_model.child_c, inner_reg_model)

if __name__ == '__main__':
    unittest.main()
