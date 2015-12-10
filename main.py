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
        if op == 0:  # Halt execution
            break
        elif op == 19:  # "19 a": writes the ascii code at <a> to terminal
            value = memory[offset + 1]
            print(chr(value), end='')
            offset += op_len
        elif op == 21:  # No op
            pass
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


