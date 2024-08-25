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

script to check that a peakrdl-python package generated has the correct headers based on the
toml file in this folder
"""

import argparse
import pathlib
import sys

import jinja2 as jj

from peakrdl_python.__about__ import __version__ as peakrdl_version

if sys.version_info[0:2] < (3, 11):
    # Prior to py3.11, tomllib is a 3rd party package
    import tomli as tomllib
else:
    # py3.11 and onwards, tomli was absorbed into the standard library as tomllib
    import tomllib



CommandLineParser = argparse.ArgumentParser(description='Test the header generation')
CommandLineParser.add_argument('--generated_package_location', dest='package_location',
                               type=pathlib.Path, required=True)
CommandLineParser.add_argument('--top_name', dest='top_name',
                               type=str, required=True)


if __name__ == '__main__':

    CommandLineArgs = CommandLineParser.parse_args()

    toml_path = pathlib.Path(__file__).parent
    toml_file = toml_path / 'peakrdl.toml'
    with open(toml_file, 'rb') as fid:
        config = tomllib.load(fid)

    # peakrdl always interprets the paths as being relative to the toml files itself
    template_path = toml_path / pathlib.Path(config['python']['user_template_dir'])
    context = {}

    # build the same jinja template outside
    loader = jj.ChoiceLoader([
        jj.FileSystemLoader(template_path),
        jj.PrefixLoader({'base': jj.FileSystemLoader(template_path)}, delimiter=":")])
    jj_env = jj.Environment(
        loader=loader,
        undefined=jj.StrictUndefined
    )
    template = jj_env.get_template('header.py.jinja')
    context.update({'top_node': {'inst_name': CommandLineArgs.top_name},
                    'version': peakrdl_version})
    result = template.render(context)

    sys.path.append(str(CommandLineArgs.package_location))

    reg_model_package = __import__(CommandLineArgs.top_name +
                                  '.reg_model',
                                  globals(), locals(), [CommandLineArgs.top_name], 0)
    reg_model_top_module = getattr(reg_model_package, CommandLineArgs.top_name)

    module_doc_string = '"""' + reg_model_top_module.__doc__ + '"""'

    print('\n\ngenerated module docstring:')
    print(module_doc_string)
    print('\n\nlocally generated template:')
    print(result)

    assert module_doc_string == result, 'strings do not match'
    print('\n\n\n strings match \n *************** \n     PASS \n ***************')

