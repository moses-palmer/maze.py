import os
import sys

# Prefer in-tree library at ../../lib
libdir = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    os.path.pardir,
    'lib'))
sys.path = [libdir] + [sys_path for sys_path in sys.path
    if not os.path.abspath(sys_path) == libdir]

import math
import random

from tests import *
from maze import *
from maze.quad import *
from maze.tri import *
from maze.hex import *

import maze.randomized_prim as randomized_prim


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
def TriMaze_edge():
    maze = TriMaze(10, 20)

    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            for w in maze.Wall.WALLS:
                expected = (x, y) in maze and (False
                    or (w == maze.Wall.HORIZONTAL and y == 0 and not x % 2)
                    or (w == maze.Wall.HORIZONTAL and y == maze.height - 1
                        and (x + y) % 2)
                    or (w == maze.Wall.DIAGONAL_1 and x == 0 and not y % 2)
                    or (w == maze.Wall.DIAGONAL_2 and x == 0 and y % 2)
                    or (w == maze.Wall.DIAGONAL_1 and x == maze.width - 1
                        and (x + y) % 2)
                    or (w == maze.Wall.DIAGONAL_2 and x == maze.width - 1
                        and not (x + y) % 2))

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


@test
def TriMaze_walk_path():
    """Tests that the shortest path is selected"""
    maze = TriMaze(10, 20)

    maze[(1, 0):(1, 1)] = True
    maze[(1, 1):(2, 1)] = True
    maze[(2, 1):(3, 1)] = True
    maze[(3, 1):(3, 0)] = True

    assert_eq(
        list(maze.walk_path((1, 0), (3, 0))),
        [(1, 0), (1, 1), (2, 1), (3, 1), (3, 0)])

    maze[(1, 0):(2, 0)] = True
    maze[(2, 0):(3, 0)] = True

    assert_eq(
        list(maze.walk_path((1, 0), (3, 0))),
        [(1, 0), (2, 0), (3, 0)])


MAZE_TYPES = (Maze, TriMaze, HexMaze)

def maze_test(test_function = None, except_for = [], maze_size = (10, 20),
        **kwargs):
    """
    A decorator used to run a particular test for all types of mazes.

    It may be used as @maze_test, in which case the default options are used,
    or @maze_test(...) to specify options.

    @param except_for
        A list of maze types for which this test should not be run. This may
        also be a maze type, which it treated as a list containing only that
        type.
    @param maze_size
        The size of the maze used in the test.
    @param <maze type name> as data
        Data passed to the test function as the named parameter 'data'. None
    """
    if not test_function:
        return lambda test: maze_test(test, except_for, maze_size, **kwargs)

    try:
        except_for = iter(except_for)
    except TypeError:
        except_for = (except_for,)

    def inner():
        global MAZE_TYPES
        maze_classes = filter(
            lambda mc: not mc == except_for or mc in except_for,
            MAZE_TYPES)

        for maze_class in maze_classes:
            if maze_class in except_for:
                continue
            maze = maze_class(*maze_size)
            try:
                if maze.__class__.__name__ in kwargs:
                    test_function(maze, data = kwargs[maze.__class__.__name__])
                else:
                    test_function(maze)
            except Exception as e:
                e.message = 'For %s: %s' % (maze_class.__name__, e.message)
                raise

    inner.__doc__ = test_function.__doc__
    inner.__name__ = test_function.__name__

    return test(inner)


@maze_test(maze_size = (12, 34))
def maze_test_maze_size(maze):
    assert maze.width == 12 and maze.height == 34, \
        'Passing maze_size to maze_test did not change the size of the maze'


@maze_test
def Maze_Wall_fields(maze):
    """Tests that Maze.Wall contains the expected fields"""
    walls = set()

    assert_eq(len(maze.Wall.WALLS), len(maze.Wall.NAMES))
    assert_eq(len(maze.Wall.NAMES), len(set(maze.Wall.NAMES)))

    for a in (name.upper() for name in maze.Wall.NAMES):
        assert hasattr(maze.Wall, a), \
            'Wall.%s is undefined' % a

        w = getattr(maze.Wall, a)
        assert not w in walls, \
            '%s has a previously set value' % a

        walls.add(w)


@maze_test
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


@maze_test
def Maze_Wall_int(maze):
    """Test that int(wall) yields the correct value"""
    for w in maze.Wall.WALLS:
        wall = maze.Wall((0, 0), w)
        assert_eq(w, int(wall))


@maze_test(
    Maze = {
        (0, 0): (
            (-1, 0),
            (0, 1),
            (1, 0),
            (0, -1))},
    TriMaze = {
        (0, 0): (
            (-1, 0),
            (1, 0),
            (0, -1)),
        (0, 1): (
            (1, 0),
            (-1, 0),
            (0, 1)),
        (1, 0): (
            (1, 0),
            (-1, 0),
            (0, 1)),
        (0, 0): (
            (-1, 0),
            (1, 0),
            (0, -1))},
    HexMaze = {
        (0, 0): (
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, -1)),
        (0, 1): (
            (-1, 0),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1))})
def Maze_Wall_from_direction(maze, data):
    for room_pos, directions in data.items():
        for w, direction in enumerate(directions):
            expected = maze.Wall(room_pos, w)
            actual = maze.Wall.from_direction(room_pos, direction)
            assert_eq(expected, actual)


@maze_test(
    Maze = {
        ((1, 1), Maze.Wall.UP): (
            ((1, 2), Maze.Wall.LEFT),
            ((0, 2), Maze.Wall.DOWN),
            ((1, 1), Maze.Wall.LEFT)),
        ((1, 1), Maze.Wall.LEFT): (
            ((0, 1), Maze.Wall.DOWN),
            ((0, 0), Maze.Wall.RIGHT),
            ((1, 1), Maze.Wall.DOWN))},
    TriMaze = {
        ((1, 1), TriMaze.Wall.DIAGONAL_2): (
            ((2, 2), TriMaze.Wall.HORIZONTAL),
            ((1, 2), TriMaze.Wall.DIAGONAL_1),
            ((0, 2), TriMaze.Wall.DIAGONAL_2),
            ((0, 1), TriMaze.Wall.HORIZONTAL),
            ((1, 1), TriMaze.Wall.DIAGONAL_1)),
        ((3, 0), TriMaze.Wall.HORIZONTAL): (
            ((3, 1), TriMaze.Wall.DIAGONAL_1),
            ((2, 1), TriMaze.Wall.DIAGONAL_2),
            ((1, 1), TriMaze.Wall.HORIZONTAL),
            ((1, 0), TriMaze.Wall.DIAGONAL_1),
            ((2, 0), TriMaze.Wall.DIAGONAL_2))},
    HexMaze = {
        ((1, 1), HexMaze.Wall.UP_LEFT): (
            ((1, 2), HexMaze.Wall.DOWN_LEFT),
            ((0, 1), HexMaze.Wall.RIGHT)),
        ((1, 1), HexMaze.Wall.UP_RIGHT): (
            ((2, 2), HexMaze.Wall.LEFT),
            ((1, 2), HexMaze.Wall.DOWN_RIGHT))})
def Maze_Wall_from_corner(maze, data):
    for (room_pos, w), corner_walls in data.items():
        actual = tuple(maze.Wall.from_corner(room_pos, w))

        expected = (maze.Wall(room_pos, w),) + tuple(
            maze.Wall(corner_room_pos, corner_wall)
                for corner_room_pos, corner_wall in corner_walls)

        assert_eq(actual, expected)


@maze_test
def Maze_Wall_get_walls(maze):
    walls = set()

    for wall in maze.Wall.from_room_pos((10, 20)):
        assert_eq(wall.room_pos, (10, 20))

        if wall.wall in walls:
            assert False, \
                '%d was found twice' % int(wall)
        walls.add(int(wall))


@maze_test(
    except_for = TriMaze,
    Maze = (
        (((0, 0), Maze.Wall.LEFT), ((0, 0), Maze.Wall.RIGHT)),
        (((0, 0), Maze.Wall.UP), ((0, 0), Maze.Wall.DOWN)),
        (((0, 0), Maze.Wall.RIGHT), ((0, 0), Maze.Wall.LEFT)),
        (((0, 0), Maze.Wall.DOWN), ((0, 0), Maze.Wall.UP))),
    HexMaze = (
        (((0, 0), HexMaze.Wall.LEFT), ((0, 0), HexMaze.Wall.RIGHT)),
        (((0, 0), HexMaze.Wall.UP_LEFT), ((0, 0), HexMaze.Wall.DOWN_RIGHT)),
        (((0, 0), HexMaze.Wall.UP_RIGHT), ((0, 0), HexMaze.Wall.DOWN_LEFT)),
        (((0, 0), HexMaze.Wall.RIGHT), ((0, 0), HexMaze.Wall.LEFT)),
        (((0, 0), HexMaze.Wall.DOWN_RIGHT), ((0, 0), HexMaze.Wall.UP_LEFT)),
        (((0, 0), HexMaze.Wall.DOWN_LEFT), ((0, 0), HexMaze.Wall.UP_RIGHT))))
def Maze_Wall_opposite(maze, data):
    for (room_pos1, wall1), (room_pos2, wall2) in data:
        assert_eq(
            maze.Wall(room_pos1, wall1).opposite,
            maze.Wall(room_pos2, wall2))


@maze_test(
    Maze = (
        ((0, 0), Maze.Wall.LEFT, (-1, 0)),
        ((0, 0), Maze.Wall.UP, (0, 1)),
        ((0, 0), Maze.Wall.RIGHT, (1, 0)),
        ((0, 0), Maze.Wall.DOWN, (0, -1))),
    TriMaze = (
        ((0, 0), TriMaze.Wall.DIAGONAL_1, (-1, 0)),
        ((0, 1), TriMaze.Wall.DIAGONAL_1, (1, 0)),
        ((1, 0), TriMaze.Wall.DIAGONAL_1, (1, 0)),
        ((1, 1), TriMaze.Wall.DIAGONAL_1, (-1, 0)),
        ((0, 0), TriMaze.Wall.HORIZONTAL, (0, -1)),
        ((0, 1), TriMaze.Wall.HORIZONTAL, (0, 1)),
        ((1, 0), TriMaze.Wall.HORIZONTAL, (0, 1)),
        ((1, 1), TriMaze.Wall.HORIZONTAL, (0, -1)),
        ((0, 0), TriMaze.Wall.DIAGONAL_2, (1, 0)),
        ((0, 1), TriMaze.Wall.DIAGONAL_2, (-1, 0)),
        ((1, 0), TriMaze.Wall.DIAGONAL_2, (-1, 0)),
        ((1, 1), TriMaze.Wall.DIAGONAL_2, (1, 0))),
    HexMaze = (
        ((0, 0), HexMaze.Wall.LEFT, (-1, 0)),
        ((0, 1), HexMaze.Wall.LEFT, (-1, 0)),
        ((0, 0), HexMaze.Wall.UP_LEFT, (-1, 1)),
        ((0, 1), HexMaze.Wall.UP_LEFT, (0, 1)),
        ((0, 0), HexMaze.Wall.UP_RIGHT, (0, 1)),
        ((0, 1), HexMaze.Wall.UP_RIGHT, (1, 1)),
        ((0, 0), HexMaze.Wall.RIGHT, (1, 0)),
        ((0, 1), HexMaze.Wall.RIGHT, (1, 0)),
        ((0, 0), HexMaze.Wall.DOWN_RIGHT, (0, -1)),
        ((0, 1), HexMaze.Wall.DOWN_RIGHT, (1, -1)),
        ((0, 0), HexMaze.Wall.DOWN_LEFT, (-1, -1)),
        ((0, 1), HexMaze.Wall.DOWN_LEFT, (0, -1))))
def Maze_Wall_direction(maze, data):
    for room_pos, w, direction in data:
        assert_eq(maze.Wall(room_pos, w).direction, direction)


@maze_test(
    Maze = (
        (((1, 1), Maze.Wall.LEFT), ((0, 1), Maze.Wall.RIGHT)),
        (((1, 1), Maze.Wall.RIGHT), ((2, 1), Maze.Wall.LEFT)),
        (((1, 1), Maze.Wall.UP), ((1, 2), Maze.Wall.DOWN)),
        (((1, 1), Maze.Wall.DOWN), ((1, 0), Maze.Wall.UP))),
    TriMaze = (
        (((1, 1), TriMaze.Wall.DIAGONAL_1), ((0, 1), TriMaze.Wall.DIAGONAL_1)),
        (((1, 2), TriMaze.Wall.DIAGONAL_1), ((2, 2), TriMaze.Wall.DIAGONAL_1)),
        (((1, 1), TriMaze.Wall.HORIZONTAL), ((1, 0), TriMaze.Wall.HORIZONTAL)),
        (((1, 2), TriMaze.Wall.HORIZONTAL), ((1, 3), TriMaze.Wall.HORIZONTAL)),
        (((1, 1), TriMaze.Wall.DIAGONAL_2), ((2, 1), TriMaze.Wall.DIAGONAL_2)),
        (((1, 2), TriMaze.Wall.DIAGONAL_2), ((0, 2), TriMaze.Wall.DIAGONAL_2))),
    HexMaze = (
        (((1, 1), HexMaze.Wall.LEFT), ((0, 1), HexMaze.Wall.RIGHT)),
        (((1, 1), HexMaze.Wall.UP_LEFT), ((1, 2), HexMaze.Wall.DOWN_RIGHT)),
        (((1, 1), HexMaze.Wall.UP_RIGHT), ((2, 2), HexMaze.Wall.DOWN_LEFT)),
        (((1, 1), HexMaze.Wall.RIGHT), ((2, 1), HexMaze.Wall.LEFT)),
        (((1, 1), HexMaze.Wall.DOWN_RIGHT), ((2, 0), HexMaze.Wall.UP_LEFT)),
        (((1, 1), HexMaze.Wall.DOWN_LEFT), ((1, 0), HexMaze.Wall.UP_RIGHT))))
def Maze_Wall_back(maze, data):
    for f, b in data:
        front = maze.Wall(*f)
        back = maze.Wall(*b)
        assert_eq(front.back, back)
        assert_eq(back.back, front)



@maze_test
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


@maze_test
def Maze_Room_eq(maze):
    """Tests room1 == room2"""
    room1 = maze.Room()
    room2 = maze.Room()

    for wall in maze.Wall.WALLS:
        assert room1 == room2, \
            'Equal rooms did not compare equally'

        room1 += wall
        assert room1 != room2, \
            'Inequal rooms did not compare inequally'
        room2 += wall


@maze_test
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


@maze_test
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


@maze_test
def Maze_Room_bool(maze):
    """Tests that truth testing with Maze.Room works"""
    room = maze.Room()

    assert not room, \
        'An empty room tested True'

    for wall in maze.Wall.WALLS:
        room += wall
        assert room, \
            'A non-empty room tested False'


@maze_test
def Maze_pickle(maze):
    """Tests that pickling a maze works"""
    import pickle

    pickled = pickle.dumps(maze)


@maze_test
def Maze_unpickle(maze):
    """Tests that pickling a maze works"""
    import pickle

    pickled = pickle.dumps(maze)
    reconstructed = pickle.loads(pickled)

    for room_pos in maze.room_positions:
        assert maze[room_pos] == reconstructed[room_pos], \
            'Rooms at %s were different' % str(room_pos)


@maze_test(
    Maze = ((5, 6), (5, 7)),
    TriMaze = ((2, 1), (2, 2)),
    HexMaze = ((5, 6), (5, 7)))
def Maze_iter(maze, data):
    """Tests that for room_pos in maze: works"""
    actual = set()
    for room_pos in maze:
        actual.add(room_pos)
    assert_eq(actual, set())

    room_pos1, room_pos2 = data

    maze[room_pos1:room_pos2] = True
    actual = set()
    for room_pos in maze:
        actual.add(room_pos)
    assert_eq(actual, set((
        room_pos1,
        room_pos2)))


@maze_test
def Maze_index_tuple(maze):
    """Tests that indexing Maze with a tuple yields a Room"""
    assert isinstance(maze[3, 4], maze.Room), \
        'Maze[x, y] did not yield a Room'


@maze_test
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
        wall = maze.Wall((-5, -5), 0)
        other_room_pos = tuple(r + d
            for r, d in zip(wall.room_pos, wall.direction))
        maze[wall.room_pos:other_room_pos] = True
        assert False, \
            'Adding a door outside of the maze did not raise error'
    except IndexError:
        pass

    try:
        wall = maze.Wall((-5, -5), 0)
        other_room_pos = tuple(r + d
            for r, d in zip(wall.room_pos, wall.direction))
        maze[wall.room_pos:other_room_pos] = False
        assert False, \
            'Removing a door outside of the maze did not raise error'
    except IndexError:
        pass


@maze_test
def Maze_slice(maze):
    """Tests that reading a slice of a maze yields the path between the two
    rooms"""
    for y in xrange(maze.height):
        for x in xrange(maze.width):
            for wall in maze.walls((x, y)):
                if not maze.edge(wall):
                    maze[x, y][wall] = True

    assert_eq(
        list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1))),
        list(maze[(0, 0):(maze.width - 1, maze.height - 1)]))


@maze_test
def Maze_contains(maze):
    """Tests that room_pos in maze works"""
    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            expected = x >= 0 and x < maze.width and y >= 0 and y < maze.height
            actual = (x, y) in maze
            assert expected == actual, \
                '(%d, %d) in maze was incorrect (was %s)' % (x, y, actual)


@maze_test
def Maze_contains(maze):
    """Tests that wall in maze works"""
    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            expected = x >= 0 and x < maze.width and y >= 0 and y < maze.height
            actual = maze.Wall((x, y), 0) in maze
            assert expected == actual, \
                '(%d, %d) in maze was incorrect (was %s)' % (x, y, actual)


@maze_test
def Maze_width_and_height(maze):
    """Tests that the width and height properties are correct"""
    maze1 = maze.__class__(10, 20)
    assert_eq(maze1.width, 10)
    assert_eq(maze1.height, 20)

    maze2 = maze.__class__(200, 100)
    assert_eq(maze2.width, 200)
    assert_eq(maze2.height, 100)


@maze_test
def Maze_room_positions(maze):
    room_positions = set()
    for x in xrange(maze.width):
        for y in xrange(maze.height):
            room_positions.add((x, y))

    assert_eq(
        set(maze.room_positions),
        room_positions)


@maze_test
def Maze_edge_walls(maze):
    """Tests Maze.edge_wall for a large maze"""
    expected = set()
    for room_pos in maze.room_positions:
        for wall in maze.walls(room_pos):
            if maze.edge(wall):
                expected.add((room_pos, int(wall)))
    for w in maze.edge_walls:
        edge_wall = (w.room_pos, int(w))
        assert edge_wall in expected, \
            '%s is not on the edge' % str(w)
        expected.remove(edge_wall)


@maze_test(maze_size = (1, 10))
def Maze_edge_walls_tall(maze):
    """Tests Maze.edge_wall for a tall maze"""
    expected = set()
    for room_pos in maze.room_positions:
        for wall in maze.walls(room_pos):
            if maze.edge(wall):
                expected.add((room_pos, int(wall)))
    for w in maze.edge_walls:
        edge_wall = (w.room_pos, int(w))
        assert edge_wall in expected, \
            '%s is not on the edge' % str(w)
        expected.remove(edge_wall)


@maze_test(maze_size = (10, 1))
def Maze_edge_walls_wide(maze):
    """Tests Maze.edge_wall for a wide maze"""
    expected = set()
    for room_pos in maze.room_positions:
        for wall in maze.walls(room_pos):
            if maze.edge(wall):
                expected.add((room_pos, int(wall)))
    for w in maze.edge_walls:
        edge_wall = (w.room_pos, int(w))
        assert edge_wall in expected, \
            '%s is not on the edge' % str(w)
        expected.remove(edge_wall)


@maze_test
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
        wall = maze.Wall((-5, -5), 0)
        maze.add_door(wall.room_pos,
            tuple(r + d for r, d in zip(wall.room_pos, wall.direction)))
        assert False, \
            'Adding a door outside of the maze did not raise error'
    except IndexError:
        pass


@maze_test
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
        wall = maze.Wall((-5, -5), 0)
        maze.remove_door(wall.room_pos,
            tuple(r + d for r, d in zip(wall.room_pos, wall.direction)))
        assert False, \
            'Removing a door outside of the maze did not raise error'
    except IndexError:
        pass


@maze_test
def Maze_set_door(maze):
    room = maze[4, 4]

    for wall in maze.walls((4, 4)):
        assert not wall in room, \
            'A door was not initially missing'

    for wall in maze.walls((4, 4)):
        other_door = wall.back
        other_room = maze[other_door.room_pos]
        maze.set_door((4, 4), wall, True)

        assert wall in room, \
            'Maze.set_door did not open the door in the first room'
        assert wall.back in other_room, \
            'Maze.set_door did not open the door in the second room'

        maze.set_door((4, 4), int(wall), False)

        assert not wall in room, \
            'Maze.set_door did not close the door in the first room'
        assert not wall.back in other_room, \
            'Maze.set_door did not close the door in the second room'


@maze_test(except_for = TriMaze)
def Maze_get_center(maze):
    for room_pos in maze.room_positions:
        for wall in maze.walls(room_pos):
            if maze.edge(wall):
                continue

            center = maze.get_center(room_pos)
            corners = [(
                center[0] + math.cos(span),
                center[1] + math.sin(span)) for span in wall.span]

            other_center = maze.get_center(wall.back.room_pos)
            other_corners = [(
                other_center[0] + math.cos(span),
                other_center[1] + math.sin(span)) for span in wall.back.span]
            other_corner_display = tuple(other_corners)

            for corner in corners:
                found = False
                for other_corner in other_corners:
                    if math.sqrt(sum((c - oc)**2
                            for c, oc in zip(corner, other_corner))) < 0.001:
                        found = True
                        other_corners.remove(other_corner)
                        break

                assert found, \
                    'The corner %s for the wall %s did not meet a corner in ' \
                    'the back wall %s (with corners at %s)' % (
                        str(corner),
                        str(wall),
                        str(wall.back),
                        str(other_corner_display))


@maze_test
def Maze_adjacent(maze):
    adjacent = set(tuple(p + d for (p, d) in zip(wall.room_pos, wall.direction))
        for wall in maze.walls((5, 5)))

    for x, y in maze.room_positions:
        assert maze.adjacent((5, 5), (x, y)) == ((x, y) in adjacent), \
            'Room (%d, %d) incorrectly marked as %s to (5, 5)' % (x, y,
                'adjacent' if maze.adjacent((5, 5), (x, y)) else 'non-adjacent')


@maze_test(except_for = TriMaze)
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


@maze_test
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


@maze_test
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


@maze_test
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


@maze_test
def Maze_walls(maze):
    assert_eq(
        set(int(w) for w in maze.walls((1, 1))),
        set(maze.Wall.WALLS))


@maze_test
def Maze_walk_path(maze):
    """Tests that walking from one room to the same room always works"""
    assert_eq(
        list(maze.walk_path((2, 2), (2, 2))),
        [(2, 2)])


@maze_test
def Maze_walk_path(maze):
    """Tests that walking from a room outside of the maze raises ValueError"""
    try:
        list(maze.walk_path((-1, -1), (0, 0)))
        assert False, \
            'Managed to walk from (-1, -1)'
    except ValueError:
        pass


@maze_test
def Maze_walk_path(maze):
    """Tests that walking between non-connected rooms raises ValueError"""
    try:
        list(maze.walk_path((0, 0), (2, 0)))
        assert False, \
            'Managed to walk between non-connected rooms'
    except ValueError:
        pass


@maze_test
def Maze_walk_path(maze):
    """Tests that walking between adjacent rooms works as expected"""
    maze[(0, 0):(1, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (1, 0))),
        [(0, 0), (1, 0)])


@maze_test
def Maze_with_randomized_prim(maze):
    """Tests that randomized_prim.initialize creates a valid maze"""
    def rand(m):
        return random.randint(0, m - 1)

    randomized_prim.initialize(maze, rand)

    for x in xrange(0, maze.width):
        for y in xrange(0, maze.height):
            assert len(list(maze[(0, 0):(x, y)])) > 0, \
                'Could not walk from (%d, %d) to (0, 0)' % (x, y)
