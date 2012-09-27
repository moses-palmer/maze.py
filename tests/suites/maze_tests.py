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

    assert_eq(len(Maze.Wall.WALLS), len(Maze.Wall.DIRECTIONS))
    assert_eq(len(Maze.Wall.DIRECTIONS), len(set(Maze.Wall.DIRECTIONS)))
    assert_eq(len(Maze.Wall.WALLS), len(Maze.Wall.NAMES))
    assert_eq(len(Maze.Wall.NAMES), len(set(Maze.Wall.NAMES)))


@test
def Maze_Wall_from_direction():
    for w, direction in enumerate(Maze.Wall.DIRECTIONS):
        expected = Maze.Wall((0, 0), w)
        actual = Maze.Wall.from_direction((0, 0), direction)
        assert_eq(expected, actual)


@test
def Maze_Wall_get_opposite():
    assert_eq(Maze.Wall.get_opposite(Maze.Wall.LEFT), Maze.Wall.RIGHT)
    assert_eq(Maze.Wall.get_opposite(Maze.Wall.UP), Maze.Wall.DOWN)
    assert_eq(Maze.Wall.get_opposite(Maze.Wall.RIGHT), Maze.Wall.LEFT)
    assert_eq(Maze.Wall.get_opposite(Maze.Wall.DOWN), Maze.Wall.UP)


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
def Maze_Wall_get_span():
    first_span = Maze.Wall.get_span(Maze.Wall.WALLS[0])
    first_d = math.sin(first_span[1] - first_span[0])
    last_span = first_span

    for wall in Maze.Wall.WALLS[1:]:
        span = Maze.Wall.get_span(wall)
        assert last_span[1] == span[0], \
            'Walls are not continuous'
        assert first_d == math.sin(span[1] - span[0]), \
            'Wall lengths are not uniform'
        last_span = span

    assert last_span[1] == first_span[0], \
        'Walls do not cover entire room'


@test
def Maze_Wall_span():
    first_span = Maze.Wall((0, 0), Maze.Wall.WALLS[0]).span
    first_d = math.sin(first_span[1] - first_span[0])
    last_span = first_span

    for wall in Maze.Wall.WALLS[1:]:
        span = Maze.Wall((0, 0), wall).span
        assert last_span[1] == span[0], \
            'Walls are not continuous'
        assert first_d == math.sin(span[1] - span[0]), \
            'Wall lengths are not uniform'
        last_span = span

    assert last_span[1] == first_span[0], \
        'Walls do not cover entire room'


@test
def Maze_Wall_get_direction():
    assert_eq(Maze.Wall.get_direction(Maze.Wall.LEFT), (-1, 0))
    assert_eq(Maze.Wall.get_direction(Maze.Wall.UP), (0, 1))
    assert_eq(Maze.Wall.get_direction(Maze.Wall.RIGHT), (1, 0))
    assert_eq(Maze.Wall.get_direction(Maze.Wall.DOWN), (0, -1))


@test
def Maze_Wall_direction():
    assert_eq(Maze.Wall((0, 0), Maze.Wall.LEFT).direction, (-1, 0))
    assert_eq(Maze.Wall((0, 0), Maze.Wall.UP).direction, (0, 1))
    assert_eq(Maze.Wall((0, 0), Maze.Wall.RIGHT).direction, (1, 0))
    assert_eq(Maze.Wall((0, 0), Maze.Wall.DOWN).direction, (0, -1))


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
def Maze_Wall_get_walls():
    walls = set()

    for wall in Maze.Wall.get_walls((10, 20)):
        assert_eq(wall.room_pos, (10, 20))

        if wall.wall in walls:
            assert False, \
                '%s was found twice' % Maze.Wall.NAMES[wall]
        walls.add(wall.wall)


@test
def Maze_Wall_eq():
    """Tests wall1 == wall2"""
    assert Maze.Wall((1, 1), Maze.Wall.LEFT) \
            == Maze.Wall((1, 1), Maze.Wall.LEFT), \
        'Equal wall did not compare equally'
    assert Maze.Wall((1, 2), Maze.Wall.LEFT) \
            != Maze.Wall((1, 1), Maze.Wall.LEFT), \
        'Walls with equal wall index and different positions compared equally'
    assert Maze.Wall((1, 2), Maze.Wall.LEFT) \
            != Maze.Wall((1, 2), Maze.Wall.RIGHT), \
        'Walls with different wall index and equal positions compared equally'


@test
def Maze_Wall_int():
    """Test that int(wall) yields the correct value"""
    for w in Maze.Wall.WALLS:
        wall = Maze.Wall((0, 0), w)
        assert_eq(w, int(wall))


@test
def Maze_Room_door_functions():
    """Tests that Maze.Room.add_door, remove_door and has_door work"""
    room = Maze.Room()

    assert all(not room.has_door(wall)
            for wall in Maze.Wall.WALLS), \
        'Not all walls were empty when Room was created'

    room.add_door(Maze.Wall.LEFT)
    assert all(not room.has_door(wall) or wall == Maze.Wall.LEFT
            for wall in Maze.Wall.WALLS), \
        'Adding left door did not have the expected effect (doors = %d)' % (
            room.doors)

    for wall in Maze.Wall.WALLS:
        room.add_door(wall)
    assert_eq(room.doors, set(Maze.Wall.WALLS))

    room.remove_door(Maze.Wall.RIGHT)
    assert all(room.has_door(wall) or wall == Maze.Wall.RIGHT
            for wall in Maze.Wall.WALLS), \
        'Removing right door did not have the expected effect (doors = %d)' % (
            room.doors)


@test
def Maze_Room_door_operators():
    """Tests that the operator overloads work"""
    room = Maze.Room()

    assert all(not wall in room and not room[wall]
            for wall in Maze.Wall.WALLS), \
        'Not all walls were empty when Room was created'

    room[Maze.Wall.LEFT] = True
    assert all(not wall in room and not room[wall] or wall == Maze.Wall.LEFT
            for wall in Maze.Wall.WALLS), \
        'Adding left door did not have the expected effect (doors = %d)' % (
            room.doors)

    for wall in Maze.Wall.WALLS:
        room += wall
    assert_eq(room.doors, set(Maze.Wall.WALLS))

    room -= Maze.Wall.RIGHT
    assert all(wall in room and room[wall] or wall == Maze.Wall.RIGHT
            for wall in Maze.Wall.WALLS), \
        'Removing right door did not have the expected effect (doors = %d)' % (
            room.doors)


@test
def Maze_Room_bool():
    """Tests that truth testing with Maze.Room works"""
    room = Maze.Room()

    assert not room, \
        'An empty room tested True'

    for wall in Maze.Wall.WALLS:
        room += wall
        assert room, \
            'A non-empty room tested False'


@test
def Maze_width_and_height():
    """Tests that the width and height properties are correct"""
    maze1 = Maze(10, 20)
    assert_eq(maze1.width, 10)
    assert_eq(maze1.height, 20)

    maze2 = Maze(200, 100)
    assert_eq(maze2.width, 200)
    assert_eq(maze2.height, 100)


@test
def Maze_room_positions():
    maze = Maze(3, 2)

    assert_eq(
        set(maze.room_positions),
        set((
            (0, 0), (1, 0), (2, 0),
            (0, 1), (1, 1), (2, 1))))


@test
def Maze_iter():
    """Tests that for room_pos in maze: works"""
    maze = Maze(10, 20)

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
def Maze_index_tuple():
    """Tests that indexing Maze with a tuple yields a Room"""
    maze = Maze(10, 20)

    assert isinstance(maze[3, 4], maze.Room), \
        'Maze[x, y] did not yield a Room'


@test
def Maze_index_tuple():
    """Tests that assigning to Maze[(x1, y1):(x2, y2)] works"""
    maze = Maze(10, 20)

    room1 = maze[3, 4]
    room2 = maze[4, 4]

    assert not maze.Wall.RIGHT in room1, \
        'Right door of room was not initially missing'
    assert not maze.Wall.LEFT in room2, \
        'Left door of room was not initially missing'

    maze[(3, 4):(4, 4)] = True

    assert maze.Wall.RIGHT in room1, \
        'Maze[(x1, y1):(x2, y2)] = True did not open the left door'
    assert maze.Wall.LEFT in room2, \
        'Maze[(x1, y1):(x2, y2)] = True did not open the right door'

    maze[(3, 4):(4, 4)] = False

    assert not maze.Wall.RIGHT in room1, \
        'Maze[(x1, y1):(x2, y2)] = False did not close the left door'
    assert not maze.Wall.LEFT in room2, \
        'Maze[(x1, y1):(x2, y2)] = False did not close the right door'

    try:
        maze[(-1, 0):(0, 0)] = True
        assert False, \
            'Maze.add_door did not raise IndexError for rooms outside of maze'
    except IndexError:
        pass


@test
def Maze_adjacent():
    maze = Maze(10, 20)

    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            adjacent1 = maze.adjacent((4, 4), (4 + x, 4 + y))
            adjacent2 = abs(x) + abs(y) == 1
            assert adjacent1 == adjacent2, \
                '(4, 4) %s be adjacent to (%d, %d)' % (
                    'should' if adjacent2 else 'should not',
                    4 + x,
                    4 + y)


@test
def Maze_contains():
    """Tests that room_pos in maze works"""
    maze = Maze(10, 20)

    for x in xrange(-5, maze.width + 5):
        for y in xrange(-5, maze.height + 5):
            expected = x >= 0 and x < maze.width and y >= 0 and y < maze.height
            actual = (x, y) in maze
            assert expected == actual, \
                '(%d, %d) in maze was incorrect (was %s)' % (x, y, actual)


@test
def Maze_add_door():
    maze = Maze(10, 20)

    room1 = maze[3, 4]
    room2 = maze[4, 4]

    assert not maze.Wall.RIGHT in room1, \
        'Right door of room was not initially missing'
    assert not maze.Wall.LEFT in room2, \
        'Left door of room was not initially missing'

    maze.add_door((3, 4), (4, 4))

    assert maze.Wall.RIGHT in room1, \
        'Maze.add_door did not open the left door'
    assert maze.Wall.LEFT in room2, \
        'Maze.add_door did not open the right door'

    maze.add_door((0, 0), (-1, 0))

    try:
        maze.add_door((0, 0), (2, 0))
        assert False, \
            'Maze.add_door did not raise IndexError for non-connected rooms'
    except ValueError:
        pass

    try:
        maze.add_door((-1, 0), (0, 0))
        assert False, \
            'Maze.add_door did not raise IndexError for rooms outside of maze'
    except IndexError:
        pass


@test
def Maze_remove_door():
    maze = Maze(10, 20)

    room1 = maze[3, 4]
    room2 = maze[4, 4]

    maze.add_door((3, 4), (4, 4))

    maze.remove_door((3, 4), (4, 4))

    assert not maze.Wall.RIGHT in room1, \
        'Maze.remove_door did not close the left door'
    assert not maze.Wall.LEFT in room2, \
        'Maze.remove_door did not close the right door'

    maze.remove_door((0, 0), (-1, 0))

    try:
        maze.remove_door((0, 0), (2, 0))
        assert False, \
            'Maze.remove_door did not raise IndexError for non-connected rooms'
    except ValueError:
        pass

    try:
        maze.remove_door((-1, 0), (0, 0))
        assert False, \
            'Maze.remove_door did not raise IndexError for rooms outside of ' \
                'maze'
    except IndexError:
        pass


@test
def Maze_connected():
    maze = Maze(10, 20)

    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            connected1 = maze.connected((4, 4), (4 + x, 4 + y))
            connected2 = False
            assert connected1 == connected2, \
                '(4, 4) %s be connected to (%d, %d)' % (
                    'should' if adjacent2 else 'should not',
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
                    'should' if adjacent2 else 'should not',
                    4 + x,
                    4 + y)


@test
def Maze_walk_from():
    maze = Maze(10, 20)

    assert_eq(maze.walk_from((0, 0), maze.Wall.RIGHT), (1, 0))
    assert_eq(maze.walk_from((1, 0), maze.Wall.LEFT), (0, 0))
    assert_eq(maze.walk_from((0, 1), maze.Wall.DOWN), (0, 0))
    assert_eq(maze.walk_from((0, 0), maze.Wall.UP), (0, 1))
    assert_eq(maze.walk_from((-1, 0), maze.Wall.RIGHT), (0, 0))

    try:
        maze.walk_from((-2, 0), maze.Wall.RIGHT)
        assert False, \
            'Walking from an invalid room did not raise IndexError'
    except IndexError:
        pass

    try:
        maze.walk_from((0, 0), maze.Wall.RIGHT, True)
        assert False, \
            'Walking through a wall without door did not raise ValueError'
    except ValueError:
        pass

    try:
        maze.walk_from((-1, 0), maze.Wall.RIGHT, True)
        assert False, \
            'Walking through a wall without door did not raise ValueError'
    except ValueError:
        pass


@test
def Maze_walk():
    maze = Maze(10, 20)

    assert_eq(maze.walk(maze.Wall((0, 0), maze.Wall.RIGHT)), (1, 0))
    assert_eq(maze.walk(maze.Wall((1, 0), maze.Wall.LEFT)), (0, 0))
    assert_eq(maze.walk(maze.Wall((0, 1), maze.Wall.DOWN)), (0, 0))
    assert_eq(maze.walk(maze.Wall((0, 0), maze.Wall.UP)), (0, 1))
    assert_eq(maze.walk(maze.Wall((-1, 0), maze.Wall.RIGHT)), (0, 0))

    try:
        maze.walk(maze.Wall((-2, 0), maze.Wall.RIGHT))
        assert False, \
            'Walking from an invalid room did not raise IndexError'
    except IndexError:
        pass

    try:
        maze.walk(maze.Wall((0, 0), maze.Wall.RIGHT), True)
        assert False, \
            'Walking through a wall without door did not raise ValueError'
    except ValueError:
        pass

    try:
        maze.walk(maze.Wall((-1, 0), maze.Wall.RIGHT), True)
        assert False, \
            'Walking through a wall without door did not raise ValueError'
    except ValueError:
        pass


@test
def Maze_doors():
    maze = Maze(10, 20)

    assert_eq(
        list(maze.doors((1, 1))),
        [])

    doors = []

    for w in maze.Wall.WALLS:
        wall = maze.Wall((1, 1), w)
        doors.append(wall)
        maze.add_door((1, 1), (1 + wall.direction[0], 1 + wall.direction[1]))
        assert_eq(
            sorted(list(maze.doors((1, 1)))),
            sorted(doors))


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
def Maze_walls():
    maze = Maze(10, 20)

    assert_eq(
        sorted(list(maze.walls((1, 1)))),
        sorted([maze.Wall((1, 1), w) for w in maze.Wall.WALLS]))

@test
def Maze_walk_path():
    """Tests that walking from one room to the same room always works"""
    maze = Maze(10, 20)

    assert_eq(
        list(maze.walk_path((2, 2), (2, 2))),
        [(2, 2)])


@test
def Maze_walk_path():
    """Tests that walking from a room outside of the maze raises ValueError"""
    maze = Maze(10, 20)

    try:
        list(maze.walk_path((-1, -1), (0, 0)))
        assert False, \
            'Managed to walk from (-1, -1)'
    except ValueError:
        pass


@test
def Maze_walk_path():
    """Tests that walking between non-connected rooms raises ValueError"""
    maze = Maze(10, 20)

    try:
        list(maze.walk_path((0, 0), (2, 0)))
        assert False, \
            'Managed to walk between non-connected rooms'
    except ValueError:
        pass


@test
def Maze_walk_path():
    """Tests that walking between adjacent rooms works as expected"""
    maze = Maze(10, 20)

    maze[(0, 0):(1, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (1, 0))),
        [(0, 0), (1, 0)])


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
def Maze_slice():
    """Tests that reading a slice of a maze yields the path between the two
    rooms"""
    maze = Maze(10, 20)

    maze[(0, 0):(0, 1)] = True
    maze[(0, 1):(1, 1)] = True
    maze[(1, 1):(2, 1)] = True
    maze[(2, 1):(2, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (2, 0))),
        list(maze[(0, 0):(2, 0)]))

    maze[(0, 0):(1, 0)] = True
    maze[(1, 0):(2, 0)] = True

    assert_eq(
        list(maze.walk_path((0, 0), (2, 0))),
        list(maze[(0, 0):(2, 0)]))


@test
def Maze_with_randomized_prim():
    """Tests that randomized_prim.initialize creates a valid maze"""
    maze = Maze(10, 20)

    def rand(m):
        return random.randint(0, m - 1)

    randomized_prim.initialize(maze, rand)

    for x in xrange(0, maze.width):
        for y in xrange(0, maze.height):
            assert len(list(maze[(0, 0):(x, y)])) > 0, \
                'Could not walk from (%d, %d) to (0, 0)' % (x, y)
