"""
Test the export with name and desc, this unit test is needed so that the string as recieved from
the SystemRDL can be cross-checked back to exported code, this can not be done with the
integration tests
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

class TestAlternativeTemplates(unittest.TestCase):
    """
    Test class for the export of hidden and force not hidden (show hidden)
    """

    test_case_path = test_cases


    @contextmanager
    def build_python_wrappers_and_make_instance(self, test_case: str):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """
        test_case_file = test_case +'.rdl'
        test_case_reg_model_cls = test_case + '_cls'

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, test_case_file))
        spec = rdlc.elaborate(top_def_name=test_case).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons

            # pylint: disable=duplicate-code
            exporter.export(node=spec,
                            path=tmpdirname,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False)
            # pylint: enable=duplicate-code

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__(
                test_case + '.reg_model.' + test_case,
                globals(), locals(), [test_case_reg_model_cls],
                0)
            dut_cls = getattr(reg_model_module, test_case_reg_model_cls)
            peakrdl_python_package = __import__(test_case + '.lib',
                                                globals(), locals(), ['CallbackSet'], 0)
            callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')
            dummy_operations_module = __import__(test_case +
                                                 '.sim_lib.dummy_callbacks',
                                                 globals(), locals(),
                                                 ['dummy_read_block'], 0)
            dummy_read = getattr(dummy_operations_module, 'dummy_read_block')
            dummy_write = getattr(dummy_operations_module, 'dummy_write_block')

            yield (dut_cls(callbacks=callbackset_cls(read_block_callback=dummy_read,
                                                     write_block_callback=dummy_write)),
                   spec)

            sys.path.remove(tmpdirname)

    def test_all_name_and_desc(self):
        """
        Checks all the nodes in the reg model match the name and desc in the systemRDL compilation
        """
        node_name_regex = re.compile(r"(?P<node_name>\w*)(\[(?P<index>\d*)\])?")
        def walk_node_path(node, node_path: list[str]):
            if len(node_path) > 0:
                node_name_breakdown = node_name_regex.match(node_path[0])
                if (node_name:=node_name_breakdown.group('node_name')) is None:
                    raise RuntimeError(f'No Node name found for {node_path[0]}')
                child_node_name = node.systemrdl_python_child_name_map[node_name]
                if (node_index := node_name_breakdown.group('index')) is None:
                    child_node = getattr(node, child_node_name)
                else:
                    child_node = getattr(node, child_node_name)[int(node_index)]
                return walk_node_path(child_node, node_path[1:])
            return node

        for test_case in ['name_desc_all_levels', 'reg_name_stress']:
            with self.subTest(test_case=test_case):
                with self.build_python_wrappers_and_make_instance(test_case) as \
                        (reg_model, compiled_system_rdl):
                    for item in compiled_system_rdl.descendants(unroll=True):
                        path_segments = item.get_path_segments()
                        node = walk_node_path(reg_model, path_segments[1:])
                        if 'name' in item.list_properties():
                            self.assertEqual(item.get_property('name'), node.rdl_name)
                        else:
                            self.assertIsNone(node.rdl_name)

                        if 'desc' in item.list_properties():
                            self.assertEqual(item.get_property('desc'), node.rdl_desc)
                        else:
                            self.assertIsNone(node.rdl_desc)


if __name__ == '__main__':
    unittest.main()
