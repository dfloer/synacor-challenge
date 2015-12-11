from struct import unpack
import sys
import json


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


def run(memory, stack, registers, offset, special):
    #offset = 0
    debug = False
    tamper = False
    if special:
        tamper = True

    def serve_interrupt():
        print("\n-----\nh: halt, m: dump memory, d: toggle debug, r: set value to r8, c: continue\n"
              "t: toggle teleport tamper, x: checkpoint current program state")
        choice = sys.stdin.read(2).rstrip()
        if choice == 'h':
            return True
        elif choice == 'm':
            state = save_state(memory, stack, registers, offset)
            print_state(state)
        elif choice == 'd':
            nonlocal debug
            debug = not debug
            print("debug:", debug)
        elif choice == 'r':
            print("value? (current:", registers[7], "):")
            raw = sys.stdin.readlines(1)
            value = int(''.join([x.rstrip() for x in raw]))
            print("setting reg8 to:", value)
            registers[7] = value
        elif choice == 't':
            nonlocal tamper
            tamper = not tamper
            print("tamper:", tamper)
        elif choice == 'x':
            state = save_state(memory, stack, registers, offset)
            with open('checkpoint.json', 'w') as f:
                print(json.dumps(state), file=f)
            print("current state checkpointed.")
        else:  # 'c' or any other char continues.
            pass
        print("\n-----")
        return False

    halt = False
    while True:
        while not halt:
            try:
                halt, memory, stack, registers, offset = run_inner(memory, stack, registers, offset, debug, tamper, special)
            except KeyboardInterrupt:
                halt = serve_interrupt()
                break
            if len(stack) > 300:
                print("killed")
                halt = True
        if halt:
            break


def run_inner(memory, stack, registers, offset, debug, tamper, special):
    param_lens = [0, 2, 1, 1, 3, 3, 1, 2, 2, 3, 3, 3, 3, 3, 2, 2, 2, 1, 0, 1, 1, 0]
    halt = False
    op = memory[offset]
    num_params = param_lens[op]
    op_len = 1 + num_params

    if debug:
        with open('debug.log', 'a') as logfile:
            print('|', "offset:", offset, "\nregs:", registers, "\nstack:", stack, file=logfile)
            print("op:", memory[offset: offset + op_len], "\n", file=logfile)

    if op == 0:  # "0": Halt execution
        halt = True
    elif op == 1:  # "1 a b": set register <a> to value of <b>
        params = memory[offset + 1 : offset + 1 + num_params]
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
        # Tamper with the teleporter's checks.
        if params == [32775, 5605] and tamper:
            offset += op_len
            if special:
                registers[7] = special
            print("Teleport jump not taken.")
        else:
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
    elif op == 15:  # "15 a b": read memory address <b> and write it to <a>
        params = memory[offset + 1 : offset + 1 + num_params]
        dest = params[0]
        val_b = load_value(params[1], memory, registers)
        set_value(val_b, dest, registers, memory)
        offset += op_len
    elif op == 16:  # "16 a b": read memory address <b> and write to <a>
        params = memory[offset + 1 : offset + 1 + num_params]
        loc = params[0]
        if loc > 32767:
            loc = get_value(loc, registers)
        val_b = get_value(params[1], registers)
        set_value(val_b, loc, registers, memory)
        offset += op_len
    elif op == 17:  # "17 a": Write address of next instruction to stack and jump to memory location <a>
        params = memory[offset + 1 : offset + 1 + num_params]
        next_offset = offset + op_len
        stack.append(next_offset)
        offset = get_value(params[0], registers)
    elif op == 18:  # "18": remove element from stack and jump to it (empty stack = halt)
        next_offset = stack.pop()
        offset = next_offset
    elif op == 19:  # "19 a": writes the ascii code at <a> to terminal
        value = get_value(memory[offset + 1], registers)
        print(chr(value), end='')
        offset += op_len
    elif op == 20:  # "20 a": read ascii character from terminal into <a>. Probably strung together ops to read a whole line.
        params = memory[offset + 1 : offset + 1 + num_params]
        char = ord(sys.stdin.read(1))
        loc = params[0]
        set_value(char, loc, registers, memory)
        offset += op_len
        if char == 10:
            pass
            # print("10!")
            # raise KeyboardInterrupt
    elif op == 21:  # "21": No op
        offset += op_len
    else:
        halt = True
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


def load_state():
    with open('checkpoint.json', 'r') as f:
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


if __name__ == "__main__":
    file = read_file()
    split_input = split_file(file)
    memory = load_memory(split_input)
    registers = [0] * 8
    stack = []

    offset = 0
    state = load_state()
    memory = state['memory']
    stack = state['stack']
    registers = state['registers']
    offset = state['offset']
    run(memory, stack, registers, offset, 0)
    #run(memory, stack, registers)
    # for x in range(1, 32768):
    #     print(x)
        # state = load_state()
        # memory = state['memory']
        # stack = state['stack']
        # registers = state['registers']
        # offset = state['offset']
        # run(memory, stack, registers, offset, x)
