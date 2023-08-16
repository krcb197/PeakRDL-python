"""
Command Line tool for the PeakRDL Python
"""

#!/usr/bin/env python3
import argparse
import os
import unittest.loader
import warnings
from typing import List, Optional
import pathlib

from systemrdl import RDLCompiler # type: ignore
from systemrdl.node import Node, AddrmapNode # type: ignore
from peakrdl_ipxact import IPXACTImporter # type: ignore

from .exporter import PythonExporter


def build_command_line_parser() -> argparse.ArgumentParser:
    """
    generates the command line argument parser to be used by the module.

    Returns:
        command line args parser
    """
    parser = argparse.ArgumentParser(
        description='Generate Python output from systemRDL')
    parser.add_argument('infile', metavar='file', type=str,
                        help='input systemRDL file')

    parser.add_argument('--include_dir', type=str, action='append',
                        metavar='dir',
                        help='add dir to include search path')
    parser.add_argument('--outdir', type=str, default='.',
                        help='output director (default: %(default)s)')
    parser.add_argument('--top', type=str,
                        help='specify top level addrmap (default operation will use last defined '
                             'global addrmap)')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='set logging verbosity')
    parser.add_argument('--async', action='store_true',
                        help='builds the register model using the async callbacks')
    parser.add_argument('--ipxact', dest='ipxact', nargs='*',
                        type=str)
    parser.add_argument('--user_template_dir', action='store', type=pathlib.Path,
                           help='directory of user templates to override the default ones')
    checker = parser.add_argument_group('post-generate checks')
    checker.add_argument('--test', action='store_true',
                         help='run unittests for the created')
    parser.add_argument('--skip_test_case_generation', action='store_true',
                        help='skip the generation of the test cases')

    return parser


def compile_rdl(infile:str,
                incl_search_paths:Optional[List[str]]=None,
                top:Optional[str]=None,
                ipxact_files:Optional[List[str]]=None) -> AddrmapNode:
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


def generate(root:Node, outdir:str,
             asyncoutput:bool=False,
             skip_test_case_generation:bool=False) -> List[str]:
    """
    Generate a PeakRDL output package from compiled systemRDL

    Args:
        root: node in the systemRDL from which the code should be generated
        outdir: directory to store the result in
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

def main_function() -> None:
    """
    Main function for the Command Line tool, this needs to be separated out so that it can be
    referenced in setup.py

    Returns:
        None

    """

    cli_parser = build_command_line_parser()
    args = cli_parser.parse_args()

    if args.test and args.skip_test_case_generation:
        raise ValueError('it is not possible to run the tests if the generation has been skipped')

    print('***************************************************************')
    print('* Compile the SystemRDL                                       *')
    print('***************************************************************')
    spec = compile_rdl(args.infile, incl_search_paths=args.include_dir,
                       top=args.top, ipxact_files=args.ipxact)

    print('***************************************************************')
    print('* Generate the Python Package                                 *')
    print('***************************************************************')
    generate(spec, args.outdir,
             skip_test_case_generation=args.skip_test_case_generation,
             asyncoutput=args.asyncoutput)

    if args.test:
        print('***************************************************************')
        print('* Unit Test Run                                               *')
        print('***************************************************************')

        tests = unittest.TestLoader().discover(
            start_dir=os.path.join(args.outdir, spec.inst_name, 'tests'),
            top_level_dir=args.outdir)
        runner = unittest.TextTestRunner()
        runner.run(tests)

if __name__ == '__main__':

    warnings.warn('The peakpython command line option will be removed in a future release. '
                  'Command line functionality should be used via the see '
                  'https://peakrdl-python.readthedocs.io/en/latest/command_line.html',
                  category=PendingDeprecationWarning)

    main_function()
