"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

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

The file is used for making pathological system RDL files for stress testing the tool
"""
import os
from typing import Optional
from pathlib import Path
import string
from dataclasses import dataclass, field
import random

import jinja2 as jj

file_path = os.path.dirname(__file__)

def name_generator():
    """
    name generator that makes names in the form: a, b, c, ... z, aa, ab, ac, ... zz, aaa, aab, ...
    """
    letters = string.ascii_lowercase
    n = 1  # starting length
    while True:
        for i in range(len(letters) ** n):
            # Convert i to base `len(letters)` representation
            name = []
            num = i
            for _ in range(n):
                num, rem = divmod(num, len(letters))
                name.append(letters[rem])
            yield ''.join(reversed(name))
        n += 1  # increase length after exhausting current size




@dataclass
class _PathologicalInstance:
    name_prefix: str
    name:str

    @property
    def child_prefix(self) -> str:
        return self.name_prefix + '_' + self.name

@dataclass
class _PathologicalInstanceWithRegisters(_PathologicalInstance):

    @property
    def registers(self):
        """
        A generator to make a random set of fields
        """
        reg_name = name_generator()
        register_instances_per_addr = random.randint(10, 50)
        for _ in range(register_instances_per_addr):
            yield PathologicalRegisterInstance(name=next(reg_name),
                                               name_prefix=self.child_prefix)

@dataclass
class _PathologicalInstanceWithRegistersAndRegFiles(_PathologicalInstanceWithRegisters):

    regfile_recursion_depth: int = 2

    @property
    def register_files(self):
        """
        A generator to make a random set of register files
        """
        name = name_generator()
        reg_file_instances = random.randint(0, self.regfile_recursion_depth)
        for _ in range(reg_file_instances):
            yield PathologicalRegFileInstance(name=next(name),
                                               name_prefix=self.child_prefix,
                                              regfile_recursion_depth=self.regfile_recursion_depth-1)

@dataclass
class PathologicalRegFileInstance(_PathologicalInstanceWithRegistersAndRegFiles):
    ...

@dataclass
class PathologicalFieldEncodingEntry:
    value: int
    name: str

@dataclass
class PathologicalFieldEncoding:

    width: int

    @property
    def encodings(self):
        enum_name = name_generator()
        pos_values = 2**self.width
        # in order to avoid the number of enumeration entries getting silly, it is capped to
        # 10
        entries = min(pos_values-1, 10)
        for value in random.sample(range(0, pos_values), entries):
            yield PathologicalFieldEncodingEntry(name=next(enum_name), value=value)

@dataclass
class PathologicalFieldInstance(_PathologicalInstance):
    width:int
    encoding: Optional[PathologicalFieldEncoding] = field(init=False)

    def __post_init__(self):
        self.encoding = None
        if random.randint(0, 1) == 1:
            self.encoding = PathologicalFieldEncoding(width=self.width)

@dataclass
class PathologicalRegisterInstance(_PathologicalInstance):

    @property
    def fields(self):
        """
        A generator to make a random set of fields
        """
        field_name = name_generator()
        bits_left = 32
        while bits_left > 0:
            width_next_field = random.randint(1, bits_left)
            bits_left -= width_next_field
            yield PathologicalFieldInstance(name=next(field_name), width=width_next_field,
                                            name_prefix=self.child_prefix)

@dataclass
class PathologicalMemoryInstance(_PathologicalInstanceWithRegisters):

    # the class can have up to 50 registers so needs to have a depth of minium of 50
    depth: int = field(default_factory=lambda: random.randint(50, 50000))


@dataclass
class PathologicalAddrmapInstance(_PathologicalInstanceWithRegistersAndRegFiles):
    addrmap_recursion_depth: int = 1

    @property
    def addrmaps(self):
        """
        A generator to make a random set of addrmaps
        """
        name = name_generator()
        reg_file_instances = random.randint(0, self.addrmap_recursion_depth)
        for _ in range(reg_file_instances):
            yield PathologicalAddrmapInstance(name=next(name),
                                              name_prefix=self.child_prefix,
                                              addrmap_recursion_depth=self.addrmap_recursion_depth - 1)

    @property
    def memories(self):
        """
        A generator to make a random set of fields
        """
        mem_name = name_generator()
        register_instances_per_addr = random.randint(0, 5)
        for _ in range(register_instances_per_addr):
            yield PathologicalMemoryInstance(name=next(mem_name),
                                               name_prefix=self.child_prefix)


class PathologicalRDL:
    """
    Make a very unusual system RDL model to stress test the system

    Args:

    """

    # pylint: disable=too-few-public-methods
    def __init__(self, ):
        self.jj_env = jj.Environment(
            loader=jj.FileSystemLoader(os.path.join(file_path, "templates")),
            undefined=jj.StrictUndefined
        )

    def export_code(self, filename:Path, addrmap_name:str):

        reg_gen = self.register_generator()
        addrmap_gen = self.addrmap_generator()
        memory_gen = self.memory_generator()

        template_context = {
            'top_level_addrmap_name' : addrmap_name,
            'registers' : ( next(reg_gen) for _ in range(10) ),
            'addrmaps' : ( next(addrmap_gen) for _ in range(10) ),
            'memories' : ( next(memory_gen) for _ in range(10) )
        }

        template = self.jj_env.get_template('pathological_template.rdl.jinja')

        with filename.open('w', encoding='utf-8') as fp:
            stream = template.stream(template_context)
            stream.dump(fp)

    @staticmethod
    def register_generator():

        reg_name_generator = name_generator()
        while True:
            yield PathologicalRegisterInstance(name=next(reg_name_generator),
                                               name_prefix='top_level_regs')

    @staticmethod
    def memory_generator():

        mem_name_generator = name_generator()
        while True:
            yield PathologicalMemoryInstance(name=next(mem_name_generator),
                                               name_prefix='top_level_mem')

    @staticmethod
    def addrmap_generator():

        reg_name_generator = name_generator()
        while True:
            yield PathologicalAddrmapInstance(name=next(reg_name_generator),
                                              name_prefix='top_level_addr')


if __name__ == '__main__':

    generator = PathologicalRDL()
    generator.export_code(Path('deep.rdl'), addrmap_name='deep')
