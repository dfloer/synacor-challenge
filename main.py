from struct import unpack


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


def run(memory, stack, registers):
    param_lens = [0, 2, 1, 1, 3, 3, 1, 2, 2, 3, 3, 3, 3, 3, 2, 2, 2, 1, 0, 1, 1, 0]
    offset = 0
    while True:
        op = memory[offset]
        num_params = param_lens[op]
        op_len = 1 + num_params
        if op == 0:  # "0": Halt execution
            break
        elif op == 1:  # "1 a b": set register <a> to value of <b>
            params = memory[offset + 1 : offset + 1 + num_params]
            r = 32767 - params[0]
            v = params[1]  # Is b a memory location, or a direct value? Treating as value.
            registers[r] = v
            offset += op_len
        elif op == 2:  # "2 a": push <a> onto stack.

        elif op == 3:  # "3 a": push <a> onto stack.

        elif op == 4:  # "4 a b c": set <a> = 1 if <b> == <c>, set <a> = 0 otherwise

        elif op == 5:  # "5 a b c": set <a> = 1 if <b> > <c>, set <a> = 0 otherwise

        elif op == 6:  # "6 a": jump to memory location <a>

        elif op == 7:  # "7 a b": jump to <b> if <a> != 0

        elif op == 8:  # "8 a b": jump to <b> if <a> == 0

        elif op == 9:  # "9 a b c": <a> = <b> + <c>, % 32768

        elif op == 10:  # "10 a b c": <a> = <b> * <c>, % 32768

        elif op == 11:  # "11 a b c": <a> = remainder <b> / <c>

        elif op == 12:  # "12 a b c": <a> = <b> and <c>

        elif op == 13:  # "13 a b c": <a> = <b> or <c>

        elif op == 14:  # "14 a b": <a> = not <b> (bitwise inverse)

        elif op == 15:  # "15 a b": read memory address <b> and write to <a>

        elif op == 16:  # "16 a b": write memory address <b> and write to <a>

        elif op == 17:  # "17 a": Write address of next instruction to stack and jump to memory location <a>

        elif op == 18:  # "18": remoe element form stack and jump to it (empty stack = halt)

        elif op == 19:  # "19 a": writes the ascii code at <a> to terminal
            value = memory[offset + 1]
            print(chr(value), end='')
            offset += op_len
        elif op == 20:  # "20 a": read ascii character from terminal into <a>. Might be able to read a whole line?

        elif op == 21:  # "21": No op
            offset += op_len
        else:
            break


if __name__ == "__main__":
    file = read_file()
    split_input = split_file(file)
    memory = load_memory(split_input)
    registers = [None] * 8
    stack = []

    run(memory, stack, registers)
