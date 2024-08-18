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
import argparse
import pathlib

from systemrdl import RDLCompiler # type: ignore
from systemrdl.node import Node, AddrmapNode # type: ignore
from peakrdl_ipxact import IPXACTImporter # type: ignore
from src.peakrdl_python import PythonExporter # type: ignore

test_case_path = os.path.join('tests', 'testcases')

CommandLineParser = argparse.ArgumentParser(description='Test the framework')
CommandLineParser.add_argument('--output', dest='output_path',
                               type=pathlib.Path,
                               default='testcase_output')
CommandLineParser.add_argument('--test_case', dest='test_case',
                               type=str)


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
             skip_test_case_generation: bool = False,
             legacy_block_access: bool = True) -> List[str]:
    """
    Generate a PeakRDL output package from compiled systemRDL

    Args:
        root: node in the systemRDL from which the code should be generated
        outdir: directory to store the result in
        autoformatoutputs: If set to True the code will be run through autopep8 to
                clean it up. This can slow down large jobs or mask problems
        legacy_block_access: If set to True the code build a register model the legacy array block
                             access as opposed to the newer list based

    Returns:
        List of strings with the module names generated

    """
    print(f'Info: Generating python for {root.inst_name} in {outdir}')
    modules = PythonExporter().export(root, outdir, # type: ignore[no-untyped-call]
                                      asyncoutput=asyncoutput,
                                      skip_test_case_generation=skip_test_case_generation,
                                      legacy_block_access=legacy_block_access)

    return modules


if __name__ == '__main__':

    CommandLineArgs = CommandLineParser.parse_args()

    output_path = CommandLineArgs.output_path

    #-------------------------------------------------------------------------------
    results = {}
    if CommandLineArgs.test_case:
        testcases = [os.path.join(test_case_path, CommandLineArgs.test_case)]
    else:
        testcases = glob(os.path.join(test_case_path, '*.rdl'))
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

        for build_options, folder_name in \
                [({'asyncoutput': True, 'legacy':False}, 'raw_async'),
                 ({'asyncoutput': False, 'legacy':False}, 'raw'),
                 ({'asyncoutput': True, 'legacy': True}, 'raw_async_legacy'),
                 ({'asyncoutput': False, 'legacy': True}, 'raw_legacy')
                 ]:

            # test cases that use the extended widths an not be tested in the non-legacy modes
            if (testcase_name in ['extended_memories', 'extended_sizes_registers_array']) and \
                    (build_options['legacy'] is True):
                continue

            _ = generate(root, str(output_path / folder_name),
                         asyncoutput=build_options['asyncoutput'],
                         legacy_block_access=build_options['legacy']
                         )

            module_fqfn = output_path / folder_name / '__init__.py'
            with open(module_fqfn, 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

        print("\n-----------------------------------------------------------------\n")

    print("\tALL TESTS COMPLETED\n")