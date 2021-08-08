#!/usr/bin/env python3

import sys
import os

import peakrdl.python.peakpython as pp

from glob import glob
from shutil import which
import re

if len(sys.argv) == 1:
    testcases = glob('tests/testcases/*.rdl')
else:
    testcases = glob('tests/testcases/{}.rdl'.format(sys.argv[1]))

#-------------------------------------------------------------------------------
results = {}
for case in testcases:
    print("Case: ", case)
    rdl_file = case
    testcase_name = os.path.splitext(os.path.basename(case))[0]

    root = pp.compile_rdl(rdl_file)
    modules = pp.generate(root, 'testcase_output')


    print("\n-----------------------------------------------------------------\n")

print("\tALL TESTS COMPLETED\n")