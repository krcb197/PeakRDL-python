#!/usr/bin/env python3
import argparse
import os
import subprocess

import flake8
import unittest.loader
from systemrdl import RDLCompiler

from peakrdl.python.exporter import PythonExporter

def parse_args():
    '''Program specific argument parsing'''
    parser = argparse.ArgumentParser(description='Generate Python output from systemRDL')
    parser.add_argument('infile', metavar='file', type=str,
                        help='input systemRDL file')

    parser.add_argument('--include_dir', type=str, action='append', metavar='dir',
                        help='add dir to include search path')
    parser.add_argument('--outdir', type=str, default='.',
                        help='output director (default: %(default)s)')
    parser.add_argument('--top', type=str,
                        help='specify top level addrmap (default operation will use last defined global addrmap)')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='set logging verbosity')

    checker = parser.add_argument_group('post-generate checks')
    checker.add_argument('--lint', action='store_true',
                         help='run Flake8 lint on the generated python')
    checker.add_argument('--test', action='store_true',
                         help='run unittests for the created')

    temp = parser.parse_args()

    return temp

def compile_rdl(infile, incl_search_paths=None, top=None):
    '''compile the rdl'''
    rdlc = RDLCompiler()
    rdlc.compile_file(infile, incl_search_paths=incl_search_paths)
    return rdlc.elaborate(top_def_name=top).top

def generate(root, outdir):
    '''generate the python'''
    print('Info: Generating python for {} in {}'.format(root.inst_name, outdir))
    modules = PythonExporter().export(root, outdir)
    for m in modules:
        print(" - Generated: " + ' '.join(os.path.join(outdir, '{}_{}'.format(m, k)) for k in ('rf.sv', 'tb.sv', 'tb.cpp')))

    return modules

if __name__ == '__main__':
    args = parse_args()
    spec = compile_rdl(args.infile, incl_search_paths=args.include_dir, top=args.top)
    #overrides = {k.prop: k.new for k in args.O}
    blocks = generate(spec, args.outdir)
    if args.lint:
        subprocess.run(['flake8', os.path.join(args.outdir, 'basic'), '--doctests'])
    if args.test:
        tests = unittest.TestLoader().discover(start_dir=os.path.join(args.outdir, 'basic', 'tests'))
        runner = unittest.TextTestRunner()
        result = runner.run(tests)