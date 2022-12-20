"""
Module to test the old style import method
"""
import os
from peakrdl.python import PythonExporter as pp
test_case_path = os.path.join('tests', 'testcases')

if __name__ == '__main__':

    root = pp.compile_rdl(os.path.join(test_case_path, 'basic.rdl'))
    pp.generate(root, os.path.join('backward_testcase_output'), autoformatoutputs=False)