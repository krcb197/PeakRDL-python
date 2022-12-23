"""
Module to test the old style import method
"""
import os
from systemrdl import RDLCompiler # type: ignore

# import peakrdl-python using the old import regime
from peakrdl.python import PythonExporter


test_case_path = os.path.join('tests', 'testcases')

if __name__ == '__main__':
    rdlc = RDLCompiler()
    rdlc.compile_file(os.path.join(test_case_path, 'basic.rdl'))
    root = rdlc.elaborate(top_def_name='basic').top

    PythonExporter().export(root, os.path.join('backward_testcase_output'), autoformatoutputs=False)