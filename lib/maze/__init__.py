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

