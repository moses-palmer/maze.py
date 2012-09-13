class Wall(object):
    """
    A reference to the wall of a room.

    A wall has an index and a direction.
      * The index is its position in the list (LEFT, UP, RIGHT, DOWN).
      * The direction is a direction vector for the wall; up and right are
        positive directions.
    """

    # Define the walls; this will also add the class variables mapping wall name
    # to its value
    DIRECTIONS = []
    NAMES = []
    WALLS = []
    for i, (name, hdir, vdir) in enumerate((
            ('LEFT', -1, 0),
            ('UP', 0, 1),
            ('RIGHT', 1, 0),
            ('DOWN', 0, -1))):
        locals()[name] = i
        DIRECTIONS.append((hdir, vdir))
        NAMES.append(name.lower())
        WALLS.append(i)

    def __init__(self, room_pos, wall):
        self.room_pos = room_pos
        self.wall = wall

    @classmethod
    def get_opposite(self, wall_index):
        """
        Returns the opposite wall.

        @param wall_index
            The index of the wall for which to find the opposite.
        @return the index of the opposite wall
        """
        return (wall_index + len(self.WALLS) / 2) % len(self.WALLS)

    @classmethod
    def get_direction(self, wall_index):
        """
        Returns a direction vector to move in when going through the wall.

        @param wall_index
            The index of the wall.
        @return a direction vector though the wall
        @raise IndexError if wall_index is invalid
        """
        return self.DIRECTIONS[wall_index]

    @classmethod
    def get_wall(self, direction):
        """
        Returns the index of the wall in the given direction.

        @param direction
            A direction vector. Its length does not matter; only the direction
            is used.
        @return the index of the wall in the specified direction
        @raise ValueError if the wall cannot be determined by the vector
        """
        return self.DIRECTIONS.index((
            (0 if direction[0] == 0 else
                1 if direction[0] > 0 else
                    -1),
            (0 if direction[1] == 0 else
                1 if direction[1] > 0 else
                    -1)))

    @classmethod
    def get_walls(self, room_pos):
        """
        Generates all walls of a room.

        @param room_pos
            The room coordinates.
        """
        for wall in self.WALLS:
            yield self(room_pos, wall)


class Room(object):
    """
    A room is a part of the maze.

    A room has all walls defined in Wall, and a concept of doors on the walls.
    """

    def __init__(self):
        """
        Creates a new room.
        """
        self.doors = set()


class Maze(object):
    """
    A maze is a grid of rooms.
    """

    def __init__(self, width, height):
        """
        Creates a maze with no open doors.

        @param width
            The width of the maze.
        @param height
            The height of the maze.
        """
        self.rooms = [[Room() for x in xrange(width)] for y in xrange(height)]

    @property
    def height(self):
        """The height of the maze."""
        return len(self.rooms)

    @property
    def width(self):
        """The width of the maze."""
        return len(self.rooms[0])

