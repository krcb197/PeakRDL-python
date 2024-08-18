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

Defined the compiler classes that are used
"""
from systemrdl.udp import UDPDefinition
from systemrdl.components import Field, Signal


class PythonInstNameUDP(UDPDefinition):
    name = "python_inst_name"
    valid_components = {Field, Signal}
    valid_type = int


class PythonHideUDP(UDPDefinition):
    name = "python_hide"
    valid_components = {Field, Signal}
    valid_type = bool


