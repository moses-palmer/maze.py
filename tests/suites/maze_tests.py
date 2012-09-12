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
def Maze_width_and_height():
    """Tests that the width and height properties are correct"""
    maze1 = Maze(10, 20)
    assert_eq(maze1.width, 10)
    assert_eq(maze1.height, 20)

    maze2 = Maze(200, 100)
    assert_eq(maze2.width, 200)
    assert_eq(maze2.height, 100)

