import math
import os
import random
import re
import sys

try:
    import cairo
except ImportError:
    print 'This program requires cairo'
    sys.exit(1)

from maze.quad import Maze
from maze.tri import TriMaze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

def print_maze(maze, solution, wall_char, path_char, floor_char, room_size):
    if len(maze.Wall.WALLS) != 4:
        print 'This maze cannot be printed as it is not square'
        return

    def output(s):
        sys.stdout.write(s)

    # Iterate over all rows and make sure to start with the last one to maintain
    # the orientation of the maze
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


def calculate_bounds(maze):
    """
    Calculates the bounds of the walls of a maze.

    @param maze
        The maze whose bounds to calculate.
    @return the tuple (min_x, min_y, max_x, max_y)
    """
    max_x, max_y = 0, 0
    min_x, min_y = sys.maxint, sys.maxint
    for wall in maze.edge_walls:
        a = wall.span[0]
        cx, cy = maze.get_center(wall.room_pos)
        px, py = cx + math.cos(a), cy + math.sin(a)
        max_x, max_y = max(max_x, px), max(max_y, py)
        min_x, min_y = min(min_x, px), min(min_y, py)
    return (min_x, min_y, max_x, max_y)

def draw_walls(maze, ctx, coords):
    """
    Draws the walls of a maze.

    @param maze
        The maze whose walls to draw.
    @param ctx
        The cairo context to use for drawing.
    @param coords
        A callable that transforms its parameters (maze_x, maze_y) to
        coordinates in the cairo context.
    """
    # Note that we have not yet painted any walls for any rooms
    for room_pos in maze.room_positions:
        maze[room_pos].painted = set()

    # Initialise the wall queue
    queue = []
    def extend_queue():
        """
        Finds a room with walls that have not yet been painted and adds them to
        queue.
        """
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
        offset_x, offset_y = maze.get_center(wall.room_pos)

        def angle_to_coordinate(angle):
            """
            Converts an angle from a wall span in the current room to a
            coordinate.

            @param angle
                The angle to convert.
            @return the tuple (x, y)
            """
            return coords(
                offset_x + math.cos(angle),
                offset_y + math.sin(angle))

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
            maze[wall.back.room_pos].painted.add(int(wall.back))

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

    # Remove the temporary attribute
    for room_pos in maze.room_positions:
        del maze[room_pos].painted

def draw_path_smooth(maze, ctx, coords, solution):
    """
    Draws the solution path using a smooth bezier curve.

    @param maze
        The maze whose solution to draw.
    @param ctx
        The cairo context to use for drawing.
    @param coords
        A callable that transforms its parameters (maze_x, maze_y) to
        coordinates in the cairo context.
    @param solution
        The solution. This must be a list of all rooms to traverse.
    """
    room_positions = ((solution[i - 1], solution[i], solution[i + 1])
        for i in xrange(1, len(solution) - 1))
    ctx.move_to(*coords(*maze.get_center(solution[0])))
    for (previous_pos, current_pos, next_pos) in room_positions:
        # Draw a bezier curve from the wall to the previous room to the wall
        # to the next room
        previous_center = coords(*maze.get_center(previous_pos))
        current_center = coords(*maze.get_center(current_pos))
        next_center = coords(*maze.get_center(next_pos))
        d = 0.3
        ctx.curve_to(
            d * previous_center[0] + (1.0 - d) * current_center[0],
            d * previous_center[1] + (1.0 - d) * current_center[1],
            d * next_center[0] + (1.0 - d) * current_center[0],
            d * next_center[1] + (1.0 - d) * current_center[1],
            0.5 * (current_center[0] + next_center[0]),
            0.5 * (current_center[1] + next_center[1]))
    ctx.line_to(*coords(*maze.get_center(solution[-1])))
    ctx.stroke()

def draw_path(maze, ctx, coords, solution):
    """
    Draws the solution path using straight lines.

    @param maze
        The maze whose solution to draw.
    @param ctx
        The cairo context to use for drawing.
    @param coords
        A callable that transforms its parameters (maze_x, maze_y) to
        coordinates in the cairo context.
    @param solution
        The solution. This must be a list of all rooms to traverse.
    """
    for i, room_pos in enumerate(solution):
        # Draw a line to the centre of the room
        center = coords(*maze.get_center(room_pos))
        if i == 0:
            ctx.move_to(*center)
        else:
            ctx.line_to(*center)
    ctx.stroke()

def make_image(maze, solution, room_size, output, background_color, wall_color,
        path_color, wall_width, path_width, path_smooth):
    room_width, room_height = room_size
    image_create, image_write = output

    # Calculate the actual size of the image
    min_x, min_y, max_x, max_y = calculate_bounds(maze)

    # Create the cairo surface and context
    width = int((max_x - min_x) * room_width) + 2 * wall_width + 1
    height = int((max_y - min_y) * room_height) + 2 * wall_width + 1
    surface = image_create(width, height)
    ctx = cairo.Context(surface)

    # Make line caps and line joins round
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # Clear the background
    ctx.set_source_rgba(*background_color)
    ctx.paint()

    def coords(x, y):
        """
        Converts coordinates from maze coordinates to context coordinates.

        The coordinates are scaled according to the room dimesions and offset
        with the minimum coordinates in the respective dimension and then
        rounded to make the lines sharp when drawing.

        @param x, y
            The maze coordinates to convert.
        @return coordinates to use for drawing
        """
        return (
            wall_width + (
                round((x - min_x) * room_width)),
            height - wall_width - (
                round((y - min_y) * room_height)))

    # Draw the walls
    ctx.set_source_rgba(*wall_color)
    ctx.set_line_width(wall_width)
    draw_walls(maze, ctx, coords)

    # Draw the path
    ctx.set_source_rgba(*path_color)
    ctx.set_line_width(path_width)
    if path_smooth:
        draw_path_smooth(maze, ctx, coords, solution)
    else:
        draw_path(maze, ctx, coords, solution)

    image_write(surface)


def main():
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
        Maze, TriMaze, HexMaze))
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
                'The room size must be greater than or equal to 3')
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

    surface_types = {
        'pdf': (
            lambda f, w, h: cairo.PDFSurface(f, w, h),
            lambda f, surface: None),
        'png': (
            lambda f, w, h: cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h),
            lambda f, surface: surface.write_to_png(f)),
        'ps': (
            lambda f, w, h: cairo.PSSurface(f, w, h),
            lambda f, surface: None),
        'svg': (
            lambda f, w, h: cairo.SVGSurface(f, w, h),
            lambda f, surface: None)}
    def surface(s):
        try:
            ext = s.rsplit(os.path.extsep, 1)[1]
            return (
                lambda w, h: surface_types[ext][0](s, w, h),
                lambda surface: surface_types[ext][1](s, surface))
        except KeyError as e:
            argparse.ArgumentTypeError(
                '"%s" is not a valid file extension' % e.args[0])
        except IndexError:
            argparse.ArgumentTypeError(
                'The image file must have a valid extension')
    class default:
        def write(*args, **kwargs):
            pass
    parser.add_argument('--image-output', type = surface,
        metavar = 'FILENAME',
        required = True,
        help = ('The name of the image file to create. Valid types are %s.') % (
            ', '.join(surface_types.keys())))

    def color(allow_rgba):
        def rgb(s):
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
            return result + (1.0,)
        def rgba(s):
            result = None
            m = re.match(r'''(?x)
                \#(?P<alpha>[0-9A-Fa-f]{2})
                 (?P<red>[0-9A-Fa-f]{2})
                 (?P<green>[0-9A-Fa-f]{2})
                 (?P<blue>[0-9A-Fa-f]{2})''', s)
            if not m is None:
                result = tuple(float(int(d, 16)) / 255
                    for d in m.groups()[1:] + (m.group(1),))
            else:
                m = re.match(r'''(?x)
                    rgba\(
                        \s*(?P<red>\d{1,3}%?)\s*,
                        \s*(?P<green>\d{1,3}%?)\s*,
                        \s*(?P<blue>\d{1,3}%?)\s*\,
                        \s*(?P<alpha>\d{1,3}%?)\s*\)''', s)
                if not m is None:
                    result = tuple(float(d) / 255 if d[-1].isdigit()
                        else float(d[:-1]) / 100 for d in m.groups())
            if result is None:
                return rgb(s)
            elif any(r < 0 or r > 1.0 for r in result):
                raise argparse.ArgumentTypeError(
                    '"%s" is not a valid colour.' % s)
            return result
        if allow_rgba:
            return rgba
        else:
            return rgb
    parser.add_argument('--image-background-color', type = color(True),
        metavar = 'COLOUR',
        default = (0.0, 0.0, 0.0),
        help = 'The background colour of the image. This must be specified as '
            'an HTML colour on the form #RRGGBB or rgb(r, g, b), or #AARRGGBB '
            'or rgba(r, g, b, a).')
    parser.add_argument('--image-wall-color', type = color(False),
        metavar = 'COLOUR',
        default = (1.0, 1.0, 1.0),
        help = 'The colour of the wall in the image. This must be specified as '
            'an HTML colour on the form #RRGGBB or rgb(r, g, b).')
    parser.add_argument('--image-path-color', type = color(True),
        metavar = 'COLOUR',
        default = (0.8, 0.4, 0.2),
        help = 'The colour of the path in the image. This must be specified as '
            'an HTML colour on the form #RRGGBB or rgb(r, g, b), or #AARRGGBB '
            'or rgba(r, g, b, a).')

    def line_width(s):
        result = int(s)
        if result < 2:
            raise argparse.ArgumentTypeError(
                'Line widths must be greater than 1')
        elif result & 1:
            raise argparse.ArgumentTypeError(
                'Line widths must be an even number')
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

    parser.add_argument('--image-path-smooth',
        action = 'store_true',
        default = False,
        help = 'Whether the path should be painted as a smooth curve instead '
            'of a sharp line.')

    namespace = parser.parse_args()

    # Create and initialise the maze
    maze = maze_classes[namespace.walls](*namespace.maze_size)
    initialize(maze, lambda max: random.randint(0, max - 1))
    solution = list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))

    print_maze(maze, solution, **dict(
            (name.split('_', 1)[1], value)
                for name, value in vars(namespace).items()
                if name.startswith('print_')))
    make_image(maze, solution, **dict(
            (name.split('_', 1)[1], value)
                for name, value in vars(namespace).items()
                if name.startswith('image_')))

