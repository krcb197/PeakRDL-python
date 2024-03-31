#!/usr/bin/env python3

"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

script to generate all the test cases from the test set
"""

import sys
import os

from glob import glob
from typing import Optional, List

from systemrdl import RDLCompiler # type: ignore
from systemrdl.node import Node, AddrmapNode # type: ignore
from peakrdl_ipxact import IPXACTImporter # type: ignore
from src.peakrdl_python import PythonExporter # type: ignore

test_case_path = os.path.join('tests', 'testcases')


def compile_rdl(infile: str,
                incl_search_paths: Optional[List[str]] = None,
                top: Optional[str] = None,
                ipxact_files: Optional[List[str]] = None) -> AddrmapNode:
    """
    Compile the systemRDL

    Args:
        infile: top level systemRDL file
        incl_search_paths: list of additional paths where dependent systemRDL files can be
            retrived from. Set to ```none``` if no additional paths are required.
        top: name of the top level address map
        ipxact_files: any IP-XACT files that must be precompiled before compiling the systemRDL

    Returns:

    """
    rdlc = RDLCompiler()
    if ipxact_files is not None:

        ipxact = IPXACTImporter(rdlc)
        if isinstance(ipxact_files, list):
            for ipxact_file in ipxact_files:
                ipxact.import_file(ipxact_file)
        else:
            raise ValueError(f'This ipxact_files should be a list got {type(ipxact_files)}')

    rdlc.compile_file(infile, incl_search_paths=incl_search_paths)
    return rdlc.elaborate(top_def_name=top).top


def generate(root: Node, outdir: str,
             asyncoutput: bool = False,
             skip_test_case_generation: bool = False) -> List[str]:
    """
    Generate a PeakRDL output package from compiled systemRDL

    Args:
        root: node in the systemRDL from which the code should be generated
        outdir: directory to store the result in
        autoformatoutputs: If set to True the code will be run through autopep8 to
                clean it up. This can slow down large jobs or mask problems
        asyncoutput: If set to True the code build a register model with async operations to
                access the harware layer

    Returns:
        List of strings with the module names generated

    """
    print(f'Info: Generating python for {root.inst_name} in {outdir}')
    modules = PythonExporter().export(root, outdir, # type: ignore[no-untyped-call]
                                      asyncoutput=asyncoutput,
                                      skip_test_case_generation=skip_test_case_generation)

    return modules


if __name__ == '__main__':
    if len(sys.argv) == 1:
        testcases = glob(os.path.join(test_case_path,'*.rdl'))
    else:
        testcases = glob(os.path.join(test_case_path,'{}.rdl').format(sys.argv[1]))

    #-------------------------------------------------------------------------------
    results = {}
    for case in testcases:
        print("Case: ", case)
        rdl_file = case
        testcase_name = os.path.splitext(os.path.basename(case))[0]

        if testcase_name == 'multifile':
            # this needs the simple.xml file included
            root = compile_rdl(rdl_file, ipxact_files=[os.path.join(test_case_path, 'simple.xml')])
        elif testcase_name == 'multi_block':
            # this needs the simple.xml file included
            root = compile_rdl(rdl_file, ipxact_files=[os.path.join(test_case_path, 'block_a.xml'),
                                                       os.path.join(test_case_path,
                                                                    'block_b.xml')])
        else:
            root = compile_rdl(rdl_file)

        for asyncoutput, folder_name in [(False, 'raw'),
                                         (True, 'raw_async')]:
            _ = generate(root, os.path.join('testcase_output', folder_name),
                            asyncoutput=asyncoutput)

            module_fqfn = os.path.join('testcase_output', folder_name, '__init__.py')
            with open(module_fqfn, 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

        print("\n-----------------------------------------------------------------\n")

    print("\tALL TESTS COMPLETED\n")