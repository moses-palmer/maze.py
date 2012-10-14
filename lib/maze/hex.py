import math

from . import BaseWall, BaseMaze

class HexWall(BaseMaze.Wall):
    # Define the walls; this will also add the class variables
    # mapping wall name to its value
    _ANGLES = []
    _DIRECTIONS = []
    NAMES = []
    WALLS = []

    __slots__ = tuple()

    start_angle = math.pi / 2 + (2 * 2 * math.pi) / 6
    data = (
        ('LEFT', (-1, 0), None),
        ('UP_LEFT', (-1, 1), (0, 1)),
        ('UP_RIGHT', (0, 1), (1, 1)),
        ('RIGHT', (1, 0), None),
        ('DOWN_RIGHT', (0, -1), (1, -1)),
        ('DOWN_LEFT', (-1, -1), (0, -1)))
    for i, (name, dir1, dir2) in enumerate(data):
        locals()[name] = i
        next_angle = _ANGLES[-1] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle

        while next_angle < 0.0:
            next_angle += 2 * math.pi
        _ANGLES.append(next_angle)
        _DIRECTIONS.append((dir1, dir2))
        NAMES.append(name.lower())
        WALLS.append(i)

    VERTICAL_MULTIPLICATOR = 1.0 - 0.5 * math.sin(_ANGLES[1])

    @classmethod
    def from_direction(self, room_pos, direction):
        """
        @see Maze.Wall.from_direction
        """
        use_alt = room_pos[1] % 2 == 1
        for i, (dir1, dir2) in enumerate(self._DIRECTIONS):
            if direction == (dir1 if not use_alt or not dir2 else dir2):
                return self(room_pos, i)

        raise ValueError('Invalid direction for %s: %s' % (
            str(room_pos), str(direction)))

    def _get_direction(self):
        """
        @see Maze.Wall._get_direction
        """
        if (self.room_pos[1] % 2 == 1) and self._DIRECTIONS[self.wall][1]:
            return self._DIRECTIONS[self.wall][1]
        else:
            return self._DIRECTIONS[self.wall][0]

class HexMaze(BaseMaze):
    """
    This is a maze with hexagonal rooms.
    """
    Wall = HexWall

    def get_center(self, room_pos):
        """
        @see Maze.get_center
        """
        center_x = room_pos[0] + (1.0 if room_pos[1] % 2 == 1 else 0.5)
        center_y = self.Wall.VERTICAL_MULTIPLICATOR * room_pos[1] + 0.5
        return (center_x, center_y)
