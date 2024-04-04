"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values. The text file has the following format:

    [First line] A dictionary describing the environment
    [n-th line] The n-th instruction in our program.

As an example, the program below sums up the numbers a, b and c:

    {"a": 1, "b": 3, "c": 5}
    x = add a b
    l2 = x = add x c
"""

from enum import Enum
from pprint import pprint
from typing import cast
from lang import *

class Branch:
    assembly_instruction: str
    second_argument: str
    type: str

def line2env(line):
    """
    Maps a string (the line) to a dictionary in python. This function will be
    useful to read the first line of the text file. This line contains the
    initial environment of the program that will be created. If you don't like
    the function, feel free to drop it off.

    Example
        >>> line2env('{"zero": 0, "one": 1, "three": 3, "iter": 9}').get('one')
        1
    """
    import json
    env_dict = json.loads(line)
    env_lang = Env()
    for k, v in env_dict.items():
        env_lang.set(k.strip(), v)
    return env_lang

def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.

    Example:
        >>> l0 = '{"a": 0, "b": 3}'
        >>> l1 = 'bt a 1'
        >>> l2 = 'x = add a b'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        3

        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> env, prog = file2cfg_and_env([l0, l1, l2, l3])
        >>> interp(prog[0], env).get("x")
        42

        >>> l0 = '{"a": 1, "b": 3, "c": 5}'
        >>> l1 = 'x = add a b'
        >>> l2 = 'x = add x c'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        9
    """
    
    env = line2env(lines[0])

    final_instructions = []

    parsed_instructions = {}

    for index in range(1, len(lines)):
        assembly_instruction = lines[index]
        instruction_pieces = assembly_instruction.split(" ")

        current_instruction = None

        if (instruction_pieces[0] == "bt"):
            current_instruction = assembly_instruction
        elif (instruction_pieces[2] == "add"):
            current_instruction = Add(instruction_pieces[0].strip(), instruction_pieces[3].strip(), instruction_pieces[4].strip())
        elif (instruction_pieces[2] == "geq"):
            current_instruction = Geq(instruction_pieces[0].strip(), instruction_pieces[3].strip(), instruction_pieces[4].strip())
        elif (instruction_pieces[2] == "lth"):
            current_instruction = Lth(instruction_pieces[0].strip(), instruction_pieces[3].strip(), instruction_pieces[4].strip())
        elif (instruction_pieces[2] == "mul"):
            current_instruction = Mul(instruction_pieces[0].strip(), instruction_pieces[3].strip(), instruction_pieces[4].strip())

        parsed_instructions.setdefault(index - 1, current_instruction)
    
    for key, value in parsed_instructions.items():
        if isinstance(value, str):
            instruction_pieces = value.split(" ")

            branch_instruction = Bt(instruction_pieces[1], parsed_instructions.get(instruction_pieces[2]), None)

            parsed_instructions[key] = branch_instruction
        if key > 0:
            parsed_instructions[key-1].add_next(parsed_instructions[key])

    final_instructions = list(parsed_instructions.values())

    return (env, final_instructions)

