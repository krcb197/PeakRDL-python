#!/usr/bin/env python3
import argparse
import os
import subprocess
import unittest.loader

import coverage

from systemrdl import RDLCompiler

from peakrdl.python.exporter import PythonExporter

def build_command_line_parser():
    '''Program specific argument parsing'''
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
                        help='specify top level addrmap (default operation will use last defined global addrmap)')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='set logging verbosity')
    parser.add_argument('--autoformat', action='store_true',
                        help='use autopep8 on generated code')

    checker = parser.add_argument_group('post-generate checks')
    checker.add_argument('--lint', action='store_true',
                         help='run pylint on the generated python')
    checker.add_argument('--test', action='store_true',
                         help='run unittests for the created')
    checker.add_argument('--coverage', action='store_true',
                         help='run a coverage report on the unittests')
    checker.add_argument('--html_coverage_out',
                         help='output director (default: %(default)s)')

    return parser

def parse_args():

    cli_parser = build_command_line_parser()

    return cli_parser.parse_args()

def compile_rdl(infile, incl_search_paths=None, top=None):
    '''compile the rdl'''
    rdlc = RDLCompiler()
    rdlc.compile_file(infile, incl_search_paths=incl_search_paths)
    return rdlc.elaborate(top_def_name=top).top

def generate(root, outdir, autoformatoutputs=True):
    '''generate the python'''
    print('Info: Generating python for {} in {}'.format(root.inst_name, outdir))
    modules = PythonExporter().export(root, outdir,
                                      autoformatoutputs=autoformatoutputs)

    return modules

def run_lint(root, outdir):
    subprocess.run(['pylint', '--rcfile', os.path.join('tests','pylint.rc'), os.path.join(outdir, root)])

if __name__ == '__main__':
    args = parse_args()
    spec = compile_rdl(args.infile, incl_search_paths=args.include_dir, top=args.top)
    #overrides = {k.prop: k.new for k in args.O}
    blocks = generate(spec, args.outdir, args.autoformat)
    if args.lint:
        print('***************************************************************')
        print('* Lint Checks                                                 *')
        print('***************************************************************')
        run_lint(outdir=args.outdir, root=spec.inst_name)
    if args.test:
        print('***************************************************************')
        print('* Unit Test Run                                               *')
        print('***************************************************************')
        if args.coverage:
            cov = coverage.Coverage(include=[f'*\\{spec.inst_name}\\reg_model\\*.py',
                                             f'*\\{spec.inst_name}\\tests\\*.py'])
            cov.start()
        tests = unittest.TestLoader().discover(start_dir=os.path.join(args.outdir, spec.inst_name, 'tests'), top_level_dir=args.outdir)
        runner = unittest.TextTestRunner()
        result = runner.run(tests)

        if args.coverage:
            cov.stop()

        if args.html_coverage_out is not None:
            cov.html_report(directory=args.html_coverage_out )
