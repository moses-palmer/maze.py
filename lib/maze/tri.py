import math

from . import BaseWall, BaseMaze

class TriWall(BaseMaze.Wall):
    # Define the walls; this will also add the class variables
    # mapping wall name to its value
    _ANGLES = []
    _DIRECTIONS = []
    NAMES = []
    WALLS = []

    __slots__ = tuple()

    start_angle = math.pi / 2 + 2 * math.pi / 3
    data = (
        ('DIAGONAL_1', (-1, 0), (1, 0)),
        ('DIAGONAL_2', (1, 0), (-1, 0)),
        ('HORIZONTAL', (0, -1), (0, 1)))
    for i, (name, dir1, dir2) in enumerate(data):
        locals()[name] = i
        next_angle = _ANGLES[-1][0] - 2 * math.pi / len(data) \
            if _ANGLES else start_angle

        while next_angle < 0.0:
            next_angle += 2 * math.pi
        alt_angle = next_angle - math.pi
        while alt_angle < 0.0:
            alt_angle += 2 * math.pi
        _ANGLES.append((next_angle, alt_angle))
        _DIRECTIONS.append((dir1, dir2))
        NAMES.append(name.lower())
        WALLS.append(i)

    @classmethod
    def from_direction(self, room_pos, direction):
        """
        @see Maze.Wall.from_direction
        """
        alt = (room_pos[0] + room_pos[1]) % 2
        for i, dirs in enumerate(self._DIRECTIONS):
            if direction == dirs[alt]:
                return self(room_pos, i)

        raise ValueError('Invalid direction for %s: %s' % (
            str(room_pos), str(direction)))

    def _get_opposite_index(self):
        """
        There is no opposite wall in a triangular room.

        @raise NotImplementedError
        """
        raise NotImplementedError()

    def _get_direction(self):
        """
        @see Maze.Wall._get_direction
        """
        alt = (self.room_pos[0] + self.room_pos[1]) % 2
        return self._DIRECTIONS[self.wall][alt]

class TriMaze(BaseMaze):
    """
    This is a maze with triangular rooms.
    """
    Wall = TriWall
