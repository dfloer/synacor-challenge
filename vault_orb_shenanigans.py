room_grid =\
    [
        ['*', '8', '-', '1'],
        ['4', '*', '11', '*'],
        ['+', '4', '-', '18'],
        ['22', '-', '9', '*']
    ]
# Because it's easier to access like (x, y) than [x][y], or at least feels nicer.
rooms = {(a, b): room_grid[a][b] for b in range(4) for a in range(4)}


ops = {'+': (lambda a, b: (a + b) % 32768), '-': (lambda a, b: (a - b) % 32768), '*': (lambda a, b: (a * b) % 32768)}
dirs = {(1, 0): 'north', (-1, 0): 'south', (0, 1): 'west', (0, -1): 'east'}
total = 30


def find_equation(max_steps, position):
    """
    Finds the equation by calling a recursive function.
    Gets things set up, by putting the value of the starting room in, and initializing the step list.
    """
    equation = [(position, rooms[position])]
    return find_equation_inner(max_steps, position, [], equation)


def find_equation_inner(max_steps, position, steps, equation):
    """
    Recursive function to build up the equation.
    Returns the cardinal directions as a list.
    """
    if position == (0, 3):
        if check_result(equation):
            return steps
        else:
            return []
    elif max_steps == 0:
        return []
    else:
        next_rooms = adjacent_rooms(position)
        if (3, 0) in next_rooms:  # We don't want to go back to the start.
            del next_rooms[(3, 0)]
        for k, v in next_rooms.items():
            direction = tuple([a - b for a, b in zip(position, k)])
            res = find_equation_inner(max_steps - 1, k, steps + [dirs[direction]], equation + [(k, v)])
            if res:
                return res


def check_result(equation):
    """
    Runs the equation to see if algo has arrived at a solution.
    """
    if len(equation) <= 6:  # 6 is the Manhattan distance between (3, 0) and (0, 3), and minimum possible.
        return False
    result = int(equation[0][1])
    for x in range(1, len(equation) - 1, 2):
        op = equation[x][1]
        result = ops[op](result, int(equation[x + 1][1]))
    if result == 30:
        return True
    return False


def adjacent_rooms(position):
    """
    Takes the current position and returns the adjacent rooms in a plus (if applicable) around the room.
    """
    x, y = position
    result = {}
    for a, b in [(x + i, y + j) for i in [-1, 0, 1] for j in [-1, 0, 1]
                 if (i != 0 or j != 0) and not (i != 0 and j != 0)]:
        if (a, b) in rooms:
            result[(a, b)] = rooms[(a, b)]
    return result


if __name__ == "__main__":
    # I chose 12 because it was the lowest number to produce useful output.
    result = find_equation(12, (3, 0))
    print(result)
    for x in result:
        print(x)
