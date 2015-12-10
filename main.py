from struct import unpack
import sys


def read_file():
    """
    Opens and reads the input file.
    Returns the binary data from the file.
    """
    with open('challenge.bin', 'rb') as f:
        return f.read()


def split_file(raw_file):
    output = []
    for idx in range(0, len(raw_file), 2):
        val = unpack('<H', raw_file[idx : idx + 2])
        output += [val[0]]
    return output


def load_memory(to_split):
    """
    Loads the split values into memory.
    Returns the full memory array.
    """
    memory = [None] * 32768
    for idx in range(len(to_split)):
        memory[idx] = to_split[idx]
    return memory


def get_value(value, registers):
    """
    Returns the value for value, or the value from a register if applicable.
    """
    if value < 32768:
        return value
    else:
        return registers[32768 - value]

def set_value(value, location, registers, memory):
    """
    Determines if location refers to a register or memory and sets it to value.
    """
    if location < 32768:
        memory[location] = value
    else:
        registers[32768 - location] = value


def run(memory, stack, registers):
    param_lens = [0, 2, 1, 1, 3, 3, 1, 2, 2, 3, 3, 3, 3, 3, 2, 2, 2, 1, 0, 1, 1, 0]
    offset = 0
    while True:
        op = memory[offset]
        num_params = param_lens[op]
        op_len = 1 + num_params

        print('\n', op, registers)
        if op == 0:  # "0": Halt execution
            break
        elif op == 1:  # "1 a b": set register <a> to value of <b>
            params = memory[offset + 1 : offset + 1 + num_params]
            reg = 32768 - params[0]
            val_b = params[1]  # Is b a memory location, or a direct value? Treating as value.
            registers[reg] = get_value(val_b, registers)
            offset += op_len
        elif op == 2:  # "2 a": push <a> onto stack.
            val_a = get_value(memory[offset + 1], registers)
            stack.append(val_a)
            offset += op_len
        elif op == 3:  # "3 a": pop from stack into <a>, empty is error, assuming <a> is a memory location
            val = stack.pop()
            loc = memory[offset + 1]
            set_value(val, loc, registers, memory)
            offset += op_len
        elif op == 4:  # "4 a b c": set <a> = 1 if <b> == <c>, set <a> = 0 otherwise
            params = memory[offset + 1 : offset + 1 + num_params]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = 0
            if val_b == val_c:
                res = 1
            loc = params[0]
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 5:  # "5 a b c": set <a> = 1 if <b> > <c>, set <a> = 0 otherwise
            params = memory[offset + 1 : offset + 1 + num_params]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = 0
            if val_b > val_c:
                res = 1
            loc = params[0]
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 6:  # "6 a": jump to memory location <a>
            new_offset = memory[offset + 1]
            offset = new_offset
        elif op == 7:  # "7 a b": jump to <b> if <a> != 0
            params = memory[offset + 1 : offset + 1 + num_params]
            val_a = get_value(params[0], registers)
            new_offset = offset + op_len
            if val_a != 0:
                new_offset = get_value(params[1], registers)
            offset = new_offset
        elif op == 8:  # "8 a b": jump to <b> if <a> == 0
            params = memory[offset + 1 : offset + 1 + num_params]
            val_a = get_value(params[0], registers)
            new_offset = offset + op_len
            if val_a == 0:
                new_offset = get_value(params[1], registers)
            offset = new_offset
        elif op == 9:  # "9 a b c": <a> = <b> + <c>, % 32768
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = (val_b + val_c) % 32768
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 10:  # "10 a b c": <a> = <b> * <c>, % 32768
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = (val_b * val_c) % 32768
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 11:  # "11 a b c": <a> = remainder <b> / <c>
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = val_b % val_c
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 12:  # "12 a b c": <a> = <b> and <c>
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = val_b & val_c
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 13:  # "13 a b c": <a> = <b> or <c>
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            val_c = get_value(params[2], registers)
            res = val_b | val_c
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 14:  # "14 a b": <a> = not <b> (bitwise inverse)
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            res = 32767 - val_b
            set_value(res, loc, registers, memory)
            offset += op_len
        elif op == 15:  # "15 a b": read memory address <b> and write to <a>
            params = memory[offset + 1 : offset + 1 + num_params]
            val_b = memory[params[1]]
            loc = params[0]
            set_value(val_b, loc, registers, memory)
            offset += op_len
        elif op == 16:  # "16 a b": write memory address <b> and write to <a>
            params = memory[offset + 1 : offset + 1 + num_params]
            loc = params[0]
            val_b = get_value(params[1], registers)
            memory[loc] = val_b
            offset += op_len
        elif op == 17:  # "17 a": Write address of next instruction to stack and jump to memory location <a>
            next_offset = offset + op_len
            stack.append(next_offset)
            new_offset = memory[offset + 1]
            offset = new_offset
        elif op == 18:  # "18": remove element from stack and jump to it (empty stack = halt)
            next_offset = stack.pop()
            offset = next_offset
        elif op == 19:  # "19 a": writes the ascii code at <a> to terminal
            value = memory[offset + 1]
            print(chr(value), end='')
            offset += op_len
        elif op == 20:  # "20 a": read ascii character from terminal into <a>. Might be able to read a whole line?
            params = memory[offset + 1 : offset + 1 + num_params]
            char = ord(sys.stdin.read(1))
            loc = params[0]
            set_value(char, loc, registers, memory)
            offset += op_len
        elif op == 21:  # "21": No op
            offset += op_len
        else:
            break


if __name__ == "__main__":
    file = read_file()
    split_input = split_file(file)
    memory = load_memory(split_input)
    registers = [0] * 8
    stack = []

    run(memory, stack, registers)
