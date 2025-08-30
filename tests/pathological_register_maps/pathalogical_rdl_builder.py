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
class PathologicalFieldEnumInstanceEntry:
    name: str
    value: int

@dataclass
class PathologicalFieldEnumInstance:
    width: int

    @property
    def encodings(self):
        enum_name = name_generator()
        pos_values = 2**self.width
        # make up to 10 possible_enumeration_values
        for value in range(min(pos_values, 10)):
            yield PathologicalFieldEnumInstanceEntry(name=next(enum_name), value=value)

@dataclass
class PathologicalFieldInstance:
    name:str
    width:int
    encoding: Optional[PathologicalFieldEnumInstance] = field(init=False)

    def __post_init__(self):
        self.encoding = None
        if random.randint(0, 1) == 1:
            self.encoding = PathologicalFieldEnumInstance(width=self.width)

@dataclass
class PathologicalRegisterInstance:
    name:str

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
            yield PathologicalFieldInstance(name=next(field_name), width=width_next_field)

@dataclass
class PathologicalAddrmapInstance:
    name:str

    @property
    def registers(self):
        """
        A generator to make a random set of fields
        """
        reg_name = name_generator()
        register_instances_per_addr = random.randint(10, 50)
        for _ in range(register_instances_per_addr):
            yield PathologicalRegisterInstance(name=next(reg_name))



def register_generator():

    reg_name_generator = name_generator()
    while True:
        yield PathologicalRegisterInstance(name=next(reg_name_generator))


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

        reg_gen = register_generator()

        template_context = {
            'top_level_addrmap_name' : addrmap_name,
            'registers' : ( next(reg_gen) for _ in range(300) )
        }

        template = self.jj_env.get_template('pathological_template.rdl.jinja')

        with filename.open('w', encoding='utf-8') as fp:
            stream = template.stream(template_context)
            stream.dump(fp)


if __name__ == '__main__':

    generator = PathologicalRDL()
    generator.export_code(Path('deep.rdl'), addrmap_name='deep')
