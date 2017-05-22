from collections import Counter


assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    two_elements_boxes = [box for box in values.keys() if len(values[box]) == 2]

    for box in two_elements_boxes:
        row_peers, col_peers, diagonal_peers = unit_peers(box)
        values = naked_twins_by_unit(values, row_peers)
        values = naked_twins_by_unit(values, col_peers)
        values = naked_twins_by_unit(values, diagonal_peers)

    return values


def unit_peers(box):
    """Obtain peers grouped by unit"""
    row_peers = [row_unit for row_unit in row_units if box in row_unit][0]
    col_peers = [col_unit for col_unit in column_units if box in col_unit][0]
    if box in l_diagonal_units[0] and box in r_diagonal_units[0]:
        diagonal_peers = l_diagonal_units[0] + r_diagonal_units[0]
    elif box in l_diagonal_units[0]:
        diagonal_peers = l_diagonal_units[0]
    elif box in r_diagonal_units[0]:
        diagonal_peers = r_diagonal_units[0]
    else:
        diagonal_peers = []

    return row_peers, col_peers, diagonal_peers


def naked_twins_by_unit(values, peers):
    peers_values = [values[peer] for peer in peers]
    peers_values_count = dict((x, peers_values.count(x)) for x in peers_values)
    for k, v in peers_values_count.items():
        if len(k) == 2 and v > 1:
            for c in k:
                for peer in peers:
                    if len(values[peer]) > 2:
                        values[peer] = values[peer].replace(c, "")

    return values


def cross(a, b):
    """Cross product of elements in A and elements in B."""
    return [s + t for s in a for t in b]


def diagonal(a, b):
    """create diagonal elements"""
    return [s + t for s, t in zip(a, b)]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
l_diagonal_units = [diagonal(rows, cols)]
r_diagonal_units = [diagonal(rows, cols[::-1])]
diagonal_units = l_diagonal_units + r_diagonal_units
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

unit_list = row_units + column_units + square_units + l_diagonal_units + r_diagonal_units
units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    values = []
    all_number = '123456789'
    for x in grid:
        if x == '.':
            values.append(all_number)
        elif x in all_number:
            values.append(x)
    return dict(zip(boxes, values))


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    sin_boxes = [box for box in values.keys() if len(values[box]) == 1 ]
    for box in sin_boxes:
            for peer in peers[box]:
                values[peer] = values[peer].replace(values[box], "")
    return values


def only_choice(values):
    for unit in unit_list:
        for digit in '123456789':
            only_one = [box for box in unit if digit in values[box]]
            if len(only_one) == 1:
                values = assign_value(values, only_one[0], digit)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  # Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #print("Before solved")
    display(dict(zip(boxes, diag_sudoku_grid)))
    #print("After solved")
    display(solve(diag_sudoku_grid))


    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
