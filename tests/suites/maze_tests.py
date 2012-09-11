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
def Maze_width_and_height():
    """Tests that the width and height properties are correct"""
    maze1 = Maze(10, 20)
    assert_eq(maze1.width, 10)
    assert_eq(maze1.height, 20)

    maze2 = Maze(200, 100)
    assert_eq(maze2.width, 200)
    assert_eq(maze2.height, 100)

