"""
Blah Blah
"""
import os
from pathlib import Path
from shutil import copyfile
from typing import List

import autopep8
import jinja2 as jj

from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode
from systemrdl.rdltypes import OnReadType, OnWriteType, PropertyReference

from .systemrdl_node_utility_functions import get_reg_readable_fields, get_reg_writable_fields, \
    get_array_dim, get_table_block, get_dependent_enum, get_dependent_component, \
    get_field_bitmask_hex_string, get_field_inv_bitmask_hex_string, \
    get_field_max_value_hex_string, get_reg_max_value_hex_string, get_fully_qualified_type_name, \
    uses_enum, fully_qualified_enum_type

file_path = os.path.dirname(__file__)

class PythonExporter:
    """
    PeakRDL Python Exporter class

    Args:
        user_template_dir (str) : Path to a directory where user-defined
            template overrides are stored.
        user_template_context (dict) : Additional context variables to load
            into the template namespace.
    """

    def __init__(self, **kwargs):

        user_template_dir = kwargs.pop("user_template_dir", None)
        self.user_template_context = kwargs.pop("user_template_context",
                                                {})
        self.strict = False  # strict RDL rules rather than helpful implicit
                             # behaviour

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        if user_template_dir:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(user_template_dir),
                jj.FileSystemLoader(os.path.join(file_path, "templates")),
                jj.PrefixLoader({ 'user': jj.FileSystemLoader(user_template_dir),
                                  'base': jj.FileSystemLoader(os.path.join(file_path, "templates"))
                                },
                                delimiter=":")
            ])
        else:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(os.path.join(file_path, "templates")),
                jj.PrefixLoader({'base': jj.FileSystemLoader(os.path.join(file_path, "templates"))},
                                delimiter=":")])

        self.jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined
        )

        # Dictionary of root-level type definitions
        # key = definition type name
        # value = representative object
        #   components, this is the original_def (which can be None in some cases)
        self.namespace_db = {}

    def export(self, node: Node, path: str,
               autoformatoutputs: bool=True) -> List[str]:
        """
        Generated Python Code and Testbench

        Args:
            node (str) : Top-level node to export. Can be the top-level `RootNode` or any
                  internal `AddrmapNode`.
            path (str) : Output package path.
            autoformatoutputs (bool) : If set to True the code will be run through autopep8 to
                clean it up. This can slow down large jobs or mask problems

        Returns:
            List[str] : modules that have been exported:
        """

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        package_path = os.path.join(path, node.inst_name)
        self.create_empty_package(package_path=package_path)

        modules = [node]

        for block in modules:

            context = {
                'print': print,
                'type': type,
                'top_node': block,
                'systemrdlFieldNode': FieldNode,
                'systemrdlRegNode': RegNode,
                'systemrdlRegfileNode': RegfileNode,
                'systemrdlAddrmapNode': AddrmapNode,
                'systemrdlMemNode': MemNode,
                'systemrdlAddressableNode': AddressableNode,
                'OnWriteType': OnWriteType,
                'OnReadType': OnReadType,
                'PropertyReference': PropertyReference,
                'isinstance': isinstance,
                'uses_enum' : uses_enum(block),
                'get_fully_qualified_type_name': get_fully_qualified_type_name,
                'get_array_dim': get_array_dim,
                'get_dependent_component': get_dependent_component,
                'get_dependent_enum': get_dependent_enum,
                'get_fully_qualified_enum_type': fully_qualified_enum_type,
                'get_field_bitmask_hex_string': get_field_bitmask_hex_string,
                'get_field_inv_bitmask_hex_string': get_field_inv_bitmask_hex_string,
                'get_field_max_value_hex_string': get_field_max_value_hex_string,
                'get_reg_max_value_hex_string': get_reg_max_value_hex_string,
                'get_table_block': get_table_block,
                'get_reg_writable_fields': get_reg_writable_fields,
                'get_reg_readable_fields': get_reg_readable_fields

            }

            context.update(self.user_template_context)

            template = self.jj_env.get_template("addrmap.py.jinja")
            module_fqfn = os.path.join(package_path,
                                       'reg_model',
                                       block.inst_name + '.py')
            if autoformatoutputs is True:
                module_code_str = autopep8.fix_code(template.render(context))
                with open(module_fqfn, "w", encoding='utf-8') as fid:
                    fid.write(module_code_str)
            else:
                stream = template.stream(context)
                stream.dump(module_fqfn, encoding='utf-8')

            template = self.jj_env.get_template("addrmap_tb.py.jinja")
            module_tb_fqfn = os.path.join(package_path,
                                          'tests',
                                          'test_' + block.inst_name + '.py')
            if autoformatoutputs is True:
                module_tb_code_str = autopep8.fix_code(template.render(context))
                with open(module_tb_fqfn, "w", encoding='utf-8') as fid:
                    fid.write(module_tb_code_str)
            else:
                stream = template.stream(context)
                stream.dump(module_tb_fqfn, encoding='utf-8')

        copyfile(src=os.path.join(os.path.dirname(__file__),
                                  "templates",
                                  "peakrdl_python_types.py"),
                 dst=os.path.join(package_path,
                                  'reg_model',
                                  'peakrdl_python_types.py'))

        return [m.inst_name for m in modules]

    @staticmethod
    def create_empty_package(package_path:str):
        """
        create the directories and __init__.py files associated with the exported package

        Args:
            package_path: directory for the package output

        Returns:
            None

        """

        Path(package_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'reg_model')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'tests')).mkdir(parents=True, exist_ok=True)

        module_fqfn = os.path.join(package_path, 'reg_model', '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')
        module_fqfn = os.path.join(package_path, 'tests', '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')
        module_fqfn = os.path.join(package_path, '__init__.py')
        with open(module_fqfn, 'w', encoding='utf-8') as fid:
            fid.write('pass\n')
