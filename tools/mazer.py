import random
import re

from maze import Maze, HexMaze
from maze.randomized_prim import initialize

def print_maze(maze, solution, wall_char, path_char, floor_char, room_size):
    import sys

    if len(maze.Wall.WALLS) != 4:
        print 'This maze cannot be printed as it is not square'
        return

    def output(s):
        sys.stdout.write(s)

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


def make_image(maze, solution, (room_width, room_height), image_file,
        background_color, wall_color, path_color, wall_width, path_width):
    import math

    try:
        import cairo
    except ImportError:
        print 'cairo is not installed, not generating image'
        return

    # Calculate the actual size of the image
    max_x, max_y = 0, 0
    for y in xrange(maze.height):
        row = (maze.width - 1,) if y < maze.height - 1 else xrange(maze.width)
        for x in row:
            cx, cy = maze.get_center((x, y))
            max_x = max(max_x, cx + 0.5)
            max_y = max(max_y, cy + 0.5)

    # Create the cairo surface and context
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24,
        int(max_x * room_width) + 2 * wall_width,
        int(max_y * room_height) + 2 * wall_width)
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

    # Note that we have not yet painted any walls for any rooms
    for room_pos in maze.room_positions:
        maze[room_pos].painted = set()

    # Initialise the wall queue
    queue = [maze.Wall((0, 0), 0)]

    # Draw the walls
    ctx.set_source_rgb(*wall_color)
    ctx.set_line_width(wall_width)
    needs_move = True
    while queue:
        # Get the last wall from the queue and retrieve all remaining walls in
        # its corner; we add the back of the walls in order to actually move
        # along the wall instead of just spinning around the corner
        wall = queue.pop()
        walls = [w.back if w.back in maze else w
            for w in wall.corner_walls
            if w in maze or w.back in maze]
        remaining = [w for w in walls
            if not int(w) in maze[w.room_pos]
                and not int(w) in maze[w.room_pos].painted
                and not w == wall]

        # Queue all remaining walls for later use
        queue.extend(remaining)

        start_angle, end_angle = wall.span

        def angle_to_coordinate(angle):
            return (
                dx * room_width *  math.cos(angle),
                -dy * room_height *  math.sin(angle))

        ctx.save()

        # Make (0.0, 0.0) the centre of the room
        offset_x, offset_y = maze.get_center(wall.room_pos)
        ctx.translate(
            offset_x * room_width + wall_width,
            (max_y - offset_y) * room_height + wall_width)

        # If we need to move, we move to the end of the span since
        # maze.Wall.from_corner will yield walls with the start span in the
        # given corner
        if needs_move:
            ctx.move_to(*angle_to_coordinate(end_angle))
        ctx.line_to(*angle_to_coordinate(start_angle))

        ctx.restore()

        # Mark the current wall as painted, and the wall on the other side as
        # well as long as this is not a wall along the edge of the maze
        maze[wall.room_pos].painted.add(int(wall))
        if not maze.edge(wall):
            maze[wall.back.room_pos].painted.add(int(wall.opposite))

        # If we have reached a dead end, we need to stroke the line and start
        # over with a wall from the queue
        if not remaining:
            ctx.stroke()
            needs_move = True
        else:
            needs_move = False

    ctx.stroke()

    # Draw the path
    ctx.set_source_rgb(*path_color)
    ctx.set_line_width(path_width)
    for x, y in maze:
        if (x, y) in solution:
            for wall in maze.walls((x, y)):
                def angle_to_coordinate(angle):
                    return (
                        0.5 / dy * room_width *  math.cos(angle),
                        -0.5 / dx * room_height *  math.sin(angle))

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

                ctx.save()

                # Make (0.0, 0.0) the centre of the room
                offset_x, offset_y = maze.get_center(wall.room_pos)
                ctx.translate(
                    offset_x * room_width + wall_width,
                    (max_y - offset_y) * room_height + wall_width)

                # Draw a line from the centre to the middle of the wall span
                ctx.move_to(0, 0)
                ctx.line_to(*angle_to_coordinate(angle))

                ctx.restore()

            ctx.stroke()

    surface.write_to_png(image_file)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description = 'A tool to generate mazes')

    def maze_size(s):
        result = int(s)
        if result < 1:
            raise argparse.ArgumentTypeError(
                'The maze size must be greater than 0')
        else:
            return result
    parser.add_argument('--maze-size', type = maze_size, nargs = 2,
        metavar = ('WIDTH', 'HEIGHT'),
        default = (15, 10),
        help = 'The size of the maze.')

    maze_classes = dict((len(mc.Wall.WALLS), mc) for mc in (
        Maze, HexMaze))
    parser.add_argument('--walls', type = int,
        choices = maze_classes.keys(),
        default = 4,
        help = 'The number of walls for every room.')

    def char(s):
        if len(s) != 1:
            raise argparse.ArgumentTypeError('%s is not a valid character' % s)
        else:
            return s
    parser.add_argument('--print-wall-char', type = char,
        default = '@',
        help = 'The character used for walls when printing the maze.')
    parser.add_argument('--print-path-char', type = char,
        default = '.',
        help = 'The character used for the path when printing the maze.')
    parser.add_argument('--print-floor-char', type = char,
        default = ' ',
        help = 'The character used for the floor when printing the maze.')

    def print_room_size(s):
        result = int(s)
        if result < 3:
            raise argparse.ArgumentTypeError(
                'The room size must be greater than 3')
        else:
            return result
    parser.add_argument('--print-room-size', type = print_room_size,
        nargs = 2,
        default = (5, 4),
        help = 'The size of each room in characters when printing the maze.')

    def image_room_size(s):
        result = int(s)
        if result < 1:
            raise argparse.ArgumentTypeError(
                'The maze room size in the image must be greater than 0')
        else:
            return result
    parser.add_argument('--image-room-size', type = image_room_size, nargs = 2,
        metavar = ('WIDTH', 'HEIGHT'),
        default = (30, 30),
        help = 'The size of the rooms in the maze image.')

    class default:
        def write(*args, **kwargs):
            pass
    parser.add_argument('--image-file', type = argparse.FileType('w'),
        metavar = 'FILENAME',
        default = default(),
        help = 'The name of the PNG file to create.')

    def color(s):
        result = None
        m = re.match(r'''(?x)
            \#(?P<red>[0-9A-Fa-f]{2})
             (?P<green>[0-9A-Fa-f]{2})
             (?P<blue>[0-9A-Fa-f]{2})''', s)
        if not m is None:
            result = tuple(float(int(d, 16)) / 255 for d in m.groups())
        else:
            m = re.match(r'''(?x)
                rgb\(
                    \s*(?P<red>\d{1,3}%?)\s*,
                    \s*(?P<green>\d{1,3}%?)\s*,
                    \s*(?P<blue>\d{1,3}%?)\s*\)''', s)
            if not m is None:
                result = tuple(float(d) / 255 if d[-1].isdigit()
                    else float(d[:-1]) / 100 for d in m.groups())
        if result is None or any(r < 0 or r > 1.0 for r in result):
            raise argparse.ArgumentTypeError(
                '"%s" is not a valid colour.' % s)
        return result
    parser.add_argument('--image-background-color', type = color,
        metavar = 'COLOUR',
        default = (0.0, 0.0, 0.0),
        help = 'The background colour of the image. This must be specified as '
            'a HTML colour on the form #RRGGBB or rgb(r, g, b).')
    parser.add_argument('--image-wall-color', type = color,
        metavar = 'COLOUR',
        default = (1.0, 1.0, 1.0),
        help = 'The colour of the wall in the image. This must be specified as '
            'a HTML colour on the form #RRGGBB or rgb(r, g, b).')
    parser.add_argument('--image-path-color', type = color,
        metavar = 'COLOUR',
        default = (0.8, 0.4, 0.2),
        help = 'The colour of the path in the image. This must be specified as '
            'a HTML colour on the form #RRGGBB or rgb(r, g, b).')

    def line_width(s):
        result = int(s)
        if result < 2:
            raise argparse.ArgumentTypeError(
                'The maze size must be greater than 1')
        elif result & 1:
            raise argparse.ArgumentTypeError(
                'The maze size must be an even number')
        else:
            return result
    parser.add_argument('--image-wall-width', type = line_width,
        metavar = 'WIDTH',
        default = 2,
        help = 'The width of the maze wall lines.')
    parser.add_argument('--image-path-width', type = line_width,
        metavar = 'WIDTH',
        default = 2,
        help = 'The width of the maze path lines.')

    namespace = parser.parse_args()

    # Create and initialise the maze
    maze = maze_classes[namespace.walls](*namespace.maze_size)
    initialize(maze, lambda max: random.randint(0, max - 1))
    solution = list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))

    print_maze(maze, solution,
        namespace.print_wall_char,
        namespace.print_path_char,
        namespace.print_floor_char,
        namespace.print_room_size)
    make_image(maze, solution,
        namespace.image_room_size,
        namespace.image_file,
        namespace.image_background_color,
        namespace.image_wall_color,
        namespace.image_path_color,
        namespace.image_wall_width,
        namespace.image_path_width)

