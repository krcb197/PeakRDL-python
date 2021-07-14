
import os
from pathlib import Path
from shutil import copyfile
from typing import List

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

        #add_filter(self.full_array_dimensions)
        #add_filter(self.full_array_ranges)
        #add_filter(self.full_array_indexes)
        #add_filter(self.bit_range)

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
            Output file.
        """


        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        # find all the addrmap types in the, these will be converted to seperate files
        modules = []
        for desc in node.descendants():
            if ((isinstance(desc, (RegfileNode, RegNode))) and
                    isinstance(desc.parent, AddrmapNode)):
                if desc.parent not in modules:
                    modules.append(desc.parent)

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
                'get_array_dim': self._get_array_dim,
                'get_unique_scoped_component': self._get_unique_scoped_component,
                'get_unique_scoped_enums': self._get_unique_scoped_enums
            }

            context.update(self.user_template_context)

            # ensure directory exists
            Path(path).mkdir(parents=True, exist_ok=True)

            template = self.jj_env.get_template("addrmap.py.jinja")
            stream = template.stream(context)
            stream.dump(os.path.join(path, node.inst_name + '.py'))
            #template = self.jj_env.get_template("addrmap_tb.sv")
            #stream = template.stream(context)
            #stream.dump(os.path.join(path, node.inst_name + '_tb.sv'))
            #template = self.jj_env.get_template("tb.cpp")
            #stream = template.stream(context)
            #stream.dump(os.path.join(path, node.inst_name + '_tb.cpp'))

        copyfile(src=os.path.join(os.path.dirname(__file__), "templates", "peakrdl_python_types.py"),
                 dst=os.path.join(path, "peakrdl_python_types.py" ))

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

    def _get_array_dim(self, node: AddressableNode):
        """
        Returns the class type name
        """
        assert node.is_array
        assert len(node.array_dimensions) == 1
        return node.array_dimensions[0]

    def _get_unique_scoped_component(self, node: AddressableNode):

        """
        return a list of nodes that have a component which needs to be declared in the scope of the current node.
        This list is de-duplicated

        :param node:
        :return: list(node)
        """
        node_component = node.inst.original_def

        components_needed = []
        for child_node in node.descendants():
            child_node_component_scope = child_node.inst.original_def.parent_scope
            if child_node_component_scope == node_component:
                if child_node.inst.original_def in components_needed:
                    # already covered the component
                    continue

                components_needed.append(child_node.inst.original_def)

                yield child_node

    def _get_unique_scoped_enums(self, node: AddressableNode):

        node_component = node.inst.original_def

        enum_needed = []
        for child_node in node.descendants():
            if isinstance(child_node, FieldNode):
                if 'encode' in child_node.list_properties():
                    # found an field with an enumeration

                    field_enum = child_node.get_property('encode')
                    feild_enum_parent = field_enum._parent_scope

                    if feild_enum_parent == node_component:
                        #needs to be declared at this level

                        if field_enum.__name__ not in enum_needed:
                            enum_needed.append(field_enum.__name__)
                            yield field_enum

    def _uses_enum(self, node: AddressableNode):
        for child_node in node.descendants():
            if isinstance(child_node, FieldNode):
                if 'encode' in child_node.list_properties():
                    return True
        else:
            return False



















