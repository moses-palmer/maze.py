import math

from . import BaseWall, BaseMaze

class QuadWall(BaseWall):
    # Define the walls; this will also add the class variables
    # mapping wall name to its value
    _ANGLES = []
    _DIRECTIONS = []
    NAMES = []
    WALLS = []

    __slots__ = tuple()

    start_angle = (5 * math.pi) / 4
    data = (
        ('LEFT', -1, 0),
        ('UP', 0, 1),
        ('RIGHT', 1, 0),
        ('DOWN', 0, -1))
    for i, (name, hdir, vdir) in enumerate(data):
        locals()[name] = i
        next_angle = _ANGLES[-1] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle

        while next_angle < 0.0:
            next_angle += 2 * math.pi
        _ANGLES.append(next_angle)
        _DIRECTIONS.append((hdir, vdir))
        NAMES.append(name.lower())
        WALLS.append(i)

class Maze(BaseMaze):
    """
    This is a maze with square rooms.
    """
    Wall = QuadWall
