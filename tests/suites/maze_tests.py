from tests import *
from maze import *

@test
def Wall_fields():
    """Tests that Wall contains the expected fields"""
    walls = set()

    assert_eq(len(Wall.NAMES), 4)

    for a in (name.upper() for name in Wall.NAMES):
        assert hasattr(Wall, a), \
            'Wall.%s is undefined' % a

        w = getattr(Wall, a)
        assert not w in walls, \
            'Wall.%s has a previously set value' % a

        walls.add(w)

    assert_eq(len(Wall.WALLS), len(Wall.DIRECTIONS))
    assert_eq(len(Wall.DIRECTIONS), len(set(Wall.DIRECTIONS)))
    assert_eq(len(Wall.WALLS), len(Wall.NAMES))
    assert_eq(len(Wall.NAMES), len(set(Wall.NAMES)))


@test
def Wall_get_opposite():
    """Tests Wall.get_opposite"""
    assert_eq(Wall.get_opposite(Wall.LEFT), Wall.RIGHT)
    assert_eq(Wall.get_opposite(Wall.UP), Wall.DOWN)
    assert_eq(Wall.get_opposite(Wall.RIGHT), Wall.LEFT)
    assert_eq(Wall.get_opposite(Wall.DOWN), Wall.UP)


@test
def Wall_get_direction():
    """Tests Wall.get_direction"""
    assert_eq(Wall.get_direction(Wall.LEFT), (-1, 0))
    assert_eq(Wall.get_direction(Wall.UP), (0, 1))
    assert_eq(Wall.get_direction(Wall.RIGHT), (1, 0))
    assert_eq(Wall.get_direction(Wall.DOWN), (0, -1))


@test
def Wall_get_wall():
    """Tests Wall.get_wall"""
    assert_eq(Wall.get_wall((-1, 0)), Wall.LEFT)
    assert_eq(Wall.get_wall((-2, 0)), Wall.LEFT)
    assert_eq(Wall.get_wall((10, 0)), Wall.RIGHT)
    assert_eq(Wall.get_wall((20, 0)), Wall.RIGHT)

    assert_eq(Wall.get_wall((0, 1)), Wall.UP)
    assert_eq(Wall.get_wall((0, -10)), Wall.DOWN)

    try:
        Wall.get_wall((1, 1))
        assert False, \
            'Invalid direction did not raise ValueError'
    except ValueError:
        pass

    try:
        Wall.get_wall((0, 0))
        assert False, \
            'Invalid direction did not raise ValueError'
    except ValueError:
        pass


@test
def Wall_get_walls():
    """Tests Wall.get_wall"""
    walls = set()

    for wall in Wall.get_walls((10, 20)):
        assert_eq(wall.room_pos, (10, 20))

        if wall.wall in walls:
            assert False, \
                '%s was found twice' % Wall.NAMES[wall]
        walls.add(wall.wall)


@test
def Room_door_functions():
    """Tests that Room.add_door, remove_door and has_door work"""
    room = Room()

    assert all(not room.has_door(wall)
            for wall in Wall.WALLS), \
        'Not all walls were empty when Room was created'

    room.add_door(Wall.LEFT)
    assert all(not room.has_door(wall) or wall == Wall.LEFT
            for wall in Wall.WALLS), \
        'Adding left door did not have the expected effect (doors = %d)' % (
            room.doors)

    for wall in Wall.WALLS:
        room.add_door(wall)
    assert_eq(room.doors, set(Wall.WALLS))

    room.remove_door(Wall.RIGHT)
    assert all(room.has_door(wall) or wall == Wall.RIGHT
            for wall in Wall.WALLS), \
        'Removing right door did not have the expected effect (doors = %d)' % (
            room.doors)


@test
def Room_door_operators():
    """Tests that the operator overloads work"""
    room = Room()

    assert all(not wall in room and not room[wall]
            for wall in Wall.WALLS), \
        'Not all walls were empty when Room was created'

    room[Wall.LEFT] = True
    assert all(not wall in room and not room[wall] or wall == Wall.LEFT
            for wall in Wall.WALLS), \
        'Adding left door did not have the expected effect (doors = %d)' % (
            room.doors)

    for wall in Wall.WALLS:
        room += wall
    assert_eq(room.doors, set(Wall.WALLS))

    room -= Wall.RIGHT
    assert all(wall in room and room[wall] or wall == Wall.RIGHT
            for wall in Wall.WALLS), \
        'Removing right door did not have the expected effect (doors = %d)' % (
            room.doors)


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
def Maze_index_tuple():
    """Tests that indexing Maze with a tuple yields a Room"""
    maze = Maze(10, 20)

    assert isinstance(maze[3, 4], Room), \
        'Maze[x, y] did not yield a Room'


@test
def Maze_adjacent():
    """Tests that Maze.adjacent works"""
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
    """Tests that Maze.add_door works"""
    maze = Maze(10, 20)

    room1 = maze[3, 4]
    room2 = maze[4, 4]

    assert not Wall.RIGHT in room1, \
        'Right door of room was not initially missing'
    assert not Wall.LEFT in room2, \
        'Left door of room was not initially missing'

    maze.add_door((3, 4), (4, 4))

    assert Wall.RIGHT in room1, \
        'Maze.add_door did not open the left door'
    assert Wall.LEFT in room2, \
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
