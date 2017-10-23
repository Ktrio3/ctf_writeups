from pymouse import *
#from pywinauto.application import Application

window_width = 510  # Pre-determined. I used the Shutter tool on Ubuntu to get the width


def verify(puzzle, length, width):
    i = 0
    j = 0

    while i < length:
        while j < width:
            if puzzle[i][j] is 1:
                return False
            j += 1
        i += 1
        j = 0
    return True


def print_puzzle(puzzle, length, width):
    i = 0
    j = 0

    if length > 10 or width > 10:
	return

    while i < length:
        while j < width:
            print puzzle[i][j], " ",
            j += 1
        i += 1
        j = 0
        print


def solve(puzzle, length, width, base_x, base_y, base_distance):
    i = 0
    j = 0

    while i < length:
        while j < width:
            # If this light is on, click the light 2 below (or 2 above if in the last 2 rows)
            if puzzle[i][j] is 1:
                # Check if this is the final 2
                if i is length - 2 or i is length - 1:
                    click(puzzle, length, width, i - 2, j, base_x, base_y, base_distance)
                    print "Clicked (" + str(i - 2) + ", " + str(j) + ")"
                else:
                    click(puzzle, length, width, i + 2, j, base_x, base_y, base_distance)
                    print "Clicked (" + str(i + 2) + ", " + str(j) + ")"
                #print_puzzle(puzzle, length, width)
                #raw_input()
            j += 1
        i += 1
        j = 0


def click(puzzle, length, width, x, y, base_x, base_y, base_distance):
    global m
    # The list of differences we need to check
    #     X
    #   X   X
    # X   c   X The pattern updated
    #   X   X
    #     X
    # I.e. the square two above is (-2, 0) and 2 to the right is (0, 2)
    # Follow clockwise around pattern
    values = [(-2, 0), (-1, 1), (0, 2), (1, 1), (2, 0), (1, -1), (0, -2), (-1, -1)]

    # Do the actual click in the gui
    m.click(base_x + x * base_distance, base_y + y * base_distance, 1)

    for value in values:
        x_change = x + value[0]
        y_change = y + value[1]

        if x_change < 0 or x_change >= length:
            continue
        if y_change < 0 or y_change >= length:
            continue

        if puzzle[x_change][y_change] is 0:
            puzzle[x_change][y_change] = 1
        else:
            puzzle[x_change][y_change] = 0


class ListenInterrupt(Exception):
    pass


class puzzle_clicker(PyMouseEvent):
    def __init__(self):
        PyMouseEvent.__init__(self)
        self.lastX = 0
        self.lastY = 0

    def click(self, x, y, button, press):
        if button == 1:
            if press:
                self.lastX = x
                self.lastY = y
        raise ListenInterrupt("Calibrated.")


print "Please click the top left box in the gui."

PC = puzzle_clicker()
try:
    PC.run()
except ListenInterrupt as e:
    base_x = PC.lastX
    base_y = PC.lastY

print "Top left box is at (" + str(base_x) + ", " + str(base_y) + ")"

# Unclick the boxes the user just clicked to return the puzzle to normal

m = PyMouse()
m.click(base_x, base_y, 1)
#del m

#app = pywinauto.Application().connect_(path='Light.exe')
#app.MainDialog.ClickInput(coords=(953, 656))
#app.MainDialog.PrintControlIdentifiers()

puzzle = open("meow", "r")

puzzle_state = puzzle.read()

puzzle.close()

offset = 0

length = puzzle_state[offset]

length = int(length.encode('hex'), 0)
offset += 4

width = (puzzle_state[offset])
width = int(width.encode('hex'), 0)

offset += 4

print "The size of the puzzle is " + str(length) + "X" + str(width)

base_distance = window_width / length

print "Based on this size, the distance between squares is:" + str(base_distance)
print "If the puzzle is not solved, check that your window is " + str(window_width) + " pixels wide"
print "If it is not, change the window_width variable"
print "Press enter when ready to continue"
raw_input()

# We now know our size; create list to hold it
puzzle = [[0] * length for i in range(width)]

i = 0
j = 0

while i < length:
    while j < width:
        puzzle[i][j] = int(puzzle_state[offset].encode('hex'), 0)
        offset += 1
        j += 1
    i += 1
    j = 0

print_puzzle(puzzle, length, width)

while not verify(puzzle, length, width):
    solve(puzzle, length, width, base_x, base_y, base_distance)
    print_puzzle(puzzle, length, width)
    print

print "Puzzle solved:"
print_puzzle(puzzle, length, width)
