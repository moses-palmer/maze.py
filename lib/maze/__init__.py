class Room(object):
    """
    A room is a part of the maze.
    """

    def __init__(self):
        """
        Creates a new room.
        """
        pass


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

