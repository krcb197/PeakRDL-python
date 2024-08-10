"""
Test exporting this tests a couple of different things:
1. calling the exporter
2. tests some of the export options that would not other be checked with the integration tests get
   checked (notably the show_hidden)
"""
import importlib
import unittest
import os
import tempfile
import sys

from contextlib import contextmanager

from peakrdl_python import PythonExporter
from systemrdl import RDLCompiler


class TestExportHidden(unittest.TestCase):

    test_case_path = 'tests/testcases'
    test_case_name = 'hidden_property.rdl'
    test_case_top_level = 'hidden_property'
    test_case_reg_model_cls = test_case_top_level + '_cls'

    @contextmanager
    def build_python_wrappers_and_make_instance(self, show_hidden):

        # compile the code for the test
        rdlc = RDLCompiler()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons
            if show_hidden:
                temp_package_name = 'show_hidden'
            else:
                temp_package_name = 'hidden'
            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=show_hidden)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__( temp_package_name + '.' + self.test_case_top_level +
                '.reg_model.' + self.test_case_top_level,
                globals(), locals(), [self.test_case_reg_model_cls], 0)
            dut_cls = getattr(reg_model_module, self.test_case_reg_model_cls)
            peakrdl_python_package = __import__(temp_package_name + '.' +
                                                self.test_case_top_level + '.lib',
                globals(), locals(), ['CallbackSet'], 0)
            callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')
            dummy_operations_module = __import__(temp_package_name + '.' +
                                                 self.test_case_top_level +
                                                 '.sim_lib.dummy_callbacks',
                                    globals(), locals(), ['dummy_read', 'dummy_write'], 0)
            dummy_read = getattr(dummy_operations_module, 'dummy_read')

            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            yield dut_cls(callbacks=callbackset_cls(read_callback=dummy_read))


            sys.path.remove(tmpdirname)



    def test_hidden(self):
        with self.build_python_wrappers_and_make_instance(show_hidden=False) as dut:
            self.assertFalse(dut.reg_hidden_fields.property_unhidden_field.read())
            self.assertFalse(dut.reg_hidden_fields.no_property_field.read())
            with self.assertRaises(AttributeError):
                _ = dut.reg_hidden_fields.property_hidden_field.read()

    def test_show_hidden(self):
        with self.build_python_wrappers_and_make_instance(show_hidden=True) as dut:
            self.assertFalse(dut.reg_hidden_fields.property_unhidden_field.read())
            self.assertFalse(dut.reg_hidden_fields.no_property_field.read())
            self.assertFalse(dut.reg_hidden_fields.property_hidden_field.read())

if __name__ == '__main__':

    unittest.main()
