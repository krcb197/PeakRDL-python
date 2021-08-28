"""
A set of utility functions that perform supplementary processing on a node in a compiled
system RDL dataset.
"""
from typing import Iterable

import textwrap

from systemrdl.node import Node, RegNode
from systemrdl.node import FieldNode, AddressableNode

def get_fully_qualified_type_name(node: Node) -> str:
    """
    Returns the fully qualified class type name, i.e. with scope prefix
    """
    scope_path = node.inst.get_scope_path(scope_separator='_')

    # TODO if the node is a integer field we can use the base class no
    #      need to generate a unique instance, if it has not documentation
    #      properties

    if node.inst.original_def is None:
        # if the node has no orignal def, it likely cam from IPXACT, the
        # best choice is to mane the type after the fuller qualified path
        fqnode = node.get_path(hier_separator='___',
                               array_suffix='_{index:d}_of_{dim:d}',
                               empty_array_suffix='_of_{dim:d}')
        return fqnode

    # This code handles cases where a field has a reset value such that
    # it end up with the reset value appended to the type name. For the
    # register model we don't care about reset signal and these value
    original_type_name = node.inst.original_def.type_name
    inst_type_name = node.inst.type_name

    if original_type_name is None:
        type_name = inst_type_name
    else:
        type_name = original_type_name

    if (scope_path == '') or (scope_path is None):
        return type_name

    return scope_path + '_' + type_name


def get_array_dim(node: AddressableNode):
    """
    Returns the class type name
    """
    assert node.is_array
    assert len(node.array_dimensions) == 1
    return node.array_dimensions[0]


def get_dependent_component(node: AddressableNode) -> Iterable[Node]:
    """
    iterable of nodes that have a component which is used by a
    descendant, this list is de-duplicated and reversed to components
    are declared before their parents who use them

    :param node: node to analysis
    :return: nodes that are dependent on the specified node
    """
    components_needed = []
    for child_node in node.descendants(in_post_order=True):
        child_orig_def = child_node.inst.original_def

        if child_orig_def is None:
            components_needed.append(child_node)
        else:
            if child_orig_def in components_needed:
                # already covered the component
                continue

            components_needed.append(child_node.inst.original_def)

        yield child_node


def get_dependent_enum(node: AddressableNode):
    """
    iterable of enums which is used by a descendant of the input node,
    this list is de-duplicated

    :param node: node to analysis
    :return: nodes that are dependent on the specified node
    """
    enum_needed = []
    for child_node in node.descendants():
        if isinstance(child_node, FieldNode):
            if 'encode' in child_node.list_properties():
                # found an field with an enumeration

                field_enum = child_node.get_property('encode')
                fully_qualified_enum_name = fully_qualified_enum_type(field_enum, node)

                if fully_qualified_enum_name not in enum_needed:
                    enum_needed.append(fully_qualified_enum_name)
                    yield field_enum


def fully_qualified_enum_type(field_enum, root_node: AddressableNode):
    """
    Returns the fully qualified class type name, for an enum
    """
    if not hasattr(field_enum, '_parent_scope'):
        # this happens if the enum is has been declared in an IPXACT file
        # which is imported
        return field_enum.__name__

    parent_scope = getattr(field_enum, '_parent_scope')

    if root_node.inst.original_def == parent_scope:
        return field_enum.__name__

    dependent_components = get_dependent_component(root_node)

    for component in dependent_components:
        if component.inst.original_def == parent_scope:
            return get_fully_qualified_type_name(component) + '_' + field_enum.__name__

    raise RuntimeError('Failed to find parent node to reference')


def get_table_block(node: Node) -> str:
    """
    Converts the documentation for a systemRDL node into a nicely formated table that can be
    inserted into the docstring of the class

    Args:
        node: node to be analysed

    Returns:
        A string that represents a sphinx table
    """
    row_break = '+-------------------+------------------------------------------------+'
    if ('name' in node.list_properties()) or ('desc' in node.list_properties()):
        table_strs = [row_break,
                      '| System RDL Field  | Value                                          |',
                      '+===================+================================================+']
        if 'name' in node.list_properties():
            name_rows = textwrap.wrap(node.get_property('name'), width=68,
                                      initial_indent="| Name              | ",
                                      subsequent_indent="|                   | ")
            for name_row in name_rows:
                table_strs.append(name_row.ljust(68, ' ') + ' |')
            table_strs.append(row_break)

        if 'desc' in node.list_properties():
            desc_rows = textwrap.wrap(node.get_property('desc'), width=68,
                                      initial_indent="| Description       | ",
                                      subsequent_indent="|                   | ")
            for desc_row in desc_rows:
                table_strs.append(desc_row.ljust(68, ' ') + ' |')
            table_strs.append(row_break)

        return_string = '\n'.join(table_strs)
    else:
        return_string = ''

    return return_string


def get_field_bitmask_hex_string(node: FieldNode) -> str:
    """
    Hexadecimal bitmask for a field

    Args:
        node: node to be analysed

    Returns:
        bitmask as a string prefixed by 0x

    """
    if not isinstance(node, FieldNode):
        raise TypeError('node is not a %s got %s'%(type(FieldNode), type(node)))
    return '0x%X' % sum(2 ** x for x in range(node.low, node.high + 1))


def get_field_inv_bitmask_hex_string(node: FieldNode) -> str:
    """
    Hexadecimal for the inverse bitmask for a field

    Args:
        node: node to be analysed

    Returns:
        inverse bitmask as a string prefixed by 0x

    """
    if not isinstance(node, FieldNode):
        raise TypeError('node is not a %s got %s'%(type(FieldNode), type(node)))
    reg_bitmask = (2 ** (node.parent.size * 8)) - 1
    return '0x%X' % (reg_bitmask ^ sum(2 ** x for x in range(node.low, node.high + 1)))


def get_field_max_value_hex_string(node: FieldNode) -> str:
    """
    Hexadecimal for the maximum value that can be represented in a field

    Args:
        node: node to be analysed

    Returns:
        bitmask as a string prefixed by 0x

    """
    if not isinstance(node, FieldNode):
        raise TypeError('node is not a %s got %s'%(type(FieldNode), type(node)))
    return '0x%X' % ((2 ** (node.high - node.low + 1)) - 1)


def uses_enum(node: AddressableNode) -> bool:
    """
    analyses a node to determine if there are any enumerations used by descendant fields

    Args:
        node: node to analysed

    Returns: True if there are enumeration used, otherwise False
    """
    for child_node in node.descendants():
        if isinstance(child_node, FieldNode):
            if 'encode' in child_node.list_properties():
                return_value = True
                break
    else:
        return_value = False

    return return_value


def get_reg_max_value_hex_string(node: RegNode) -> str:
    """
    Hexadecimal for the maximum value that can be represented in a register

    Args:
        node: node to be analysed

    Returns:
        bitmask as a string prefixed by 0x

    """
    if not isinstance(node, RegNode):
        raise TypeError('node is not a %s got %s'%(type(RegNode), type(node)))
    return '0x%X' % ((2 ** (node.size * 8)) - 1)


def get_reg_writable_fields(node: RegNode) -> Iterable[FieldNode]:
    """
    Iterable that yields all the writable fields from the reg node

    Args:
        node: node to be analysed

    Yields:
        writeable fields

    """
    if not isinstance(node, RegNode):
        raise TypeError('node is not a %s got %s'%(type(RegNode), type(node)))

    for field in node.fields():
        if field.is_sw_writable is True:
            yield field


def get_reg_readable_fields(node: RegNode) -> Iterable[FieldNode]:
    """
    Iterable that yields all the readable fields from the reg node

    Args:
        node: node to be analysed

    Yields:
        readable fields

    """
    if not isinstance(node, RegNode):
        raise TypeError('node is not a %s got %s'%(type(RegNode), type(node)))

    for field in node.fields():
        if field.is_sw_readable is True:
            yield field
