# synacor-challenge
Repo for my solution to the [Synacor Challenge](https://challenge.synacor.com/).

## Running the VM
- `main.py [-h] -f INFILE [-x CHECKPOINT] [-d DEBUG] [-a FILE]`
  - `-f/--file`: the input binary file to run.
  - `-x/--checkpoint`: checkpoint file to write to.
  - `-d/--debug`: debug file to append to.
  - `-a/--disassemble`: file to write the disassembly to (will not execute VM).

###During VM execution
`ctrl+c` will print a control menu to the console. This allows:
- `h`: Halts current execution of the program.
- `d`: Toggles debug logging on and off. If program not run with `-d/--debug` switch, will default to "debug.txt" in current directory.
- `c`: continue execution without making any changes.
- `t`: Tamper with the teleporter.
- `x`: checkpoint current state to "checkpoint.json" in current directory.
- `m`: Dump full contents of memory, registers and stack to stdout.
- `s`: Dump just registers and stack to stdout.
- `b`: set a breakpoint. Will ask for a second line of input with the breakpoint offset.
