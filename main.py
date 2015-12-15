from struct import unpack
import sys
import json
import argparse

op_table = {0: 'halt', 1: 'set', 2: 'push', 3: 'pop', 4: 'eq', 5: 'gt',6 : 'jmp', 7: 'jt', 8: 'jf', 9: 'add', 10: 'mult', 11: 'mod', 12: 'and', 13: 'or', 14: 'not', 15: 'rmem', 16: 'wmem', 17: 'call', 18: 'ret', 19: 'out', 20: 'in', 21: 'noop'}
param_lens = [0, 2, 1, 1, 3, 3, 1, 2, 2, 3, 3, 3, 3, 3, 2, 2, 2, 1, 0, 1, 1, 0]


def read_file(infile):
    """
    Opens and reads the input file.
    Returns the binary data from the file.
    """
    with open(infile, 'rb') as f:
        return f.read()


def split_file(raw_file):
    """
    Splits the input file into uint16 pieces.
    """
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
    memory = [0] * 32768
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
        return registers[value % 32768]


def set_value(value, location, registers, memory):
    """
    Determines if location refers to a register or memory and sets it to value.
    """
    if location < 32768:
        memory[location] = value
    else:
        registers[location % 32768] = value


def load_value(location, memory, registers):
    """
    Returns the value from memory given by location. If the location points to a register, returns memory at that location.
    """
    if location < 32768:
        return memory[location]
    else:
        return memory[registers[location % 32768]]


def disassemble(infile, outfile):
    """
    Writes the disassembly generated from input file to output file.
    """
    init = split_file(read_file(infile))
    addr = 0
    with open(outfile, 'w') as f:
        while addr != len(init):
            op = init[addr]
            if op > 21:
                op_name = 'data'
                num_params = 0
            else:
                op_name = op_table[op]
                num_params = param_lens[op]
            op_len = 1 + num_params
            data = [str(init[x]) for x in range(addr, addr + op_len)]
            if op == 19:
                data[-1] = chr(int(data[-1]))
            print("offset:", addr, "-", op_name, ' '.join(data), file=f)
            addr += op_len


def run(memory, stack, registers, offset, debug_file):
    """
    Handles VM execution with execution loop.
    """
    debug = False
    tamper = False
    breakpoint = -1

    def serve_interrupt():
        """
        Little console that pops up when ctrl+c is hit.
        Allows halting the program 'h', toggling debug logging on and off 'd', continuing execution 'c',
        tampering with the teleporter (for code 7) 't', checkpointing the current program state 'x',
        dumping the whole current memory to stdout 'm' or just registers and stack 's',
        and setting a breakpoint 'b'.
        """
        if breakpoint:
            print("Breakpoint hit at:", breakpoint)
        print("\n-----\nh: halt, m: dump memory, d: toggle debug, c: continue, t: toggle teleport tamper,\n"
              "x: checkpoint current program state, s: dump reg/stack, b: set breakpoint at offset")
        choice = sys.stdin.read(2).rstrip()
        if choice == 'h':
            return True
        elif choice == 'm':
            state = save_state(memory, stack, registers, offset)
            print_state(state)
        elif choice == 's':
            state = save_state(memory, stack, registers, offset)
            print("registers:", state['registers'], ",stack:", state['stack'])
        elif choice == 'd':
            nonlocal debug
            debug = not debug
            print("debug:", debug)
        elif choice == 't':
            nonlocal tamper
            tamper = not tamper
            print("tamper:", tamper)
            registers[7] = 5
        elif choice == 'x':
            state = save_state(memory, stack, registers, offset)
            with open('checkpoint.json', 'w') as f:
                print(json.dumps(state), file=f)
            print("current state checkpointed.")
        if choice == 'b':
            print("value? (current:", breakpoint, "):")
            raw = sys.stdin.readlines(1)
            value = int(''.join([x.rstrip() for x in raw]))
            print("setting breakpoint at:", value)
        else:  # 'c' or any other char continues.
            pass
        print("\n-----")
        return False

    halt = False
    while True:
        while not halt:
            try:
                halt, memory, stack, registers, offset = run_inner(memory, stack, registers, offset, debug, tamper, breakpoint)
            # Catch the keyboard interrupt for ctrl + c
            except KeyboardInterrupt:
                halt = serve_interrupt()
                break
        if halt:
            break


def run_inner(memory, stack, registers, offset, debug, tamper, breakpoint):
    """
    Takes care of running the VM for on 'tic', and makes debug output if needed.
    """
    halt = False
    op = memory[offset]
    num_params = param_lens[op]
    op_len = 1 + num_params
    print_char = ''
    params = memory[offset + 1 : offset + 1 + num_params]
    start_offset = offset

    if breakpoint == offset:
        raise KeyboardInterrupt

    if op == 0:  # "0": Halt execution
        halt = True
    elif op == 1:  # "1 a b": set register <a> to value of <b>
        reg = params[0]
        val_b = get_value(params[1], registers)
        set_value(val_b, reg, registers, memory)
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
        val_b = get_value(params[1], registers)
        val_c = get_value(params[2], registers)
        res = 0
        if val_b == val_c:
            res = 1
        loc = params[0]
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 5:  # "5 a b c": set <a> = 1 if <b> > <c>, set <a> = 0 otherwise
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
        val_a = get_value(params[0], registers)
        new_offset = offset + op_len
        if val_a != 0:
            new_offset = get_value(params[1], registers)
        if tamper and offset == 6027:
            new_offset = 6030
            registers[1] = 5
            registers[7] = 25734
            print("Teleport check skipped.")
        offset = new_offset
    elif op == 8:  # "8 a b": jump to <b> if <a> == 0
        val_a = get_value(params[0], registers)
        new_offset = offset + op_len
        if val_a == 0:
            new_offset = get_value(params[1], registers)
        offset = new_offset
    elif op == 9:  # "9 a b c": <a> = <b> + <c>, % 32768
        loc = params[0]
        val_b = get_value(params[1], registers)
        val_c = get_value(params[2], registers)
        res = (val_b + val_c) % 32768
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 10:  # "10 a b c": <a> = <b> * <c>, % 32768
        loc = params[0]
        val_b = get_value(params[1], registers)
        val_c = get_value(params[2], registers)
        res = (val_b * val_c) % 32768
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 11:  # "11 a b c": <a> = remainder <b> / <c>
        loc = params[0]
        val_b = get_value(params[1], registers)
        val_c = get_value(params[2], registers)
        res = val_b % val_c
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 12:  # "12 a b c": <a> = <b> and <c>
        loc = params[0]
        val_b = get_value(params[1], registers)
        val_c = get_value(params[2], registers)
        res = val_b & val_c
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 13:  # "13 a b c": <a> = <b> or <c>
        loc = params[0]
        val_b = get_value(params[1], registers)
        val_c = get_value(params[2], registers)
        res = val_b | val_c
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 14:  # "14 a b": <a> = not <b> (bitwise inverse)
        loc = params[0]
        val_b = get_value(params[1], registers)
        res = 32767 - val_b
        set_value(res, loc, registers, memory)
        offset += op_len
    elif op == 15:  # "15 a b": read memory address <b> and write it to <a>
        dest = params[0]
        val_b = load_value(params[1], memory, registers)
        set_value(val_b, dest, registers, memory)
        offset += op_len
    elif op == 16:  # "16 a b": read memory address <b> and write to <a>
        loc = params[0]
        if loc > 32767:
            loc = get_value(loc, registers)
        val_b = get_value(params[1], registers)
        set_value(val_b, loc, registers, memory)
        offset += op_len
    elif op == 17:  # "17 a": Write address of next instruction to stack and jump to memory location <a>
        next_offset = offset + op_len
        stack.append(next_offset)
        offset = get_value(params[0], registers)
    elif op == 18:  # "18": remove element from stack and jump to it (empty stack = halt)
        next_offset = stack.pop()
        offset = next_offset
    elif op == 19:  # "19 a": writes the ascii code at <a> to terminal
        value = get_value(memory[offset + 1], registers)
        print(chr(value), end='')
        print_char = chr(value)
        offset += op_len
    elif op == 20:  # "20 a": read ascii character from terminal into <a>. Probably strung together ops to read a whole line.
        char = ord(sys.stdin.read(1))
        loc = params[0]
        set_value(char, loc, registers, memory)
        offset += op_len
    elif op == 21:  # "21": No op
        offset += op_len
    else:
        halt = True

    if debug:
        with open(debug_file, 'a') as logfile:
            nice_params = ' '.join([str(x) for x in params])
            print(print_char, '|', "offset:", start_offset, "\nregs:", registers, "\nstack:", stack, file=logfile)
            print("op:", op_table[op], nice_params, "\n", file=logfile)
    return halt, memory, stack, registers, offset


def save_state(memory, stack, registers, offset):
    """
    Dumps the machine state into JSON for reloading later.
    """
    output = {}
    output['memory'] = memory
    output['stack'] = stack
    output['registers'] = registers
    output['offset'] = offset
    return output


def load_state(infile='checkpoint.json'):
    with open(infile, 'r') as f:
        data = json.load(f)
    return data


def print_state(state):
    """
    Takes a state dict and prints it nicely.
    """
    print("offset:", state['offset'], "\n\nstack:", state['stack'], "\n\nregisters:", state['registers'], "\n\nmemory:")
    s = ''
    for c in state['memory']:
        if c in [11, 12, 13, 14, 15]:
            s += chr(c)
        elif c >= 0x20:
            s += chr(c)
        else:
            s += "\\" + hex(c)
    print(s)


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest="input_file", help="Input (challenge).bin", metavar="INFILE", required=True)
    parser.add_argument('-x', '--checkpoint', dest="checkpoint_file", help="Input checkpoint .json", metavar="CHECKPOINT", required=False)
    parser.add_argument('-d', '--debug', dest="debug_file", help="Debug file to append", metavar="DEBUG", required=False)
    parser.add_argument('-a', '--disassemble', dest="disassembly_file", help="Disassembly file to write", metavar="FILE", required=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    options = parse_command_line()
    input_file = options.input_file
    checkpoint = options.checkpoint_file
    debug_file = options.debug_file
    disassembly_file = options.disassembly_file

    file = read_file(input_file)
    split_input = split_file(file)
    memory = load_memory(split_input)
    registers = [0] * 8
    stack = []
    offset = 0

    if not debug_file:
        # Default debug file saved in same dir VM is run from.
        debug_file = "debug.txt"

    if checkpoint:
        state = load_state(checkpoint)
        memory = state['memory']
        stack = state['stack']
        registers = state['registers']
        offset = state['offset']

    if disassembly_file:
        disassemble(input_file, disassembly_file)
        print(input_file, "disassembled to:", disassembly_file)
    else:
        run(memory, stack, registers, offset, debug_file)
