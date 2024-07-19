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

script to generate the python wrappers from systemRDL and then execute the unit tests. This script
is not intended to be part of the package, peakrdl-python is normally intended to be run from
the peakrdl command line tool. However, when developing and debugging it is convenient to bypass
peakrdl and call the exporter directly.
"""

import os
import time
import argparse
import pathlib
import sys

import logging.config

from unittest import TestLoader
from unittest import TestSuite
from unittest import TextTestRunner

from coverage import Coverage

from systemrdl import RDLCompiler

from peakrdl_ipxact import IPXACTImporter

sys.path.append('src')
from peakrdl_python import PythonExporter

CommandLineParser = argparse.ArgumentParser(description='Test the framework')
CommandLineParser.add_argument('--RDL_source_file', dest='root_RDL_file',
                               type=pathlib.Path, required=True)
CommandLineParser.add_argument('--root_node', dest='root_node',
                               type=str, required=True)
CommandLineParser.add_argument('--output', dest='output_path',
                               type=pathlib.Path,
                               default='.')
CommandLineParser.add_argument('--ipxact', dest='ipxact', nargs='*',
                               type=str)
CommandLineParser.add_argument('--async', action='store_true', dest='asyncoutput',
                               help='use async callback register model')
CommandLineParser.add_argument('--export_only', action='store_true',
                               help='only export the code (i.e. do not attempt test run)')
CommandLineParser.add_argument('--coverage_report', action='store_true', dest='coverage_report',
                               help='generate a coverage report')
CommandLineParser.add_argument('--coverage_report_path', dest='coverage_report_path',
                               type=pathlib.Path,
                               default='generate_and_test_coverage')
CommandLineParser.add_argument('--suppress_cleanup', action='store_true', dest='suppress_cleanup',
                               help='by default peakrdl_python deletes all existing python .py '
                                    'files found in the directory where the package will be'
                                    ' generated. This is normally useful if the user is '
                                    'generating over the top of an existing package and prevents '
                                    'problems when the strucutre of the register map changes. '
                                    'However, if additional python files are added by the user '
                                    '(not recommended) this cleanup will need to be suppressed '
                                    'and managed by the user')
CommandLineParser.add_argument('--copy_libraries', action='store_true', dest='copy_libraries',
                               help='by default peakrdl python copies all the libraries over'
                                    'to the generated package along with the generated code. '
                                    'However, that is potententially problematic when developing'
                                    'and debugging as multiple copies of the libraries can cause'
                                    'confusion. Therefore by default this script does not copy '
                                    'them over.')
CommandLineParser.add_argument('--legacy_block_access', action='store_true',
                               dest='legacy_block_access',
                               help='peakrdl python has two methods to hold blocks of data, the '
                                    'legacy mode based on Array or the new mode using lists')


def build_logging_cong(logfilepath:str):
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'normal': {
                'class': 'logging.Formatter',
                'format': '%(name)-15s %(levelname)-8s %(message)s'
            },
            'root_catch': {
                'class': 'logging.Formatter',
                'format': 'ROOT_LOGGER %(name)-15s %(levelname)-8s  %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'normal',
                'level': 'WARNING'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': logfilepath,
                'mode': 'w',
                'level': 'DEBUG',
                'formatter': 'normal'
            },
            'console_root': {
                'class': 'logging.StreamHandler',
                'formatter': 'root_catch',
            },
        },
        'loggers': {
            'root': {
                'handlers': ['console_root']
            },
            __name__:  {
                'handlers': ['console', 'file'],
                'propagate': True
            },
            'reg_model':  {
                'handlers': ['console', 'file'],
                'propagate': True
            }
        }
    }


if __name__ == '__main__':

    CommandLineArgs = CommandLineParser.parse_args()

    logfile_path = build_logging_cong(CommandLineArgs.output_path / f'{__file__}.log')
    logging.config.dictConfig(logfile_path)

    rdlc = RDLCompiler()

    if CommandLineArgs.ipxact is not None:

        ipxat = IPXACTImporter(rdlc)
        if isinstance(CommandLineArgs.ipxact, list):
            for ipxact_file in CommandLineArgs.ipxact:
                ipxat.import_file(ipxact_file)
        else:
            raise(RuntimeError('not a list'))

    reg_model_class_name = CommandLineArgs.root_node +'_cls'
    sim_class_name = CommandLineArgs.root_node + '_simulator_cls'

    rdlc.compile_file(CommandLineArgs.root_RDL_file)
    spec = rdlc.elaborate(top_def_name=CommandLineArgs.root_node).top

    node_list = []
    for node in spec.descendants(unroll=True):
        node_list.append(node)
        print(node.inst_name)

    exporter = PythonExporter()
    start_time = time.time()
    exporter.export(node=spec, path=str(CommandLineArgs.output_path / 'generate_and_test_output'),
                    asyncoutput=CommandLineArgs.asyncoutput,
                    delete_existing_package_content=not CommandLineArgs.suppress_cleanup,
                    skip_library_copy=not CommandLineArgs.copy_libraries,
                    legacy_block_access=CommandLineArgs.legacy_block_access)
    print(f'generation time {time.time() - start_time}s')

    if not CommandLineArgs.export_only:

        sys.path.append(str(CommandLineArgs.output_path.absolute()))

        if CommandLineArgs.coverage_report:
            cov = Coverage(source_pkgs=[f'generate_and_test_output.{CommandLineArgs.root_node}'] )
            cov.start()

        reg_model_module = __import__( 'generate_and_test_output.' +
            CommandLineArgs.root_node + '.reg_model.' + CommandLineArgs.root_node,
            globals(), locals(), [reg_model_class_name], 0)
        sim_module = __import__( 'generate_and_test_output.' +
            CommandLineArgs.root_node + '.sim.' + CommandLineArgs.root_node,
            globals(), locals(), [sim_class_name], 0)


        dut_cls = getattr(reg_model_module, reg_model_class_name)

        if CommandLineArgs.copy_libraries:
            peakrdl_python_package = __import__('generate_and_test_output.' + CommandLineArgs.root_node + '.lib',
                                                globals(), locals(), ['CallbackSet'], 0)
        else:
            peakrdl_python_package = __import__('src.peakrdl_python.lib',
                                                globals(), locals(), ['CallbackSet'], 0)

        if CommandLineArgs.asyncoutput is True:
            if CommandLineArgs.legacy_block_access is True:
                callbackset_cls = getattr(peakrdl_python_package, 'AsyncCallbackSetLegacy')
            else:
                callbackset_cls = getattr(peakrdl_python_package, 'AsyncCallbackSet')
        else:
            if CommandLineArgs.legacy_block_access is True:
                callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSetLegacy')
            else:
                callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')

        sim_cls = getattr(sim_module, sim_class_name)
        sim = sim_cls(address=0)
        dut = dut_cls(callbacks=callbackset_cls(read_callback=sim.read,
                                                write_callback=sim.write))

        test_suite = TestSuite()
        test_suite.addTests(TestLoader().discover(
            start_dir=str(CommandLineArgs.output_path / 'generate_and_test_output' / CommandLineArgs.root_node / 'tests'),
                            top_level_dir=CommandLineArgs.output_path))
        runner = TextTestRunner()

        result = runner.run(test_suite)
        if CommandLineArgs.coverage_report:
            cov.stop()
            cov.html_report(directory=str(CommandLineArgs.coverage_report_path / CommandLineArgs.root_node))


