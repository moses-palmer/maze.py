import math

from . import BaseWall, BaseMaze

class QuadWall(BaseWall):
    # The angles for each corner
    _ANGLES = []

    # The directions for each wall
    _DIRECTIONS = []

    # The names of the walls
    NAMES = []

    # The list of walls; this is the list [0, 1, 2... N]
    WALLS = []

    # The scale factor when converting maze coordinates to physical coordinates
    MULTIPLICATOR = 2.0 / math.sqrt(2.0)

    __slots__ = tuple()

    start_angle = (5 * math.pi) / 4
    data = (
        ('LEFT', (-1, 0)),
        ('UP', (0, 1)),
        ('RIGHT', (1, 0)),
        ('DOWN', (0, -1)))
    for i, (name, dir1) in enumerate(data):
        locals()[name] = i

        next_angle = _ANGLES[-1] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle
        while next_angle < 0.0:
            next_angle += 2 * math.pi
        _ANGLES.append(next_angle)

        _DIRECTIONS.append(dir1)

        NAMES.append(name.lower())
        WALLS.append(i)

class Maze(BaseMaze):
    """
    This is a maze with square rooms.

    This is the traditional maze. Maze coordinates correspond to physical
    coordinates after a simple scale operation.
    """
    Wall = QuadWall

    def get_center(self, room_pos):
        """
        @see Maze.get_center
        """
        return (
            (room_pos[0] + 0.5) * self.Wall.MULTIPLICATOR,
            (room_pos[1] + 0.5) * self.Wall.MULTIPLICATOR)
