"""
Test exporting this tests a couple of different things:
1. calling the exporter
2. tests some of the export options that would not other be checked with the integration tests get
   checked (notably the show_hidden)
"""
import unittest
import os
import tempfile
import sys
import re
from itertools import chain, permutations, product
from pathlib import Path
from array import array as Array

from contextlib import contextmanager

import jinja2 as jj
from systemrdl import RDLCompileError
from peakrdl.config import schema

from peakrdl_python import PythonExporter
from peakrdl_python import compiler_with_udp_registers
from peakrdl_python.__about__ import __version__ as peakrdl_version
from peakrdl_python.__peakrdl__ import Exporter as PeakRDLPythonExported
from peakrdl_python.lib.utility_functions import get_array_typecode

if sys.version_info[0:2] < (3, 11):
    # Prior to py3.11, tomllib is a 3rd party package
    import tomli as tomllib
else:
    # py3.11 and onwards, tomli was absorbed into the standard library as tomllib
    import tomllib

# this assumes the current file is in the unit_test folder under tests
test_path = Path(__file__).parent.parent
test_cases = test_path / 'testcases'


class TestExportHidden(unittest.TestCase):
    """
    Test class for the export of hidden and force not hidden (show hidden)
    """

    test_case_path = test_cases
    test_case_name = 'hidden_property.rdl'
    test_case_top_level = 'hidden_property'
    test_case_reg_model_cls = test_case_top_level + '_cls'

    @contextmanager
    def build_python_wrappers_and_make_instance(self, show_hidden):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons
            if show_hidden:
                temp_package_name = 'show_hidden'
            else:
                temp_package_name = 'hidden'
            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=show_hidden)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__( temp_package_name + '.' + self.test_case_top_level +
                '.reg_model.' + self.test_case_top_level,
                globals(), locals(), [self.test_case_reg_model_cls], 0)
            dut_cls = getattr(reg_model_module, self.test_case_reg_model_cls)
            peakrdl_python_package = __import__(temp_package_name + '.' +
                                                self.test_case_top_level + '.lib',
                globals(), locals(), ['CallbackSet'], 0)
            callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')
            dummy_operations_module = __import__(temp_package_name + '.' +
                                                 self.test_case_top_level +
                                                 '.sim_lib.dummy_callbacks',
                                    globals(), locals(), ['dummy_read', 'dummy_write'], 0)
            dummy_read = getattr(dummy_operations_module, 'dummy_read')

            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            yield dut_cls(callbacks=callbackset_cls(read_callback=dummy_read))

            sys.path.remove(tmpdirname)

    def test_hidden(self):
        """
        Simple test to make sure that the fields marks as hidden are not generated
        """
        with self.build_python_wrappers_and_make_instance(show_hidden=False) as dut:
            self.assertFalse(dut.reg_hidden_fields.property_unhidden_field.read())
            self.assertFalse(dut.reg_hidden_fields.no_property_field.read())
            with self.assertRaises(AttributeError):
                _ = dut.reg_hidden_fields.property_hidden_field.read()

    def test_show_hidden(self):
        """
        Simple test to make sure that the fields marks as hidden are generated, when show_hidden
        is set
        """
        with self.build_python_wrappers_and_make_instance(show_hidden=True) as dut:
            self.assertFalse(dut.reg_hidden_fields.property_unhidden_field.read())
            self.assertFalse(dut.reg_hidden_fields.no_property_field.read())
            self.assertFalse(dut.reg_hidden_fields.property_hidden_field.read())


class TestExportUDP(unittest.TestCase):
    """
    Tests for including the UDPs in the generated RAL
    """

    test_case_path = test_cases
    test_case_name = 'user_defined_properties.rdl'
    test_case_top_level = 'user_defined_properties'
    test_case_reg_model_cls = test_case_top_level + '_cls'

    @contextmanager
    def build_wrappers_and_import(self, udp_list:list[str]):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons
            temp_package_name = 'dir_' + str(hash('_'.join(udp_list)))
            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            user_defined_properties_to_include=udp_list)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__( temp_package_name + '.' + self.test_case_top_level +
                '.reg_model.' + self.test_case_top_level,
                globals(), locals(), [self.test_case_reg_model_cls], 0)
            dut_cls = getattr(reg_model_module, self.test_case_reg_model_cls)
            peakrdl_python_package = __import__(temp_package_name + '.' +
                                                self.test_case_top_level + '.lib',
                globals(), locals(), ['CallbackSet'], 0)
            callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')
            dummy_operations_module = __import__(temp_package_name + '.' +
                                                 self.test_case_top_level +
                                                 '.sim_lib.dummy_callbacks',
                                    globals(), locals(), ['dummy_read', 'dummy_write'], 0)
            dummy_read = getattr(dummy_operations_module, 'dummy_read')

            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            yield dut_cls(callbacks=callbackset_cls(read_callback=dummy_read))

            sys.path.remove(tmpdirname)

    def test_str_property(self):
        """
        Check a str property is correctly generated in all the places, this is based on a the
        systemRDL test case having set the property to the fully qualified node name
        """

        # in the code the property str_property_to_include is always sent to the fully qualified
        # node name, arrays have to have homogeneous properties in the python systemRDL compiler
        # so the array designators are not present in the UDP

        def walk_child_registers(node):
            for register in node.get_registers(unroll=True):
                self.assertIn('str_property_to_include',
                              register.udp,
                              msg=f'{register.full_inst_name} missing str_property_to_include')
                self.assertEqual(register.udp['str_property_to_include'],
                                 re.sub(r'\[\d+\]','',register.full_inst_name))
                for field in register.fields:
                    self.assertEqual(field.udp['str_property_to_include'],
                                     re.sub(r'\[\d+\]','',field.full_inst_name))

        def walk_child_sections(node):
            for section in node.get_sections(unroll=True):
                self.assertEqual(section.udp['str_property_to_include'],
                                 re.sub(r'\[\d+\]','',section.full_inst_name))
                walk_child_sections(section)
                walk_child_registers(section)

        with self.build_wrappers_and_import(udp_list=['str_property_to_include']) as dut:
            self.assertEqual(dut.udp['str_property_to_include'], dut.full_inst_name)
            walk_child_sections(dut)
            walk_child_registers(dut)

    def test_selective_property_export(self):
        """
        Check all the permutations of the available UDPs to make sure only the correct ones get
        generated in each case
        """

        full_property_list = ['bool_property_to_include',
                              'struct_property_to_include',
                              'enum_property_to_include',
                              'int_property_to_include',
                              'str_property_to_include']
        for udp_to_include in chain.from_iterable(
                [permutations(full_property_list, r) for r in range(len(full_property_list))]):
            with self.subTest(udp_to_include=udp_to_include), \
                    self.build_wrappers_and_import(udp_list=list(udp_to_include)) as dut:
                for udp in full_property_list:
                    if udp in list(udp_to_include):
                        self.assertIn(udp, dut.reg_a.field_a.udp)
                    else:
                        self.assertNotIn(udp, dut.reg_a.field_a.udp)

                self.assertNotIn('int_property_to_exclude', dut.reg_a.field_a.udp)


class TestRegexExportHidden(unittest.TestCase):
    """
    Test class for the export of hidden and force not hidden (show hidden)
    """

    test_case_path = test_cases
    test_case_name = 'reserved_elements.rdl'
    test_case_top_level = 'reserved_elements'
    test_case_reg_model_cls = test_case_top_level + '_cls'

    @contextmanager
    def build_python_wrappers_and_make_instance(self, hidden_inst_name_regex):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons
            temp_package_name = 'dir_' + str(hash(hidden_inst_name_regex))
            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False,
                            hidden_inst_name_regex=hidden_inst_name_regex)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__( temp_package_name + '.' + self.test_case_top_level +
                '.reg_model.' + self.test_case_top_level,
                globals(), locals(), [self.test_case_reg_model_cls], 0)
            dut_cls = getattr(reg_model_module, self.test_case_reg_model_cls)
            peakrdl_python_package = __import__(temp_package_name + '.' +
                                                self.test_case_top_level + '.lib',
                globals(), locals(), ['CallbackSet'], 0)
            callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')
            dummy_operations_module = __import__(temp_package_name + '.' +
                                                 self.test_case_top_level +
                                                 '.sim_lib.dummy_callbacks',
                                    globals(), locals(), ['dummy_read', 'dummy_write'], 0)
            dummy_read = getattr(dummy_operations_module, 'dummy_read')

            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            yield dut_cls(callbacks=callbackset_cls(read_callback=dummy_read))

            sys.path.remove(tmpdirname)

    def test_hide_top(self):
        """
        This test should hide any node with a whole name match on 'RSVD':register, field, regfile,
        memory or addressmap. However, items in the form 'array_RSVD' should not get hidden
        """
        regex = r'reserved_elements'
        with self.assertRaises(RuntimeError):
            with self.build_python_wrappers_and_make_instance(hidden_inst_name_regex=regex):
                pass

    def test_hide_nothing(self):
        """
        This test should hide any node with a whole name match on 'RSVD':register, field, regfile,
        memory or addressmap. However, items in the form 'array_RSVD' should not get hidden
        """
        with self.build_python_wrappers_and_make_instance(hidden_inst_name_regex=None) as dut:

            self.assertIn('RSVD', dir(dut))
            self.assertIn('reserved', dir(dut))
            self.assertIn('show', dir(dut))
            self.assertIn('RSVD', dir(dut.show))
            self.assertIn('reserved', dir(dut.show))
            self.assertIn('show', dir(dut.show))

    # pylint: disable-next=invalid-name
    def test_hid_RSVD(self):
        """
        This test should hide any node with a whole name match on 'RSVD':register, field, regfile,
        memory or addressmap. However, items in the form 'array_RSVD' should not get hidden
        """
        regex = r'(?:[\w_\[\]]+\.)+RSVD'
        with self.build_python_wrappers_and_make_instance(hidden_inst_name_regex=regex) as dut:

            self.assertNotIn('RSVD', dir(dut))
            self.assertIn('reserved', dir(dut))
            self.assertIn('show', dir(dut))
            self.assertNotIn('RSVD', dir(dut.show))
            self.assertIn('reserved', dir(dut.show))
            self.assertIn('show', dir(dut.show))

    # pylint: disable-next=invalid-name
    def test_hid_RSVD_or_reserved(self):
        """
        This test should hide any node with a whole name match on 'RSVD':register, field, regfile,
        memory or addressmap. However, items in the form 'array_RSVD' should not get hidden
        """
        regex = r'(?:[\w_\[\]]+\.)+(RSVD|reserved)'
        with self.build_python_wrappers_and_make_instance(hidden_inst_name_regex=regex) as dut:

            self.assertNotIn('RSVD', dir(dut))
            self.assertNotIn('reserved', dir(dut))
            self.assertIn('show', dir(dut))
            self.assertNotIn('RSVD', dir(dut.show))
            self.assertNotIn('reserved', dir(dut.show))
            self.assertIn('show', dir(dut.show))
            self.assertNotIn('RSVD', dir(dut.array_show[0]))
            self.assertNotIn('reserved', dir(dut.array_show[0]))
            self.assertIn('show', dir(dut.array_show[0]))


class TestUDPDeclarations(unittest.TestCase):
    """
    Test class for the export of hidden and force not hidden (show hidden)
    """

    @contextmanager
    def build_python_wrappers_and_make_instance(self, system_rdl_content, top_name):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """

        rdlc = compiler_with_udp_registers()

        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'system_rdl.rdl'), 'w', encoding='utf-8') as fid:
                fid.write(system_rdl_content)

            rdlc.compile_file(os.path.join(tmpdirname, 'system_rdl.rdl'))
            spec = rdlc.elaborate(top_def_name=top_name).top

            yield spec


    def test_bad_property_type_declaration(self):
        """
        Test that the property not being defined as a string causes a problem
        """
        system_rdl_code = \
            'property python_inst_name { type = number; ' +\
            'component = addrmap | regfile | reg | field | mem; };' +\
            'addrmap name_of_addrmap { ' +\
            'reg {' +\
            '    python_inst_name="overidden_reg_a";'+\
            '    field { python_inst_name="overridden_field_a";  } field_a[31:0];'+\
            '} reg_a;'+\
            '};'

        with self.assertRaises(RDLCompileError):
            with self.build_python_wrappers_and_make_instance(system_rdl_content=system_rdl_code,
                                                                  top_name='name_of_addrmap'):
                pass

    def test_bad_property_component_declaration(self):
        """
        Test that the property not being defined as a string causes a problem
        """
        system_rdl_code = \
            'property python_inst_name { type = number; component = signal | reg; };' +\
            'addrmap name_of_addrmap { ' +\
            'reg {' +\
            '    python_inst_name="overidden_reg_a";'+\
            '    field { python_inst_name="overridden_field_a";  } field_a[31:0];'+\
            '} reg_a;'+\
            '};'

        with self.assertRaises(RDLCompileError):
            with self.build_python_wrappers_and_make_instance(system_rdl_content=system_rdl_code,
                                                                  top_name='name_of_addrmap'):
                pass

    def test_bad_property_name_declaration(self):
        """
        Test that the property setting to a python keyname causes an error
        """
        system_rdl_code = \
            'property python_inst_name { type = number; component = signal | reg; };' +\
            'addrmap name_of_addrmap { ' +\
            'reg {' +\
            '    python_inst_name="in";'+\
            '    field { python_inst_name="overridden_field_a";  } field_a[31:0];'+\
            '} reg_a;'+\
            '};'

        with self.assertRaises(RDLCompileError):
            with self.build_python_wrappers_and_make_instance(system_rdl_content=system_rdl_code,
                                                                  top_name='name_of_addrmap'):
                pass


class TestAlternativeTemplates(unittest.TestCase):
    """
    Test class for the export of hidden and force not hidden (show hidden)
    """

    test_case_path = test_cases
    test_case_name = 'simple.rdl'
    test_case_top_level = 'simple'
    test_case_reg_model_cls = test_case_top_level + '_cls'

    @contextmanager
    def build_python_wrappers_and_make_instance(self, template_path, context=None):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        if context is None:
            exporter = PythonExporter(user_template_dir=template_path)
        else:
            exporter = PythonExporter(user_template_dir=template_path,
                                      user_template_context=context)

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons
            temp_package_name = 'dir_' + str(hash(template_path))
            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=False,
                            show_hidden=False)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__( temp_package_name + '.' + self.test_case_top_level +
                '.reg_model',
                globals(), locals(), [self.test_case_top_level], 0)


            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            yield reg_model_module

            sys.path.remove(tmpdirname)

    def test_schema(self):
        """
        test the schema in the __peakrdl__ exports will process correctly
        """

        _ = schema.normalize(PeakRDLPythonExported.cfg_schema)


    def test_static_template(self):
        """
        This test uses the static templates to test building with alternative headers and then
        reads the documentation back out of the built module
        """
        toml_path = test_cases.with_name('alternative_templates_toml')
        toml_file =  toml_path / 'peakrdl.toml'
        with open(toml_file , 'rb') as fid:
            config = tomllib.load(fid)

        template_path = toml_path / Path(config['python']['user_template_dir'])

        # build the same jinja template outside this confirms it is valid
        loader = jj.ChoiceLoader([
            jj.FileSystemLoader(template_path),
            jj.PrefixLoader({'base': jj.FileSystemLoader(template_path)}, delimiter=":")])
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined
        )
        template = jj_env.get_template('header.py.jinja')
        result = template.render({'top_node':{'inst_name':'simple'},
                                  'version': peakrdl_version })

        with self.build_python_wrappers_and_make_instance(template_path=template_path) as dut:
            doc_string = dut.simple.__doc__

        self.assertEqual('"""' + doc_string + '"""',result)

    def test_dynamic_template(self):
        """
        This test uses the templates with dynamic content to test building with alternative
        headers and then reads the documentation back out of the built module
        """
        toml_path = test_cases.with_name('alternative_templates_dynamic_toml')
        toml_file =  toml_path / 'peakrdl.toml'
        with open(toml_file , 'rb') as fid:
            config = tomllib.load(fid)

        # peakrdl always interprets the paths as being relative to the toml files itself
        template_path = toml_path / Path(config['python']['user_template_dir'])
        context = config['python']['user_template_context']

        with self.build_python_wrappers_and_make_instance(template_path=template_path,
                                                          context=context) as dut:
            doc_string = dut.simple.__doc__

        # build the same jinja template outside
        loader = jj.ChoiceLoader([
            jj.FileSystemLoader(template_path),
            jj.PrefixLoader({'base': jj.FileSystemLoader(template_path)}, delimiter=":")])
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined
        )
        template = jj_env.get_template('header.py.jinja')
        context.update({'top_node':{'inst_name':'simple'},
                                  'version': peakrdl_version })
        result = template.render(context)

        self.assertEqual('"""' + doc_string + '"""',result)


class TestCallbackAndLegacyTemplates(unittest.TestCase):
    """
    Test class for the export of hidden and force not hidden (show hidden)
    """
    test_case_path = test_cases
    test_case_name = 'simple.rdl'
    test_case_top_level = 'simple'
    test_case_reg_model_cls = test_case_top_level + '_cls'

    @contextmanager
    def generate_dut(self,
                     legacy_block_access: bool,
                     legacy_call_back: bool,
                     legacy_dummy_block_read: bool):
        """
        Context manager to build the python wrappers for a value of show_hidden, then import them
        and clean up afterwards
        """
        # pylint: disable=too-many-locals

        # compile the code for the test
        rdlc = compiler_with_udp_registers()
        rdlc.compile_file(os.path.join(self.test_case_path, self.test_case_name))
        spec = rdlc.elaborate(top_def_name=self.test_case_top_level).top

        exporter = PythonExporter()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # the temporary package, within which the real package is placed is needed to ensure
            # that there are two separate entries in the python import cache and this avoids the
            # test failing for strange reasons

            temp_package_name = 'dir_'
            if legacy_block_access:
                temp_package_name += '_legacy_build_option'
            else:
                temp_package_name += '_normal_build_option'
            if legacy_call_back:
                temp_package_name += '_legacy_call_back'
            else:
                temp_package_name += '_normal_call_back'
            if legacy_dummy_block_read:
                temp_package_name += '_legacy_dummy_read'
            else:
                temp_package_name += '_normal_dummy_read'

            fq_package_path = os.path.join(tmpdirname, temp_package_name)
            os.makedirs(fq_package_path)
            with open(os.path.join(fq_package_path, '__init__.py'), 'w', encoding='utf-8') as fid:
                fid.write('pass\n')

            exporter.export(node=spec,
                            path=fq_package_path,
                            asyncoutput=False,
                            delete_existing_package_content=False,
                            skip_library_copy=False,
                            skip_test_case_generation=True,
                            legacy_block_access=legacy_block_access,
                            show_hidden=False)

            # add the temp directory to the python path so that it can be imported from
            sys.path.append(tmpdirname)

            reg_model_module = __import__(temp_package_name + '.' + self.test_case_top_level +
                                          '.reg_model.' + self.test_case_top_level,
                                          globals(), locals(), [self.test_case_reg_model_cls], 0)
            dut_cls = getattr(reg_model_module, self.test_case_reg_model_cls)
            peakrdl_python_package = __import__(temp_package_name + '.' +
                                                self.test_case_top_level + '.lib',
                                                globals(), locals(), ['CallbackSet'], 0)
            if legacy_call_back:
                callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSetLegacy')
            else:
                callbackset_cls = getattr(peakrdl_python_package, 'NormalCallbackSet')
            dummy_operations_module = __import__(temp_package_name + '.' +
                                                 self.test_case_top_level +
                                                 '.sim_lib.dummy_callbacks',
                                                 globals(), locals(),
                                                 ['dummy_read_block',
                                                  'dummy_read_block_legacy'], 0)
            if legacy_dummy_block_read:
                dummy_read = getattr(dummy_operations_module, 'dummy_read_block_legacy')
                dummy_write = getattr(dummy_operations_module, 'dummy_write_block_legacy')
            else:
                dummy_read = getattr(dummy_operations_module, 'dummy_read_block')
                dummy_write = getattr(dummy_operations_module, 'dummy_write_block')

            # no read/write are attempted so this can yield out a version with no callbacks
            # configured
            yield dut_cls(callbacks=callbackset_cls(read_block_callback=dummy_read,
                                                    write_block_callback=dummy_write))

            sys.path.remove(tmpdirname)

    def test_combinations(self):
        """
        Test all the expected permutations of legacy and normal mixtures
        """

        for legacy_dummy_block, legacy_call_back, legacy_block_access in product([True, False],
                                                                                 [True, False],
                                                                                 [True, False]):
            with self.generate_dut(legacy_dummy_block_read=legacy_dummy_block,
                                   legacy_call_back=legacy_call_back,
                                   legacy_block_access=legacy_block_access) as dut, \
                    self.subTest(legacy_dummy_block_read=legacy_dummy_block,
                                 legacy_call_back=legacy_call_back,
                                 legacy_block_access=legacy_block_access):

                # single register accesses should be function in all cases
                self.assertEqual(dut.simple_reg_a.read(), 0)

                # block access will fail in some cases
                if legacy_call_back != legacy_dummy_block:
                    with self.assertRaises(TypeError):
                        _ = dut.simple_memory_a.read(0,4)
                else:
                    mem_block_read = dut.simple_memory_a.read(0,4)
                    if legacy_block_access:
                        self.assertIsInstance(mem_block_read, Array)
                    else:
                        self.assertIsInstance(mem_block_read, list)
                    self.assertEqual(len(mem_block_read), 4)
                    self.assertEqual(mem_block_read[0], 0)

                if legacy_block_access:
                    dut.simple_memory_a.write(0,
                                              Array(get_array_typecode(
                                                  dut.simple_memory_a.width),
                                                    [0, 0, 0, 0]))
                else:
                    dut.simple_memory_a.write(0, [0, 0, 0, 0])


if __name__ == '__main__':

    unittest.main()
