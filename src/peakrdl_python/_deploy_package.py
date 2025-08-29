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

Classes to represent the package that is generated
"""
import os
from pathlib import Path
from shutil import copy
from typing import TextIO
from contextlib import contextmanager
from collections.abc import Generator

class PythonPackage:
    """
    Class to represent a python package
    """

    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        """
        path of the package
        """
        return self._path

    def child_package(self, name: str) -> 'PythonPackage':
        """
        provide a child package within the current package

        Args:
            name: name of child package

        Returns:
            None

        """
        return PythonPackage(path=self.path / name)

    def child_path(self, name: str) -> Path:
        """
        return a child path within the package, this can be used of a sub-package or module
        """
        return self.path / name

    @contextmanager
    def init_file_stream(self) -> Generator[TextIO]:
        """
        Generator for a __init__.py file that allows content to be streamed to it
        """
        with self._init_path.open('w', encoding='utf-8') as fid:
            yield fid

    @property
    def _init_path(self) -> Path:
        return self.child_path('__init__.py')

    def _make_empty_init_file(self) -> None:
        with self.init_file_stream() as fid:
            fid.write('pass\n')

    def create_empty_package(self, cleanup: bool) -> None:
        """
        make the package folder (if it does not already exist), populate the __init__.py and
        optionally remove any existing python files

        Args:
            cleanup (bool) : delete any existing python files in the package

        Returns:
            None
        """
        if self.path.exists():
            if cleanup:
                for file in self.path.glob('*.py'):
                    os.remove(file.resolve())
        else:
            self.path.mkdir(parents=True, exist_ok=False)

        self._make_empty_init_file()


class CopiedPythonPackage(PythonPackage):
    """
    Class to represent a python package, which is copied from another
    """

    def __init__(self, path: Path, ref_package: PythonPackage):
        super().__init__(path=path)
        self._ref_package = ref_package

    def create_empty_package(self, cleanup: bool) -> None:

        super().create_empty_package(cleanup=cleanup)

        # copy all the python source code that is part of the library which comes as part of the
        # peakrdl-python to the lib direction of the generated package
        files_in_package = self._ref_package.path.glob('*.py')

        for file_in_package in files_in_package:
            copy(src=file_in_package, dst=self.path)


class _GeneratedRegModelRegistersPackage(PythonPackage):

    def __init__(self, path: Path):
        super().__init__(path=path)

        self.fields = self.child_package('fields')
        self.field_enum = self.child_package('field_enum')

    def create_empty_package(self, cleanup: bool) -> None:

        # make the folder for this package and populate the empty __init__.py
        super().create_empty_package(cleanup=cleanup)
        self.fields.create_empty_package(cleanup=cleanup)
        self.field_enum.create_empty_package(cleanup=cleanup)


class _GeneratedRegModelPackage(PythonPackage):

    def __init__(self, path: Path):
        super().__init__(path=path)

        self.registers = _GeneratedRegModelRegistersPackage(self.child_path('registers'))
        self.memories = self.child_package('memories')

    def create_empty_package(self, cleanup: bool) -> None:
        # make the folder for this package and populate the empty __init__.py
        super().create_empty_package(cleanup=cleanup)
        self.registers.create_empty_package(cleanup=cleanup)
        self.memories.create_empty_package(cleanup=cleanup)


class GeneratedPackage(PythonPackage):
    """
    Class to define the package being generated

    Args:
        include_tests (bool): include the tests package
    """
    template_lib_package = PythonPackage(Path(__file__).parent / 'lib')
    template_sim_lib_package = PythonPackage(Path(__file__).parent / 'sim_lib')

    def __init__(self, path: str, package_name: str, include_tests: bool, include_libraries: bool):
        super().__init__(Path(path) / package_name)

        self._include_tests = include_tests
        self._include_libraries = include_libraries

        if include_libraries:
            self.lib = self.child_ref_package('lib', self.template_lib_package)

        self.reg_model = _GeneratedRegModelPackage(self.child_path('reg_model'))

        if include_tests:
            self.tests = self.child_package('tests')

        if include_libraries:
            self.sim_lib = self.child_ref_package('sim_lib', self.template_sim_lib_package)
        self.sim = self.child_package('sim')

    def child_ref_package(self, name: str, ref_package: PythonPackage) -> 'CopiedPythonPackage':
        """
        provide a child package within the current package

        Args:
            name: name of child package

        Returns:
            None

        """
        return CopiedPythonPackage(path=self.path / name, ref_package=ref_package)

    def create_empty_package(self, cleanup: bool) -> None:

        # make the folder for this package and populate the empty __init__.py
        super().create_empty_package(cleanup=cleanup)

        self.reg_model.create_empty_package(cleanup=cleanup)

        if self._include_tests:
            self.tests.create_empty_package(cleanup=cleanup)
        if self._include_libraries:
            self.lib.create_empty_package(cleanup=cleanup)
            self.sim_lib.create_empty_package(cleanup=cleanup)
        self.sim.create_empty_package(cleanup=cleanup)
