import random

from maze import Maze, Wall
from maze.randomized_prim import initialize

def print_maze(maze, solution):
    import sys

    def output(s):
        sys.stdout.write(s)

    wall_char = '@'
    path_char = '.'
    floor_char = ' '
    room_size = (5, 5)

    # Iterate over all rows and make sure to start with the last to maintain the
    # orientation of the maze
    for y in reversed(xrange(maze.height)):
        # Print one line for each height unit of a room
        for line in xrange(room_size[1]):
            # Calculate the vertical offset of the neighbouring room
            dy = 1 if not line else -1 if line == room_size[1] - 1 else 0
            for x in xrange(maze.width):
                # Print one line of the current room for every room in the
                # current row
                if line == 0 or line == room_size[1] - 1:
                    # This is the first or the last line
                    output(''.join((
                        # The left wall
                        wall_char,

                        # The opening or top/bottom wall
                        (path_char if Wall.get_wall((0, dy)) in maze[x, y] \
                            and (x, y) in solution \
                            and (x, y + dy) in solution
                        else floor_char \
                                if Wall.get_wall((0, dy)) in maze[x, y]
                        else wall_char) * (room_size[0] - 2),

                        # The right wall
                        wall_char)))
                else:
                    # This is a line in the middle of a room
                    output(''.join((
                        # The left opening or wall
                        path_char if Wall.get_wall((-1, 0)) in maze[x, y] \
                            and (x, y) in solution \
                            and (x - 1, y) in solution
                        else floor_char if Wall.get_wall((-1, 0)) in maze[x, y]
                        else wall_char,

                        # The center
                        (path_char if (x, y) in solution \
                        else floor_char) * (room_size[0] - 2),

                        # The right opening or wall
                        path_char if Wall.get_wall((1, 0)) in maze[x, y] \
                            and (x, y) in solution \
                            and (x + 1, y) in solution
                        else floor_char if Wall.get_wall((1, 0)) in maze[x, y]
                        else wall_char)))
            output('\n')


if __name__ == '__main__':
    maze_size = (15, 10)

    # Create and initialise the maze
    maze = Maze(*maze_size)
    initialize(maze, lambda max: random.randint(0, max - 1))
    solution = list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))

    print_maze(maze, solution)
