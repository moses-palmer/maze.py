import math
import random

from tests import *
from maze import *

import maze.randomized_prim as randomized_prim

@test
def Maze_Wall_fields():
    """Tests that Maze.Wall contains the expected fields"""
    walls = set()

    assert_eq(len(Maze.Wall.NAMES), 4)

    for a in (name.upper() for name in Maze.Wall.NAMES):
        assert hasattr(Maze.Wall, a), \
            'Maze.Wall.%s is undefined' % a

        w = getattr(Maze.Wall, a)
        assert not w in walls, \
            'Wall.%s has a previously set value' % a

        walls.add(w)

    assert_eq(len(Maze.Wall.WALLS), len(Maze.Wall.NAMES))
    assert_eq(len(Maze.Wall.NAMES), len(set(Maze.Wall.NAMES)))


@test
def HexMaze_Wall_fields():
    """Tests that HexMaze.Wall contains the expected fields"""
    walls = set()

    assert_eq(len(HexMaze.Wall.NAMES), 6)

    for a in (name.upper() for name in HexMaze.Wall.NAMES):
        assert hasattr(HexMaze.Wall, a), \
            'HexMaze.Wall.%s is undefined' % a

        w = getattr(HexMaze.Wall, a)
        assert not w in walls, \
            'HexWall.%s has a previously set value' % a

        walls.add(w)

    assert_eq(len(HexMaze.Wall.WALLS), len(HexMaze.Wall.NAMES))
    assert_eq(len(HexMaze.Wall.NAMES), len(set(HexMaze.Wall.NAMES)))


@test
def Maze_Wall_from_direction():
    for w, direction in enumerate((
            (-1, 0),
            (0, 1),
            (1, 0),
            (0, -1))):
        expected = Maze.Wall((0, 0), w)
        actual = Maze.Wall.from_direction((0, 0), direction)
        assert_eq(expected, actual)


@test
def HexMaze_Wall_from_direction():
    for w, (direction, alt) in enumerate((
            ((-1, 0), None),
            ((-1, 1), (0, 1)),
            ((0, 1), (1, 1)),
            ((1, 0), None),
            ((0, -1), (1, -1)),
            ((-1, -1), (0, -1)))):
        expected = HexMaze.Wall((0, 0), w)
        actual = HexMaze.Wall.from_direction((0, 0), direction)
        assert_eq(expected, actual)

        if alt:
            expected = HexMaze.Wall((0, 1), w)
            actual = HexMaze.Wall.from_direction((0, 1), alt)
            assert_eq(expected, actual)


@test
def Maze_Wall_from_corner():
    assert_eq(
        tuple(Maze.Wall.from_corner((1, 1), Maze.Wall.UP)),
        (
            Maze.Wall((1, 1), Maze.Wall.UP),
            Maze.Wall((1, 2), Maze.Wall.LEFT),
            Maze.Wall((0, 2), Maze.Wall.DOWN),
            Maze.Wall((1, 1), Maze.Wall.LEFT)))
    assert_eq(
        tuple(Maze.Wall.from_corner((1, 1), Maze.Wall.LEFT)),
        (
            Maze.Wall((1, 1), Maze.Wall.LEFT),
            Maze.Wall((0, 1), Maze.Wall.DOWN),
            Maze.Wall((0, 0), Maze.Wall.RIGHT),
            Maze.Wall((1, 1), Maze.Wall.DOWN)))


@test
def Maze_Wall_from_corner():
    assert_eq(
        tuple(Maze.Wall.from_corner((1, 1), Maze.Wall.UP)),
        (
            Maze.Wall((1, 1), Maze.Wall.UP),
            Maze.Wall((1, 2), Maze.Wall.LEFT),
            Maze.Wall((0, 2), Maze.Wall.DOWN),
            Maze.Wall((1, 1), Maze.Wall.LEFT)))


@test
def HexMaze_Wall_from_corner():
    assert_eq(
        tuple(HexMaze.Wall.from_corner((1, 1), HexMaze.Wall.UP_LEFT)),
        (
            HexMaze.Wall((1, 1), HexMaze.Wall.UP_LEFT),
            HexMaze.Wall((1, 2), HexMaze.Wall.DOWN_LEFT),
            HexMaze.Wall((0, 1), HexMaze.Wall.RIGHT)))
    assert_eq(
        tuple(HexMaze.Wall.from_corner((1, 1), HexMaze.Wall.UP_RIGHT)),
        (
            HexMaze.Wall((1, 1), HexMaze.Wall.UP_RIGHT),
            HexMaze.Wall((2, 2), HexMaze.Wall.LEFT),
            HexMaze.Wall((1, 2), HexMaze.Wall.DOWN_RIGHT)))


@test
def Maze_Wall_opposite():
    assert_eq(
        Maze.Wall((0, 0), Maze.Wall.LEFT).opposite,
        Maze.Wall((0, 0), Maze.Wall.RIGHT))
    assert_eq(
        Maze.Wall((0, 0), Maze.Wall.UP).opposite,
        Maze.Wall((0, 0), Maze.Wall.DOWN))
    assert_eq(
        Maze.Wall((0, 0), Maze.Wall.RIGHT).opposite,
        Maze.Wall((0, 0), Maze.Wall.LEFT))
    assert_eq(
        Maze.Wall((0, 0), Maze.Wall.DOWN).opposite,
        Maze.Wall((0, 0), Maze.Wall.UP))


@test
def HexMaze_Wall_opposite():
    assert_eq(
        HexMaze.Wall((0, 0), HexMaze.Wall.LEFT).opposite,
        HexMaze.Wall((0, 0), HexMaze.Wall.RIGHT))
    assert_eq(
        HexMaze.Wall((0, 0), HexMaze.Wall.UP_LEFT).opposite,
        HexMaze.Wall((0, 0), HexMaze.Wall.DOWN_RIGHT))
    assert_eq(
        HexMaze.Wall((0, 0), HexMaze.Wall.UP_RIGHT).opposite,
        HexMaze.Wall((0, 0), HexMaze.Wall.DOWN_LEFT))
    assert_eq(
        HexMaze.Wall((0, 0), HexMaze.Wall.RIGHT).opposite,
        HexMaze.Wall((0, 0), HexMaze.Wall.LEFT))
    assert_eq(
        HexMaze.Wall((0, 0), HexMaze.Wall.DOWN_RIGHT).opposite,
        HexMaze.Wall((0, 0), HexMaze.Wall.UP_LEFT))
    assert_eq(
        HexMaze.Wall((0, 0), HexMaze.Wall.DOWN_LEFT).opposite,
        HexMaze.Wall((0, 0), HexMaze.Wall.UP_RIGHT))


@test
def Maze_Wall_direction():
    assert_eq(Maze.Wall((0, 0), Maze.Wall.LEFT).direction, (-1, 0))
    assert_eq(Maze.Wall((0, 0), Maze.Wall.UP).direction, (0, 1))
    assert_eq(Maze.Wall((0, 0), Maze.Wall.RIGHT).direction, (1, 0))
    assert_eq(Maze.Wall((0, 0), Maze.Wall.DOWN).direction, (0, -1))


@test
def HexMaze_Wall_direction():
    assert_eq(HexMaze.Wall((0, 0), HexMaze.Wall.LEFT).direction, (-1, 0))
    assert_eq(HexMaze.Wall((0, 1), HexMaze.Wall.LEFT).direction, (-1, 0))

    assert_eq(HexMaze.Wall((0, 0), HexMaze.Wall.UP_LEFT).direction, (-1, 1))
    assert_eq(HexMaze.Wall((0, 1), HexMaze.Wall.UP_LEFT).direction, (0, 1))

    assert_eq(HexMaze.Wall((0, 0), HexMaze.Wall.UP_RIGHT).direction, (0, 1))
    assert_eq(HexMaze.Wall((0, 1), HexMaze.Wall.UP_RIGHT).direction, (1, 1))

    assert_eq(HexMaze.Wall((0, 0), HexMaze.Wall.RIGHT).direction, (1, 0))
    assert_eq(HexMaze.Wall((0, 1), HexMaze.Wall.RIGHT).direction, (1, 0))

    assert_eq(HexMaze.Wall((0, 0), HexMaze.Wall.DOWN_RIGHT).direction, (0, -1))
    assert_eq(HexMaze.Wall((0, 1), HexMaze.Wall.DOWN_RIGHT).direction, (1, -1))

    assert_eq(HexMaze.Wall((0, 0), HexMaze.Wall.DOWN_LEFT).direction, (-1, -1))
    assert_eq(HexMaze.Wall((0, 1), HexMaze.Wall.DOWN_LEFT).direction, (0, -1))


@test
def Maze_Wall_back():
    assert Maze.Wall((1, 1), Maze.Wall.LEFT).back \
            == Maze.Wall((0, 1), Maze.Wall.RIGHT), \
        'Back of left wall in(1, 1) was incorrect'
    assert Maze.Wall((1, 1), Maze.Wall.RIGHT).back \
            == Maze.Wall((2, 1), Maze.Wall.LEFT), \
        'Back of right wall in(1, 1) was incorrect'
    assert Maze.Wall((1, 1), Maze.Wall.UP).back == \
            Maze.Wall((1, 2), Maze.Wall.DOWN), \
        'Back of up wall in(1, 1) was incorrect'
    assert Maze.Wall((1, 1), Maze.Wall.DOWN).back \
            == Maze.Wall((1, 0), Maze.Wall.UP), \
        'Back of down wall in(1, 1) was incorrect'


@test
def HexMaze_Wall_back():
    assert HexMaze.Wall((1, 1), HexMaze.Wall.LEFT).back \
            == HexMaze.Wall((0, 1), HexMaze.Wall.RIGHT), \
        'Back of left wall in (1, 1) was incorrect'
    assert HexMaze.Wall((1, 1), HexMaze.Wall.UP_LEFT).back \
            == HexMaze.Wall((1, 2), HexMaze.Wall.DOWN_RIGHT), \
        'Back of up-left wall in (1, 1) was incorrect'
    assert HexMaze.Wall((1, 1), HexMaze.Wall.UP_RIGHT).back \
            == HexMaze.Wall((2, 2), HexMaze.Wall.DOWN_LEFT), \
        'Back of up-right wall in (1, 1) was incorrect'
    assert HexMaze.Wall((1, 1), HexMaze.Wall.RIGHT).back \
            == HexMaze.Wall((2, 1), HexMaze.Wall.LEFT), \
        'Back of right wall in (1, 1) was incorrect'
    assert HexMaze.Wall((1, 1), HexMaze.Wall.DOWN_RIGHT).back \
            == HexMaze.Wall((2, 0), HexMaze.Wall.UP_LEFT), \
        'Back of down-right wall in (1, 1) was incorrect'
    assert HexMaze.Wall((1, 1), HexMaze.Wall.DOWN_LEFT).back \
            == HexMaze.Wall((1, 0), HexMaze.Wall.UP_RIGHT), \
        'Back of down-left wall in (1, 1) was incorrect'


@test
def Maze_get_center():
    maze = Maze(10, 20)

    assert_eq(maze.get_center((0, 0)), (0.5, 0.5))


@test
def HexMaze_get_center():
    maze = HexMaze(10, 20)

    assert_eq(maze.get_center((0, 0)), (0.5, 0.5))
    assert sum(abs(a - b) for a, b in zip(
            maze.get_center((0, 1)),
            (1.0, 0.5 + 1.0 - 0.5 * math.sin(5 * math.pi / 6)))) < 0.001, \
        'The room (0, 1) is incorrectly centered'


@test
def Maze_edge():
    maze = Maze(10, 20)

    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            for w in maze.Wall.WALLS:
                expected = False
                if w == maze.Wall.LEFT and x == 0 \
                        and (x, y) in maze:
                    expected = True
                if w == maze.Wall.DOWN and y == 0 \
                        and (x, y) in maze:
                    expected = True
                if w == maze.Wall.RIGHT and x == maze.width - 1 \
                        and (x, y) in maze:
                    expected = True
                if w == maze.Wall.UP and y == maze.height - 1 \
                        and (x, y) in maze:
                    expected = True
                actual = maze.edge(maze.Wall((x, y), w))
                assert expected == actual, \
                    '((%d, %d), %s)) was incorrectly labelled as %s' % (
                        x, y,
                        maze.Wall.NAMES[w],
                        'edge' if not expected else 'non-edge')


@test
def HexMaze_edge():
    maze = HexMaze(10, 20)

    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            for w in maze.Wall.WALLS:
                expected = (x, y) in maze and (False
                    or (w == maze.Wall.LEFT and x == 0)
                    or ((w == maze.Wall.UP_LEFT or w == maze.Wall.UP_RIGHT)
                        and y == maze.height - 1)
                    or (w == maze.Wall.UP_LEFT and x == 0 and not y % 2)
                    or (w == maze.Wall.UP_RIGHT and x == maze.width - 1
                        and y % 2)
                    or (w == maze.Wall.RIGHT and x == maze.width - 1)
                    or ((w == maze.Wall.DOWN_RIGHT or w == maze.Wall.DOWN_LEFT)
                        and y == 0)
                    or (w == maze.Wall.DOWN_RIGHT and x == maze.width - 1
                        and y % 2)
                    or (w == maze.Wall.DOWN_LEFT and x == 0 and not y % 2))

                actual = maze.edge(maze.Wall((x, y), w))
                assert expected == actual, \
                    '((%d, %d), %s)) was incorrectly labelled as %s' % (
                        x, y,
                        maze.Wall.NAMES[w],
                        'edge' if not expected else 'non-edge')


@test
def Maze_walk_path():
    """Tests that the shortest path is selected"""
    maze = Maze(10, 20)

    maze[(0, 0):(0, 1)] = True
    maze[(0, 1):(1, 1)] = True
    maze[(1, 1):(2, 1)] = True
    maze[(2, 1):(2, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (2, 0))),
        [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)])

    maze[(0, 0):(1, 0)] = True
    maze[(1, 0):(2, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (2, 0))),
        [(0, 0), (1, 0), (2, 0)])


@test
def HexMaze_walk_path():
    """Tests that the shortest path is selected"""
    maze = HexMaze(10, 20)

    maze[(0, 0):(0, 1)] = True
    maze[(0, 1):(1, 1)] = True
    maze[(1, 1):(2, 1)] = True
    maze[(2, 1):(2, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (2, 0))),
        [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)])

    maze[(0, 0):(1, 0)] = True
    maze[(1, 0):(2, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (2, 0))),
        [(0, 0), (1, 0), (2, 0)])


def all_mazes(test):
    """
    A decorator used to run a particular test for all types of mazes.
    """
    def inner():
        for maze_class in (Maze, HexMaze):
            maze = maze_class(10, 20)
            try:
                test(maze)
            except Exception as e:
                e.message = 'For %s: %s' % (maze_class.__name__, e.message)
                raise

    inner.__doc__ = test.__doc__
    inner.__name__ = test.__name__

    return inner


@test
@all_mazes
def Maze_Wall_eq(maze):
    """Tests wall1 == wall2"""
    assert maze.Wall((1, 1), maze.Wall.WALLS[0]) \
            == maze.Wall((1, 1), maze.Wall.WALLS[0]), \
        'Equal wall did not compare equally'
    assert maze.Wall((1, 2), maze.Wall.WALLS[0]) \
            != maze.Wall((1, 1), maze.Wall.WALLS[0]), \
        'Walls with equal wall index and different positions compared equally'
    assert maze.Wall((1, 2), maze.Wall.WALLS[0]) \
            != maze.Wall((1, 2), maze.Wall.WALLS[1]), \
        'Walls with different wall index and equal positions compared equally'

    for w in maze.Wall.WALLS:
        assert maze.Wall((1, 2), w) == maze.Wall((1, 2), w).back, \
            'Wall did not compare equally with its back'


@test
@all_mazes
def Maze_Wall_int(maze):
    """Test that int(wall) yields the correct value"""
    for w in maze.Wall.WALLS:
        wall = maze.Wall((0, 0), w)
        assert_eq(w, int(wall))


@test
@all_mazes
def Maze_Wall_get_walls(maze):
    walls = set()

    for wall in maze.Wall.from_room_pos((10, 20)):
        assert_eq(wall.room_pos, (10, 20))

        if wall.wall in walls:
            assert False, \
                '%d was found twice' % int(wall)
        walls.add(int(wall))


@test
@all_mazes
def Maze_Wall_back(maze):
    for wall in maze.walls((1, 1)):
        x, y = (p + d for (p, d) in zip(wall.room_pos, wall.direction))
        w = wall.opposite.wall
        assert_eq(wall.back, maze.Wall((x, y), w))


@test
@all_mazes
def Maze_Wall_span(maze):
    first_span = maze.Wall((0, 0), maze.Wall.WALLS[0]).span
    first_d = math.sin(first_span[1] - first_span[0])
    last_span = first_span

    for wall in maze.Wall.WALLS[1:]:
        span = maze.Wall((0, 0), wall).span
        assert last_span[1] == span[0], \
            'Walls are not continuous at %d' % wall
        assert abs(first_d - math.sin(span[1] - span[0])) < 0.001, \
            'Wall lengths are not uniform (%f != %f)' % (
                first_d, math.sin(span[1] - span[0]))
        last_span = span

    assert last_span[1] == first_span[0], \
        'Walls do not cover entire room'


@test
@all_mazes
def Maze_Room_door_functions(maze):
    """Tests that Maze.Room.add_door, remove_door and has_door work"""
    room = maze.Room()

    assert all(not room.has_door(wall)
            for wall in maze.Wall.WALLS), \
        'Not all walls were empty when Room was created'

    room.add_door(maze.Wall.WALLS[0])
    assert all(not room.has_door(wall) or wall == maze.Wall.WALLS[0]
            for wall in maze.Wall.WALLS), \
        'Adding left door did not have the expected effect (doors = %d)' % (
            room.doors)

    for wall in maze.Wall.WALLS:
        room.add_door(wall)
    assert_eq(room.doors, set(maze.Wall.WALLS))

    room.remove_door(maze.Wall.WALLS[1])
    assert all(room.has_door(wall) or wall == maze.Wall.WALLS[1]
            for wall in maze.Wall.WALLS), \
        'Removing right door did not have the expected effect (doors = %d)' % (
            room.doors)


@test
@all_mazes
def Maze_Room_door_operators(maze):
    """Tests that the operator overloads work"""
    room = maze.Room()

    assert all(not wall in room and not room[wall]
            for wall in maze.Wall.WALLS), \
        'Not all walls were empty when Room was created'

    room[Maze.Wall.WALLS[0]] = True
    assert all(not wall in room and not room[wall] or wall == maze.Wall.WALLS[0]
            for wall in maze.Wall.WALLS), \
        'Adding left door did not have the expected effect (doors = %d)' % (
            room.doors)

    for wall in maze.Wall.WALLS:
        room += wall
    assert_eq(room.doors, set(maze.Wall.WALLS))

    room -= maze.Wall.WALLS[1]
    assert all(wall in room and room[wall] or wall == maze.Wall.WALLS[1]
            for wall in maze.Wall.WALLS), \
        'Removing right door did not have the expected effect (doors = %d)' % (
            room.doors)


@test
@all_mazes
def Maze_Room_bool(maze):
    """Tests that truth testing with Maze.Room works"""
    room = maze.Room()

    assert not room, \
        'An empty room tested True'

    for wall in maze.Wall.WALLS:
        room += wall
        assert room, \
            'A non-empty room tested False'


@test
@all_mazes
def Maze_iter(maze):
    """Tests that for room_pos in maze: works"""
    actual = set()
    for room_pos in maze:
        actual.add(room_pos)
    assert_eq(actual, set())

    maze[(5, 6):(5, 7)] = True
    actual = set()
    for room_pos in maze:
        actual.add(room_pos)
    assert_eq(actual, set((
        (5, 6),
        (5, 7))))


@test
@all_mazes
def Maze_index_tuple(maze):
    """Tests that indexing Maze with a tuple yields a Room"""
    assert isinstance(maze[3, 4], maze.Room), \
        'Maze[x, y] did not yield a Room'


@test
@all_mazes
def Maze_index_tuple(maze):
    """Tests that assigning to Maze[(x1, y1):(x2, y2)] works"""
    room = maze[4, 4]

    for wall in maze.walls((4, 4)):
        assert not wall in room, \
            'A door was not initially missing'

    for wall in maze.walls((4, 4)):
        other_door = wall.back
        other_room = maze[other_door.room_pos]
        maze[(4, 4):other_door.room_pos] = True

        assert wall in room, \
            'Maze[(4, 4):%s] = True did not open the door in (4, 4)' % (
                str(other_door.room_pos))
        assert wall.back in other_room, \
            'Maze[(4, 4):%s] = False did not open the door in %s' % (
                str(other_door.room_pos), str(other_door.room_pos))

    for wall in maze.walls((4, 4)):
        other_door = wall.back
        other_room = maze[other_door.room_pos]
        maze[(4, 4):other_door.room_pos] = False

        assert not wall in room, \
            'Maze[(4, 4):%s] = False did not close the door in (4, 4)' % (
                str(other_door.room_pos))
        assert not wall.back in other_room, \
            'Maze[(4, 4):%s] = False did not close the door in %s' % (
                str(other_door.room_pos), str(other_door.room_pos))

    for x, y in maze:
        failure_required = not maze.adjacent((7, 7), (x, y))
        try:
            maze[(7, 7):(x, y)] = True
            assert not failure_required, \
                'Adding a door between non-adjacent rooms did not raise error'
        except ValueError:
            assert failure_required, \
                'Adding a door between adjacent rooms raised error'

        try:
            maze[(7, 7):(x, y)] = False
            assert not failure_required, \
                'Removing a door between non-adjacent rooms did not raise error'
        except ValueError:
            assert failure_required, \
                'Removing a door between adjacent rooms raised error'

    try:
        maze[(-1, -1):(-1, 0)] = True
        assert False, \
            'Adding a door outside of the maze did not raise error'
    except IndexError:
        pass

    try:
        maze[(-1, -1):(-1, 0)] = False
        assert False, \
            'Removing a door outside of the maze did not raise error'
    except IndexError:
        pass


@test
@all_mazes
def Maze_slice(maze):
    """Tests that reading a slice of a maze yields the path between the two
    rooms"""
    for y in xrange(maze.height):
        row = xrange(maze.width) if y == 0 or y == maze.height - 1 \
            else (0, maze.width - 1)
        for x in row:
            for wall in maze.walls((x, y)):
                if not maze.edge(wall):
                    maze[x, y][wall] = True

    assert_eq(
        list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1))),
        list(maze[(0, 0):(maze.width - 1, maze.height - 1)]))


@test
@all_mazes
def Maze_contains(maze):
    """Tests that room_pos in maze works"""
    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            expected = x >= 0 and x < maze.width and y >= 0 and y < maze.height
            actual = (x, y) in maze
            assert expected == actual, \
                '(%d, %d) in maze was incorrect (was %s)' % (x, y, actual)


@test
@all_mazes
def Maze_contains(maze):
    """Tests that wall in maze works"""
    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            expected = x >= 0 and x < maze.width and y >= 0 and y < maze.height
            actual = maze.Wall((x, y), 0) in maze
            assert expected == actual, \
                '(%d, %d) in maze was incorrect (was %s)' % (x, y, actual)


@test
@all_mazes
def Maze_width_and_height(maze):
    """Tests that the width and height properties are correct"""
    maze1 = maze.__class__(10, 20)
    assert_eq(maze1.width, 10)
    assert_eq(maze1.height, 20)

    maze2 = maze.__class__(200, 100)
    assert_eq(maze2.width, 200)
    assert_eq(maze2.height, 100)


@test
@all_mazes
def Maze_room_positions(maze):
    room_positions = set()
    for x in xrange(maze.width):
        for y in xrange(maze.height):
            room_positions.add((x, y))

    assert_eq(
        set(maze.room_positions),
        room_positions)


@test
@all_mazes
def Maze_add_door(maze):
    room = maze[4, 4]

    for wall in maze.walls((4, 4)):
        assert not wall in room, \
            'A door was not initially missing'

    for wall in maze.walls((4, 4)):
        other_door = wall.back
        other_room = maze[other_door.room_pos]
        maze.add_door((4, 4), other_door.room_pos)

        assert wall in room, \
            'Maze.add_door did not open the door in the first room'
        assert wall.back in other_room, \
            'Maze.add_door did not open the door in the second room'

    for x, y in maze:
        failure_required = not maze.adjacent((7, 7), (x, y))
        try:
            maze.add_door((7, 7), (x, y))
            assert not failure_required, \
                'Adding a door between non-adjacent rooms did not raise error'
        except ValueError:
            assert failure_required, \
                'Adding a door between adjacent rooms raised error'

    try:
        maze.add_door((-1, -1), (-1, 0))
        assert False, \
            'Adding a door outside of the maze did not raise error'
    except IndexError:
        pass


@test
@all_mazes
def Maze_remove_door(maze):
    room = maze[4, 4]

    for wall in maze.walls((4, 4)):
        maze.add_door((4, 4), wall.back.room_pos)

    for wall in maze.walls((4, 4)):
        other_door = wall.back
        other_room = maze[other_door.room_pos]
        maze.remove_door((4, 4), other_door.room_pos)

        assert not wall in room, \
            'Maze.remove_door did not close the door in the first room'
        assert not wall.back in other_room, \
            'Maze.remove_door did not close the door in the second room'

    for x, y in maze:
        failure_required = not maze.adjacent((7, 7), (x, y))
        try:
            maze.add_door((7, 7), (x, y))
            assert not failure_required, \
                'Removing a door between non-adjacent rooms did not raise error'
        except ValueError:
            assert failure_required, \
                'Removing a door between adjacent rooms raised error'

    try:
        maze.add_door((-1, -1), (-1, 0))
        assert False, \
            'Removing a door outside of the maze did not raise error'
    except IndexError:
        pass


@test
@all_mazes
def Maze_adjacent(maze):
    adjacent = set(tuple(p + d for (p, d) in zip(wall.room_pos, wall.direction))
        for wall in maze.walls((5, 5)))

    for x, y in maze.room_positions:
        assert maze.adjacent((5, 5), (x, y)) == ((x, y) in adjacent), \
            'Room (%d, %d) incorrectly marked as %s to (5, 5)' % (x, y,
                'adjacent' if maze.adjacent((5, 5), (x, y)) else 'non-adjacent')


@test
@all_mazes
def Maze_connected(maze):
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            connected1 = maze.connected((4, 4), (4 + x, 4 + y))
            connected2 = False
            assert connected1 == connected2, \
                '(4, 4) %s be connected to (%d, %d)' % (
                    'should' if connected2 else 'should not',
                    4 + x,
                    4 + y)

    maze.add_door((3, 4), (4, 4))
    maze.add_door((4, 4), (5, 4))

    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            connected1 = maze.connected((4, 4), (4 + x, 4 + y))
            connected2 = y == 0 and x != 0
            assert connected1 == connected2, \
                '(4, 4) %s be connected to (%d, %d)' % (
                    'should' if connected2 else 'should not',
                    4 + x,
                    4 + y)


@test
@all_mazes
def Maze_walk_from(maze):
    for x, y in maze.room_positions:
        for wall in maze.walls((x, y)):
            dx, dy = wall.direction
            nx, ny = x + dx, y + dy
            if (nx, ny) in maze:
                assert_eq(maze.walk_from((x, y), int(wall)), (x + dx, y + dy))

                try:
                    maze.walk_from((x, y), int(wall), True)
                except ValueError:
                    pass
            else:
                try:
                    maze.walk_from((x, y), int(wall))
                except IndexError:
                    pass


@test
@all_mazes
def Maze_walk_from(maze):
    for x, y in maze.room_positions:
        for wall in maze.walls((x, y)):
            dx, dy = wall.direction
            nx, ny = x + dx, y + dy
            if (nx, ny) in maze:
                assert_eq(maze.walk(wall), (x + dx, y + dy))

                try:
                    maze.walk(wall, True)
                except ValueError:
                    pass
            else:
                try:
                    maze.walk(wall)
                except IndexError:
                    pass


@test
@all_mazes
def Maze_doors(maze):
    assert_eq(
        list(maze.doors((1, 1))),
        [])

    doors = []

    for w in maze.Wall.WALLS:
        wall = maze.Wall((1, 1), w)
        doors.append(int(wall))
        maze.add_door((1, 1), (1 + wall.direction[0], 1 + wall.direction[1]))
        assert_eq(
            set(int(w) for w in maze.doors((1, 1))),
            set(doors))


@test
@all_mazes
def Maze_walls(maze):
    assert_eq(
        set(int(w) for w in maze.walls((1, 1))),
        set(maze.Wall.WALLS))


@test
@all_mazes
def Maze_walk_path(maze):
    """Tests that walking from one room to the same room always works"""
    assert_eq(
        list(maze.walk_path((2, 2), (2, 2))),
        [(2, 2)])


@test
@all_mazes
def Maze_walk_path(maze):
    """Tests that walking from a room outside of the maze raises ValueError"""
    try:
        list(maze.walk_path((-1, -1), (0, 0)))
        assert False, \
            'Managed to walk from (-1, -1)'
    except ValueError:
        pass


@test
@all_mazes
def Maze_walk_path(maze):
    """Tests that walking between non-connected rooms raises ValueError"""
    try:
        list(maze.walk_path((0, 0), (2, 0)))
        assert False, \
            'Managed to walk between non-connected rooms'
    except ValueError:
        pass


@test
@all_mazes
def Maze_walk_path(maze):
    """Tests that walking between adjacent rooms works as expected"""
    maze[(0, 0):(1, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (1, 0))),
        [(0, 0), (1, 0)])


@test
@all_mazes
def Maze_with_randomized_prim(maze):
    """Tests that randomized_prim.initialize creates a valid maze"""
    def rand(m):
        return random.randint(0, m - 1)

    randomized_prim.initialize(maze, rand)

    for x in xrange(0, maze.width):
        for y in xrange(0, maze.height):
            assert len(list(maze[(0, 0):(x, y)])) > 0, \
                'Could not walk from (%d, %d) to (0, 0)' % (x, y)
