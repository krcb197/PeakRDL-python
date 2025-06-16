"""
Test that it is possible to build a addrmap inside the compiled structure and compare it to
a result of a the top level
"""
import unittest
import os
import tempfile
import sys
import re

from pathlib import Path



from contextlib import contextmanager

from peakrdl_python import PythonExporter
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
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons

            # pylint: disable=duplicate-code
            exporter.export(node=spec.top,
                            path=tmpdirname,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False)
            exporter.export(node=spec.top.get_child_by_name(inner_addr_map),
                            path=tmpdirname,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False)


            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            top_reg_model_module = __import__(
                test_case + '.reg_model.' + test_case,
                globals(), locals(), [test_case_reg_model_cls],
                0)
            top_dut_cls = getattr(top_reg_model_module, test_case_reg_model_cls)
            top_peakrdl_python_package = __import__(test_case + '.lib',
                                                    globals(), locals(), ['CallbackSet'], 0)
            top_callbackset_cls = getattr(top_peakrdl_python_package, 'NormalCallbackSet')
            top_dummy_operations_module = __import__(test_case +
                                                 '.sim_lib.dummy_callbacks',
                                                 globals(), locals(),
                                                 ['dummy_read_block'], 0)
            top_dummy_read = getattr(top_dummy_operations_module, 'dummy_read_block')
            top_dummy_write = getattr(top_dummy_operations_module, 'dummy_write_block')

            inner_reg_model_module = __import__(
                inner_addr_map + '.reg_model.' + inner_addr_map,
                globals(), locals(), [test_case_reg_model_cls],
                0)
            inner_dut_cls = getattr(inner_reg_model_module, inner_case_reg_model_cls)
            inner_peakrdl_python_package = __import__(inner_addr_map + '.lib',
                                                      globals(), locals(), ['CallbackSet'], 0)
            inner_callbackset_cls = getattr(inner_peakrdl_python_package, 'NormalCallbackSet')
            inner_dummy_operations_module = __import__(inner_addr_map +
                                                       '.sim_lib.dummy_callbacks',
                                                       globals(), locals(),
                                                       ['dummy_read_block'], 0)
            inner_dummy_read = getattr(inner_dummy_operations_module, 'dummy_read_block')
            inner_dummy_write = getattr(inner_dummy_operations_module, 'dummy_write_block')
            # pylint: enable=duplicate-code

            yield (top_dut_cls(callbacks=top_callbackset_cls(
                read_block_callback=top_dummy_read,
                write_block_callback=top_dummy_write)),
                   inner_dut_cls(callbacks=inner_callbackset_cls(
                       read_block_callback=inner_dummy_read,
                       write_block_callback=inner_dummy_write)),
                   spec)

            sys.path.remove(tmpdirname)

    def test_top_and_inner(self):
        with self.build_python_wrappers_and_make_instance() as \
                (top_reg_model, inner_reg_model, compiled_system_rdl):
            # TODO compare child_c in the top_reg_model to inner_reg_model
            # making sure they are the same
            pass

if __name__ == '__main__':
    unittest.main()
