#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

from systemrdl import RDLCompiler
from peakrdl.python.exporter import PythonExporter

def parse_args():
    '''Program specific argument parsing'''
    parser = argparse.ArgumentParser(description='Generate Python output from systemRDL')
    parser.add_argument('infile', metavar='file', type=str,
                        help='input systemRDL file')

    parser.add_argument('-I', type=str, action='append', metavar='dir',
                        help='add dir to include search path')
    parser.add_argument('--outdir', '-o', type=str, default='.',
                        help='output director (default: %(default)s)')
    parser.add_argument('--top', '-t', type=str,
                        help='specify top level addrmap (default operation will use last defined global addrmap)')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='set logging verbosity')

    checker = parser.add_argument_group('post-generate checks')
    checker.add_argument('--lint', '-l', action='store_true',
                         help='run verilator lint on the generated verilog')
    checker.add_argument('--simulate', '-s', action='store_true',
                         help='run verilator simulation on the generated verilog')

    temp = parser.parse_args()

    if temp.O and temp.simulate:
        parser.print_usage()
        print("{}: argument --override/-O: --simulate not currently supported when using override".format(os.path.basename(__file__)))
        sys.exit(1)

    return temp

def compile_rdl(infile, incl_search_paths=None, top=None):
    '''compile the rdl'''
    rdlc = RDLCompiler()
    rdlc.compile_file(infile, incl_search_paths=incl_search_paths)
    return rdlc.elaborate(top_def_name=top).top

def generate(root, outdir, signal_overrides=None, bus='native'):
    '''generate the verilog'''
    print('Info: Generating python for {} in {}'.format(root.inst_name, outdir))
    modules = PythonExporter().export(
        root,
        outdir
    )
    for m in modules:
        print(" - Generated: " + ' '.join(os.path.join(outdir, '{}_{}'.format(m, k)) for k in ('rf.sv', 'tb.sv', 'tb.cpp')))

    return modules

if __name__ == '__main__':
    args = parse_args()
    spec = compile_rdl(args.infile, incl_search_paths=args.I, top=args.top)
    overrides = {k.prop: k.new for k in args.O}
    blocks = generate(spec, args.outdir, signal_overrides=overrides, bus=args.bus)
    if args.lint:
        run_lint(blocks, args.outdir)
    #if args.simulate:
    #    compile_verilog(blocks, args.outdir, verbosity=args.verbose)
    #    simulate(blocks, verbosity=args.verbose)