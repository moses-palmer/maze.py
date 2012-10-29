import math
import random
import re
import sys

from maze.quad import Maze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

def print_maze(maze, solution, wall_char, path_char, floor_char, room_size):
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
    try:
        import cairo
    except ImportError:
        print 'cairo is not installed, not generating image'
        return

    # Calculate the actual size of the image
    max_x, max_y = 0, 0
    min_x, min_y = sys.maxint, sys.maxint
    for wall in maze.edge_walls:
        a = wall.span[0]
        cx, cy = maze.get_center(wall.room_pos)
        px, py = cx + math.cos(a), cy - math.sin(a)
        max_x, max_y = max(max_x, px), max(max_y, py)
        min_x, min_y = min(min_x, px), min(min_y, py)

    # Create the cairo surface and context
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24,
        int((max_x - min_x) * room_width) + 2 * wall_width + 1,
        int((max_y - min_y) * room_height) + 2 * wall_width + 1)
    ctx = cairo.Context(surface)

    # Clear the background
    ctx.set_source_rgb(*background_color)
    ctx.paint()

    ctx.translate(wall_width, wall_width)

    # Note that we have not yet painted any walls for any rooms
    for room_pos in maze.room_positions:
        maze[room_pos].painted = set()

    def align(*coords):
        return tuple(round(c - o)
            for c, o in zip(coords, (min_x * room_width, min_y * room_height)))

    # Initialise the wall queue
    queue = []
    def extend_queue():
        for room_pos in maze.room_positions:
            remaining = [w
                for w in maze.walls(room_pos)
                if not int(w) in maze[w.room_pos]
                    and not int(w) in maze[w.room_pos].painted]
            if remaining:
                queue.extend(remaining)
                break
    extend_queue()

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

        # Make (0.0, 0.0) the centre of the room; this is handled in
        # angle_to_coordinate
        offset_x, offset_y = maze.get_center(wall.room_pos)

        def angle_to_coordinate(angle):
            return align(
                offset_x * room_width
                    + room_width *  math.cos(angle),
                (max_y - offset_y) * room_height
                    - room_height *  math.sin(angle))

        # If we need to move, we move to the end of the span since
        # maze.Wall.from_corner will yield walls with the start span in the
        # given corner
        if needs_move:
            ctx.move_to(*angle_to_coordinate(end_angle))
        ctx.line_to(*angle_to_coordinate(start_angle))

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

        # If the queue is empty, check if any walls remain
        if not queue:
            extend_queue()

    ctx.stroke()

    # Draw the path
    ctx.set_source_rgb(*path_color)
    ctx.set_line_width(path_width)
    for i, (x, y) in enumerate(solution):
        ctx.save()

        # Make (0.0, 0.0) the centre of the room
        offset_x, offset_y = maze.get_center((x, y))
        ctx.translate(*align(
            offset_x * room_width,
            (max_y - offset_y) * room_height))

        # Draw a line from the centre to the middle of the wall span
        if i == 0:
            ctx.move_to(0, 0)
        else:
            ctx.line_to(0, 0)

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
            return int(0.5 * math.sqrt(2.0) * result)
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

