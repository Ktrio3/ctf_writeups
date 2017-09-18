from socket import create_connection

MAZE_SERVER = ('54.69.145.229', 16000)
RECV_SIZE = 8192


class maze:
    def __init__(self, maze):
        self.maze = []
        self.current = (0,0)
        i = 0
        for line in maze:
            j = 0
            self.maze.append([])
            for char in line:
                self.maze[i].append(item(char))
                j = j + 1
            i = i + 1

    def finished(self, current):
        item = self.maze[current[0]][current[1]]
        if item.char == "X":
            return True
        return False

    def solve(s):
        stack = []
        charStack = []

        stack.append(s.current)
        current = s.current

        while len(stack) > 0:
            if s.finished(current):
                return charStack

            nextItem, newChar = s.move(current)

            if nextItem is None:
                charStack.pop()
                current = stack.pop()
                print charStack
                continue

            charStack.append(newChar)
            stack.append(nextItem)
            current = nextItem

        return None

    def dfs_paths(s):
        stack = [(s.current, [])]
        while stack:
            (vertex, path) = stack.pop()
            print vertex
            for nextItem in s.move(vertex):
                if s.finished(nextItem[0]):
                    newPath = []
                    for item in path:
                        newPath.append(item)
                    newPath.append(nextItem[1])
                    yield newPath
                else:
                    newPath = []
                    for item in path:
                        newPath.append(item)
                    newPath.append(nextItem[1])
                    stack.append((nextItem[0], newPath))

    def move(s, current):
        # North, East, South, West
        lists = []
        nextVal = s.maze[current[0]-1][current[1]]
        if nextVal.char != "#" and not nextVal.visited:
            nextVal.visited = True
            lists.append([(current[0]-1, current[1]), "^"])

        nextVal = s.maze[current[0]][current[1]+1]
        if nextVal.char != "#" and not nextVal.visited:
            nextVal.visited = True
            lists.append([(current[0], current[1] + 1), ">"])

        nextVal = s.maze[current[0]+1][current[1]]
        if nextVal.char != "#" and not nextVal.visited:
            nextVal.visited = True
            lists.append([(current[0]+1, current[1]), "V"])

        nextVal = s.maze[current[0]][current[1]-1]
        if nextVal.char != "#" and not nextVal.visited:
            nextVal.visited = True
            lists.append([(current[0], current[1]-1), "<"])

        return lists


    def findStart(self):
        i = 0
        for line in self.maze:
            j = 0
            for char in line:
                if char.char == ">":
                    self.current = (i, j)
                j = j + 1
            i = i + 1


class item:

    def __init__(self, char):
        self.visited = False
        self.char = char

def main():
    conn = create_connection(MAZE_SERVER)
    response = conn.recv(RECV_SIZE)
    while True:
        print response
        if "Now " not in response:
            return

        response_lines = response.splitlines()
        find_delim = [x for x in response_lines if x.startswith('Now')][0]
        maze_lines = response_lines[response_lines.index(find_delim)+2:-1]
        maze_text = '\n'.join(maze_lines)

        # Do your thing here with either maze_text or maze_lines.
        myMaze = maze(maze_lines)
        myMaze.findStart()

        solutions = []
        for sol in myMaze.dfs_paths():
            solutions.append(''.join(map(str, sol)))

        solution = min(solutions, key=len)

        print solution
        if not len(solution):
            return
        conn.send(solution)

        response = conn.recv(RECV_SIZE)


if __name__ == '__main__':
    main()
