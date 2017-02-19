import subprocess as sp
import time


#############################
# CONSTANTS
#############################
ASSIGNMENTS = []
ROWS = 'ABCDEFGHI'
COLS = '123456789'

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

BOXES = cross(ROWS, COLS)

ROW_UNITS = [cross(r, COLS) for r in ROWS]
COL_UNITS = [cross(ROWS, c) for c in COLS]
SQR_UNITS = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
DIA_UNITS = [[ROWS[i] + COLS[i] for i in range(9)],
             [ROWS[i] + COLS[(i+1)*-1] for i in range(9)]]
UNIT_LIST = ROW_UNITS + COL_UNITS + SQR_UNITS + DIA_UNITS
UNITS = dict((s, [u for u in UNIT_LIST if s in u]) for s in BOXES)
PEERS = dict((s, set(sum(UNITS[s],[]))-set([s])) for s in BOXES)


# def assign_value(values, box, value):
#     """
#     Please use this function to update your values dictionary!
#     Assigns a value to a given box. If it updates the board record it.
#     """
#     values[box] = value
#     if len(value) == 1:
#         ASSIGNMENTS.append(values.copy())
#     return values


#############################
# STRATEGIES
#############################
def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit_boxes in UNIT_LIST:
        unit_dict = {box: values[box] for box in unit_boxes}
        unit_values = list(unit_dict.values()) 
        twins = [(b, values[b]) for b in unit_boxes if ((len(values[b]) == 2) & (unit_values.count(values[b]) == 2))]
        if twins:
            twin_values = list({v for _, v in twins})
            twin_boxes  = list({b for b, _ in twins})
            for box in unit_boxes:
                if box not in twin_boxes:
                    old = values[box]
                    for twin_value in twin_values:
                        new = ''.join([c for c in old if c not in twin_value])
                        values[box] = new
    return values

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in PEERS[box]:
            values[peer] = values[peer].replace(digit,'')
            pass
    return values

def only_choice(values):
    for unit in UNIT_LIST:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        eliminate(values)
        display(values)
        only_choice(values)
        display(values)
        naked_twins(values)
        display(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


#############################
# UTILS
#############################
def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The BOXES, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    for c in grid:
        if c in COLS:
            chars.append(c)
        if c == '.':
            chars.append(COLS)
    assert len(chars) == 81
    return dict(zip(BOXES, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    time.sleep(0.3)
    _ = sp.call('clear',shell=True)
    width = 1+max(len(values[s]) for s in BOXES)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in COLS))
        if r in 'CF': print(line)
    print

def search(values, show=True):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    if show:
        display(values)
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in BOXES): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in BOXES if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


#############################
# START HERE
#############################
def solve(grid, show=True):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values, show=show)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid, show=False))

    # try:
    #     from visualize import visualize_assignments
    #     visualize_assignments(ASSIGNMENTS)
    # except SystemExit:
    #     pass
    # except:
    #     print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
