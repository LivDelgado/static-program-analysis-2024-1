import sys
import todo

from lang import interp

if __name__ == "__main__":
    lines = [
        '{"num": 9, "zero": 0, "two": 2, "true": true, "false": false}',
        'var = add zero zero',
        'var = add var two',
        'g = geq var num',
        'l = lth num var',
        'bt g 6',
        'bt true 1',
        'bt l 10',
        'bt true 8',
        'iseven = geq two zero',
        'bt true 11',
        'iseven = geq zero two',
        'end = add zero zero'
    ]
    env, program = todo.file2cfg_and_env(lines)
    final_env = interp(program[0], env)
    final_env.dump()
