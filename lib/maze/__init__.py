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

    In addition to the methods defined for Room, the following constructs are
    allowed:
        if wall in room: => if wall.has_door(wall):
        if room[Wall.LEFT]: => if room.has_door(wall):
        room[Wall.LEFT] = True => room.set_door(Wall.LEFT, True)
        room += Wall.LEFT => room.add_door(Wall.LEFT)
        room -= Wall.LEFT => room_remove_door(Wall.LEFT)
    """

    def __contains__(self, wall_index):
        return self.has_door(wall_index)

    def __getitem__(self, wall_index):
        return self.has_door(wall_index)

    def __setitem__(self, wall_index, has_door):
        self.set_door(wall_index, has_door)

    def __iadd__(self, wall_index):
        self.add_door(wall_index)
        return self

    def __isub__(self, wall_index):
        self.remove_door(wall_index)
        return self

    def __init__(self):
        """
        Creates a new room.
        """
        self.doors = set()

    def has_door(self, wall_index):
        """
        Returns whether a wall has a door.

        @param wall_index
            The wall to check.
        @return whether the wall has a door
        @raise IndexError if wall is not a valid wall
        """
        return wall_index in self.doors

    def add_door(self, wall_index):
        """
        Adds a door.

        @param wall_index
            The wall to which to add a door.
        @raise IndexError if wall_index is not a valid wall
        """
        self.doors.add(wall_index)

    def remove_door(self, wall_index):
        """
        Removes a door.

        @param wall_index
            The wall from which to remove a door.
        @raise IndexError if wall_index is not a valid wall
        """
        self.doors.discard(wall_index)

    def set_door(self, wall_index, has_door):
        """
        Adds or removes a door depending on has_door.

        @param wall_index
            The wall to modify.
        @param has_door
            Whether to add or remove the door.
        @raise IndexError if wall_index is not a valid wall
        """
        if has_door:
            self.add_door(wall_index)
        else:
            self.remove_door(wall_index)


class Maze(object):
    """
    A maze is a grid of rooms.

    In addition to the methods defined for Room, the following constructs are
    allowed:
        maze[room_pos] => maze.rooms[room_pos[1]][room_pos[0]]
        if room_pos in maze: => if room_pos[0] >= 0 and room_pos[1] >= 0 \
            and room_pos[0] < maze.width and room_pos[1] < maze.height
    """

    def __getitem__(self, room_pos):
        if isinstance(room_pos, tuple) and len(room_pos) == 2:
            # A request for a specific room
            room_x, room_y = room_pos
            return self.rooms[room_y][room_x]

        raise TypeError()

    def __contains__(self, room_pos):
        return room_pos[0] >= 0 and room_pos[0] < self.width \
            and room_pos[1] >= 0 and room_pos[1] < self.height

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

    def adjacent(self, room1_pos, room2_pos):
        """
        Returns whether two rooms are adjacent.

        The rooms are adjacent if the room at room1_pos has a wall that leads to
        the room at room2_pos.

        @param room1_pos, room2_pos
            The coordinates of the rooms to check.
        @return whether there is a wall between the two rooms
        """
        return any((room1_pos[0] + d[0], room1_pos[1] + d[1]) == room2_pos
            for d in Wall.DIRECTIONS)
