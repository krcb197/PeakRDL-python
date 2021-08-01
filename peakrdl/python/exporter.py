
import os
from pathlib import Path
from shutil import copyfile
from typing import List

import autopep8

import jinja2 as jj
from systemrdl.node import RootNode, Node, RegNode, AddrmapNode, RegfileNode
from systemrdl.node import FieldNode, MemNode, AddressableNode
from systemrdl.rdltypes import AccessType, OnReadType, OnWriteType, InterruptType, PropertyReference

class PythonExporter:

    def __init__(self, **kwargs):
        """
        Constructor for the Python Exporter class
        Parameters
        ----------
        user_template_dir: str
            Path to a directory where user-defined template overrides are stored.
        user_template_context: dict
            Additional context variables to load into the template namespace.
        """
        user_template_dir = kwargs.pop("user_template_dir", None)
        self.user_template_context = kwargs.pop("user_template_context", dict())
        #self.signal_overrides = {}
        self.strict = False  # strict RDL rules rather than helpful impliciti behaviour

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        if user_template_dir:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(user_template_dir),
                jj.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
                jj.PrefixLoader({
                    'user': jj.FileSystemLoader(user_template_dir),
                    'base': jj.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))
                }, delimiter=":")
            ])
        else:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
                jj.PrefixLoader({
                    'base': jj.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))
                }, delimiter=":")
            ])

        self.jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined
        )

        # Define custom filters and tests
        def add_filter(func):
            self.jj_env.filters[func.__name__] = func

        def add_test(func, name=None):
            name = name or func.__name__.replace('is_', '')
            self.jj_env.tests[name] = func

        # Dictionary of root-level type definitions
        # key = definition type name
        # value = representative object
        #   components, this is the original_def (which can be None in some cases)
        self.namespace_db = {}

    def export(self, node: Node, path: str, **kwargs):
        """
        Perform the export!
        Parameters
        ----------
        node: systemrdl.Node
            Top-level node to export. Can be the top-level `RootNode` or any
            internal `AddrmapNode`.
        path: str
            Output package path.
        """

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        package_path = os.path.join(path, node.inst_name)
        Path(package_path).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'reg_model')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(package_path, 'tests')).mkdir(parents=True, exist_ok=True)

        """
        The long term plan is to put separate addr_maps in separate files but this
        has proven to be very complex to implement so has been shelved for now
        in favour of a single file approach
        
        # find all the addrmap types in the, these will be converted to seperate files
        modules = []
        for desc in node.descendants():
            if ((isinstance(desc, (RegfileNode, RegNode, AddrmapNode))) and
                    isinstance(desc.parent, AddrmapNode)):
                if desc.parent not in modules:
                    modules.append(desc.parent)
        """
        modules = [node]

        for block in modules:

            block.uses_enum = self._uses_enum(block)

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
                #'SignalNode': SignalNode,
                'OnWriteType': OnWriteType,
                'OnReadType': OnReadType,
                'PropertyReference': PropertyReference,
                'isinstance': isinstance,
                #'full_idx': self._full_idx,
                'get_inst_name': self._get_inst_name,
                'get_type_name': self._get_type_name,
                'get_fully_qualified_type_name': self._get_fully_qualified_type_name,
                'get_array_dim': self._get_array_dim,
                'get_dependent_component': self._get_dependent_component,
                'get_dependent_enum': self._get_dependent_enum,
                'get_fully_qualified_enum_type': self._fully_qualified_enum_type,
                'get_field_bitmask_hex_string' : self._get_field_bitmask_hex_string,
                'get_field_inv_bitmask_hex_string' : self._get_field_inv_bitmask_hex_string,
                'get_reg_max_value_hex_string' : self._get_reg_max_value_hex_string
            }

            context.update(self.user_template_context)

            template = self.jj_env.get_template("addrmap.py.jinja")
            module_code_str = autopep8.fix_code(template.render(context))
            module_fqfn = os.path.join(package_path,
                                       'reg_model',
                                       block.inst_name + '.py')
            with open(module_fqfn, "w") as fid:
                fid.write(module_code_str)

            template = self.jj_env.get_template("addrmap_tb.py.jinja")
            module_tb_code_str = autopep8.fix_code(template.render(context))
            module_tb_fqfn = os.path.join(package_path,
                                       'tests',
                                       'test_'+ block.inst_name + '.py')
            with open(module_tb_fqfn, "w") as fid:
                fid.write(module_tb_code_str)

            #template = self.jj_env.get_template("tb.cpp")
            #stream = template.stream(context)
            #stream.dump(os.path.join(path, node.inst_name + '_tb.cpp'))

        copyfile(src=os.path.join(os.path.dirname(__file__), "templates", "peakrdl_python_types.py"),
                 dst=os.path.join(os.path.join(package_path, 'reg_model'), "peakrdl_python_types.py" ))

        with open(os.path.join(package_path, 'reg_model','__init__.py'), 'w') as fid:
            fid.write('pass\n')
        with open(os.path.join(package_path, 'tests','__init__.py'), 'w') as fid:
            fid.write('pass\n')
        with open(os.path.join(package_path, '__init__.py'), 'w') as fid:
             fid.write('pass\n')

        return [self._get_inst_name(m) for m in modules]

    def _get_inst_name(self, node: Node) -> str:
        """
        Returns the class instance name
        """
        return node.inst_name

    def _get_type_name(self, node: Node) -> str:
        """
        Returns the class type name
        """
        return node.type_name

    def _get_fully_qualified_type_name(self, node: Node) -> str:
        """
        Returns the fully qualified class type name, i.e. with scope prefix
        """
        scope_path = node.inst.get_scope_path(scope_separator='_')


        # This code handles cases where a field has a reset value such that
        # it end up with the reset value appended to the type name. For the
        # register model we don't care about reset signal and these value
        original_type_name = node.inst.original_def.type_name
        inst_type_name = node.inst.type_name

        if original_type_name is None:
            type_name = inst_type_name
        else:
            type_name = original_type_name

        if scope_path == '':
            return type_name
        else:
            return scope_path + '_' + type_name

    def _get_array_dim(self, node: AddressableNode):
        """
        Returns the class type name
        """
        assert node.is_array
        assert len(node.array_dimensions) == 1
        return node.array_dimensions[0]

    def _get_dependent_component(self, node: AddressableNode):

        """
        return a list of nodes that have a component which is used by a
        decendent, this list is de-duplicated and reversed to components
        are declared before their parents who use them

        :param node:
        :return: list(node)
        """
        node_component = node.inst.original_def

        components_needed = []
        for child_node in node.descendants(in_post_order=True):
            child_orig_def = child_node.inst.original_def
            if child_orig_def in components_needed:
                # already covered the component
                continue

            components_needed.append(child_node.inst.original_def)

            yield child_node

    def _get_dependent_enum(self, node: AddressableNode):

        enum_needed = []
        for child_node in node.descendants():
            if isinstance(child_node, FieldNode):
                if 'encode' in child_node.list_properties():
                    # found an field with an enumeration

                    field_enum = child_node.get_property('encode')
                    fully_qualified_enum_name = self._fully_qualified_enum_type( field_enum, node)

                    if fully_qualified_enum_name not in enum_needed:
                        enum_needed.append(fully_qualified_enum_name)
                        yield field_enum

    def _fully_qualified_enum_type(self, field_enum, root_node: AddressableNode):

        assert hasattr(field_enum, '_parent_scope')

        if root_node.inst.original_def == field_enum._parent_scope:
            return field_enum.__name__

        dependent_components = self._get_dependent_component(root_node)

        for component in dependent_components:
            if component.inst.original_def == field_enum._parent_scope:
                return self._get_fully_qualified_type_name(component) + '_' + field_enum.__name__

        raise RuntimeError('Failed to find parent node to reference')



    def _get_field_bitmask_hex_string(self, node: FieldNode) -> str:
        return '0x%X' % sum(2**x for x in range(node.lsb, node.msb+1))


    def _get_field_inv_bitmask_hex_string(self, node: FieldNode) -> str:
        reg_bitmask = (2 ** (node.parent.size * 8))-1
        return '0x%X' % (reg_bitmask ^ sum(2**x for x in range(node.lsb, node.msb+1)))

    def _uses_enum(self, node: AddressableNode):
        for child_node in node.descendants():
            if isinstance(child_node, FieldNode):
                if 'encode' in child_node.list_properties():
                    return True
        else:
            return False

    def _get_reg_max_value_hex_string(self, node: RegNode) -> str:
        return '0x%X' % ((2 ** (node.size * 8))-1)



















