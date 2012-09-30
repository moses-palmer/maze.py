import random

from maze import Maze
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
                        (path_char if \
                            int(maze.Wall.from_direction((x, y), (0, dy))) \
                                in maze[x, y] \
                            and (x, y) in solution \
                            and (x, y + dy) in solution
                        else floor_char \
                            if int(maze.Wall.from_direction((x, y), (0, dy))) \
                                in maze[x, y]
                        else wall_char) * (room_size[0] - 2),

                        # The right wall
                        wall_char)))
                else:
                    # This is a line in the middle of a room
                    output(''.join((
                        # The left opening or wall
                        path_char if int(maze.Wall.from_direction(
                                (x, y), (-1, 0))) in maze[x, y] \
                            and (x, y) in solution \
                            and (x - 1, y) in solution
                        else floor_char if \
                            int(maze.Wall.from_direction((x, y), (-1, 0))) \
                                in maze[x, y]
                        else wall_char,

                        # The center
                        (path_char if (x, y) in solution \
                        else floor_char) * (room_size[0] - 2),

                        # The right opening or wall
                        path_char if int(maze.Wall.from_direction(
                                (x, y), (1, 0))) in maze[x, y] \
                            and (x, y) in solution \
                            and (x + 1, y) in solution
                        else floor_char if \
                            int(maze.Wall.from_direction((x, y), (1, 0))) \
                                in maze[x, y]
                        else wall_char)))
            output('\n')


def make_image(maze, solution):
    import math

    try:
        import cairo
    except ImportError:
        print 'cairo is not installed, not generating image'
        return

    background_color = (0.0, 0.0, 0.0)
    wall_color = (1.0, 1.0, 1.0)
    wall_width = 2
    path_color = (0.8, 0.4, 0.2)
    path_width = 2
    room_width, room_height = (10, 10)
    image_file = 'maze.png'

    # Create the cairo surface and context
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24,
        maze.width * room_width + 2 * wall_width,
        maze.height * room_height + 2 * wall_width)
    ctx = cairo.Context(surface)

    # Calculate the multiplication factor for the room size
    idx, idy = 0.0, 0.0
    for wall in maze.Wall.from_room_pos((0, 0)):
        span = wall.span
        idx = max(idx, abs(math.cos(span[0])))
        idy = max(idy, abs(math.sin(span[0])))
    dx, dy = 0.5 / idx, 0.5 / idy

    # Clear the background
    ctx.set_source_rgb(*background_color)
    ctx.paint()

    # Iterate over all rooms
    for x, y in maze:
        ctx.save()

        # Make (0.0, 0.0) the centre of the room
        offset_x, offset_y = maze.get_center((x, y))
        ctx.translate(
            offset_x * room_width + wall_width,
            (maze.height - offset_y) * room_height + wall_width)

        # Draw the walls
        ctx.set_source_rgb(*wall_color)
        ctx.set_line_width(wall_width)
        is_first_wall = True
        for wall in maze.walls((x, y)):
            start_angle, end_angle = wall.span

            def angle_to_coordinate(angle):
                return (
                    dx * room_width *  math.cos(angle),
                    -dy * room_height *  math.sin(angle))

            # Always move to the beginning of the first span
            if is_first_wall:
                ctx.move_to(*angle_to_coordinate(start_angle))

            if int(wall) in maze[x, y]:
                ctx.move_to(*angle_to_coordinate(end_angle))
            else:
                ctx.line_to(*angle_to_coordinate(end_angle))
        ctx.stroke()

        # Draw the path
        if (x, y) in solution:
            ctx.set_source_rgb(*path_color)
            ctx.set_line_width(path_width)

            for wall in maze.walls((x, y)):
                def angle_to_coordinate(angle):
                    return (
                        0.5 * room_width *  math.cos(angle),
                        -0.5 * room_height *  math.sin(angle))

                # Do nothing if the room on the other side is not on the path
                try:
                    if not maze.walk(wall, True) in solution:
                        continue
                except IndexError:
                    continue
                except ValueError:
                    continue

                # Calculate the angle in the middle of the wall span
                angle = math.atan2(
                    sum(math.sin(a) for a in wall.span),
                    sum(math.cos(a) for a in wall.span))

                # Draw a line from the centre to the middle of the wall span
                ctx.move_to(0, 0)
                ctx.line_to(*angle_to_coordinate(angle))
            ctx.stroke()

        ctx.restore()

    surface.write_to_png(image_file)


if __name__ == '__main__':
    maze_size = (15, 10)

    # Create and initialise the maze
    maze = Maze(*maze_size)
    initialize(maze, lambda max: random.randint(0, max - 1))
    solution = list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))

    print_maze(maze, solution)
    make_image(maze, solution)
