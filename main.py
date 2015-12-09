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


if __name__ == "__main__":
    file = read_file()
    split_input = split_file(file)
    print(split_input)

