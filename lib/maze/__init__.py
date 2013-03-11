import bisect
import math
import sys


class BaseWall(object):
    """
    A reference to the wall of a room.

    A wall has an index, a direction, a span and a position.
      * The index is its position in the list of walls. This corresponds to its
        symbolic name.
      * The direction is a direction vector for the wall; up and right are
        positive directions. The direction is the movement vector in the maze
        room matrix and not necessarily an actual physical direction.
      * The span is the physical start and end angle of the wall.
      * The position is the coordinates of the room to which the wall belongs in
        the maze room matrix.

    Furthermore, walls know their back and opposite.
      * The back is the same wall in the room on the other side of a wall. A
        wall will compare equally with its back.
      * The opposite is the wall opposing a wall in the same room. Depending on
        the layout of a room, there may be no opposite wall. Triangular mazes do
        not have opposite walls.

    Walls have factory methods.
      * from_direction will create a wall when the room and the direction is
        known. The direction must be the direction vector of the room.
      * from_room_pos will create all walls for a room.
      * from_corner will create all walls that meet in a corner.
    """

    __slots__ = (
        'wall',
        'room_pos')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.wall == other.wall and self.room_pos == other.room_pos:
            return True
        if self.wall == other._get_back_index() \
                and all(s + d == o for s, d, o in zip(
                    self.room_pos,
                    self.direction,
                    other.room_pos)):
            return True

    def __int__(self):
        return self.wall

    def __str__(self):
        return self.NAMES[self.wall] + '@' + str(self.room_pos)
    __repr__ = __str__

    def __init__(self, room_pos, wall):
        self.room_pos = room_pos
        self.wall = wall

    @classmethod
    def from_direction(self, room_pos, direction):
        """
        Creates a new wall from a direction.

        @param room_pos
            The position of the room.
        @param direction
            The direction of the wall.
        @return a new Wall
        @raise ValueError if the direction is invalid
        """
        return self(room_pos, self._DIRECTIONS.index(direction))

    @classmethod
    def from_room_pos(self, room_pos):
        """
        Generates all walls of a room.

        @param room_pos
            The room coordinates.
        """
        for wall in self.WALLS:
            yield self(room_pos, wall)

    @classmethod
    def from_corner(self, room_pos, wall_index):
        """
        Generates all walls that meet in the corner where the wall has its
        start span.

        The walls are generated counter-clockwise, starting with the wall
        described by the parameters.

        @param room_pos
            The position of the room.
        @param wall_index
            The index of the wall.
        """
        wall = start_wall = self(room_pos, wall_index)

        while True:
            yield wall

            back = wall.back
            next = self(back.room_pos, (back.wall + 1) % len(self.WALLS))
            if next == start_wall:
                break

            wall = next

    def _get_opposite_index(self):
        """
        Returns the index of the opposite wall.

        The opposite wall is the wall in the same room with a span opposing
        this wall.

        @return the opposite wall
        """
        return (self.wall + len(self.WALLS) // 2) % len(self.WALLS)

    def _get_back_index(self):
        """
        Returns the index of the wall on the back of this wall.

        @return the back wall
        """
        return self._get_opposite_index()

    def _get_opposite(self):
        """
        Returns the opposite wall.

        The opposite wall is the wall in the same room with a span opposing
        this wall.

        @return the opposite wall
        @raise ValueError if no opposite room exists
        """
        return self.__class__(self.room_pos, self._get_opposite_index())

    def _get_direction(self):
        """
        Returns a direction vector to move in when going through the wall.

        @return a direction vector though the wall
        """
        return self._DIRECTIONS[self.wall]

    def _get_span(self):
        """
        Returns the span of the wall, expressed as degrees.

        The start of the wall is defined as the most counter-clockwise edge
        of the wall and the end as the start of the next wall.

        The origin of the coordinate system is the centre of the room; thus
        points to the left of the centre of room will have negative
        x-coordinates and points below the center of the room negative
        y-coordinates.

        @return the span expressed as (start_angle, end_angle)
        """
        start = self._ANGLES[self.wall]
        end = self._ANGLES[(self.wall + 1) % len(self._ANGLES)]

        return (start, end)

    @property
    def opposite(self):
        """The opposite wall in the same room."""
        return self._get_opposite()

    @property
    def direction(self):
        """The direction vector to move in when going through the wall."""
        return self._get_direction()

    @property
    def back(self):
        """The wall on the other side of the wall."""
        direction = self._get_direction()
        return self.__class__(
            (
                self.room_pos[0] + direction[0],
                self.room_pos[1] + direction[1]),
            self._get_back_index())

    @property
    def corner_walls(self):
        """All walls in the corner that contains the start span of this
        wall."""
        return self.__class__.from_corner(self.room_pos, self.wall)

    @property
    def span(self):
        """The span of this wall"""
        return self._get_span()


class Room(object):
    """
    A room is a part of the maze.

    A room has a set of walls. Walls in the set are considered to have doors.

    In addition to the methods defined, the following constructs are allowed:
        if room: => if bool(room.doors):
        if wall in room: => if wall.has_door(wall):
        if room[Wall.LEFT]: => if room.has_door(wall):
        room[Wall.LEFT] = bool => room.set_door(Wall.LEFT, bool)
        room += Wall.LEFT => room.add_door(Wall.LEFT)
        room -= Wall.LEFT => room_remove_door(Wall.LEFT)
    """

    def __bool__(self):
        return bool(self.doors)
    __nonzero__ = __bool__

    def __eq__(self, other):
        return other.doors == self.doors

    def __contains__(self, wall_index):
        return self.has_door(int(wall_index))

    def __getitem__(self, wall_index):
        return self.has_door(int(wall_index))

    def __setitem__(self, wall_index, has_door):
        self.set_door(int(wall_index), has_door)

    def __iadd__(self, wall_index):
        self.add_door(int(wall_index))
        return self

    def __isub__(self, wall_index):
        self.remove_door(int(wall_index))
        return self

    def __init__(self):
        """
        Creates a new room with no doors.
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
        return int(wall_index) in self.doors

    def add_door(self, wall_index):
        """
        Adds a door.

        @param wall_index
            The wall to which to add a door.
        @raise IndexError if wall_index is not a valid wall
        """
        self.doors.add(int(wall_index))

    def remove_door(self, wall_index):
        """
        Removes a door.

        @param wall_index
            The wall from which to remove a door.
        @raise IndexError if wall_index is not a valid wall
        """
        self.doors.discard(int(wall_index))

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
            self.add_door(int(wall_index))
        else:
            self.remove_door(int(wall_index))


class BaseMaze(object):
    """
    A maze is a grid of rooms.

    In addition to the methods defined, the following constructs are allowed:
        maze[room_pos] => maze.rooms[room_pos[1]][room_pos[0]]
        if room_pos in maze: => if room_pos[0] >= 0 and room_pos[1] >= 0 \
            and room_pos[0] < maze.width and room_pos[1] < maze.height
        maze[room_pos1:room_pos2] = True => maze.add_door(room_pos1, room_pos2)
        maze[room_pos1:room_pos2] = True =>
            maze.remove_door(room_pos1, room_pos2)
        maze[room_pos1:room_pos2] => maze.walk_path(room_pos1, room_pos2)
        for room_pos in maze: => for room_pos in \
            (rp for rp in maze.room_positions if maze[rp]):
    """
    Room = Room
    Wall = BaseWall

    def __getitem__(self, room_pos):
        if isinstance(room_pos, tuple) and len(room_pos) == 2:
            # A request for a specific room
            room_x, room_y = room_pos
            return self.rooms[room_y][room_x]

        if isinstance(room_pos, slice):
            # A request for the path between two rooms
            if not room_pos.step is None:
                raise ValueError()
            from_pos, to_pos = room_pos.start, room_pos.stop
            return self.walk_path(from_pos, to_pos)

        raise TypeError()

    def __setitem__(self, room_pos, value):
        if isinstance(room_pos, slice):
            # A request to set the wall between two rooms
            from_pos, to_pos = room_pos.start, room_pos.stop
            if value:
                self.add_door(from_pos, to_pos)
            else:
                self.remove_door(from_pos, to_pos)
            return

        raise TypeError()

    def __contains__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            x, y = item
            return x >= 0 and x < self.width and y >= 0 and y < self.height

        if isinstance(item, self.Wall):
            x, y = item.room_pos
            return x >= 0 and x < self.width and y >= 0 and y < self.height

    def __iter__(self):
        return (room_pos for room_pos in self.room_positions if self[room_pos])

    def __init__(self, width, height):
        """
        Creates a maze with no open doors.

        @param width
            The width of the maze.
        @param height
            The height of the maze.
        """
        self.rooms = [[self.__class__.Room() for x in range(width)]
            for y in range(height)]
        self.width = width
        self.height = height

    @property
    def room_positions(self):
        """A generator that yields the positions of all rooms"""
        for x in range(0, self.width):
            for y in range(0, self.height):
                yield (x, y)

    @property
    def edge_walls(self):
        """A generator that yields all walls on the edge of the maze; the order
        is undefined"""
        for y in range(0, self.height):
            row = (0,) if self.width == 1 \
                else (0, self.width - 1) if y == 0 or y == self.height - 1 \
                else range(0, self.width)
            for x in row:
                for wall in self.walls((x, y)):
                    if self.edge(wall):
                        yield wall

    def add_door(self, from_pos, to_pos):
        """
        Adds a door between two rooms.

        @param from_pos, to_pos
            The coordinates of the rooms.
        @raise IndexError if a room lies outside of the maze
        @raise ValueError if the rooms are not adjacent
        """
        direction = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
        wall = self.__class__.Wall.from_direction(from_pos, direction)

        self.set_door(from_pos, wall, True)

    def remove_door(self, from_pos, to_pos):
        """
        Removes a door between two rooms.

        @param from_pos, to_pos
            The coordinates of the rooms.
        @raise IndexError if a room lies outside of the maze
        @raise ValueError if the rooms are not adjacent
        """
        direction = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
        wall = self.__class__.Wall.from_direction(from_pos, direction)

        return self.set_door(from_pos, wall, False)

    def set_door(self, room_pos, wall, has_door):
        """
        Adds or removes a door.

        @param room_pos
            The coordinates of the room.
        @param
            The wall to modify.
        @param has_door
            True to add the door and False to remove it.
        @raise IndexError if room_pos lies outside of the maze
        """
        if not room_pos in self:
            raise IndexError()

        # Get the coordinate of the other room
        if not isinstance(wall, self.Wall):
            wall = self.Wall(room_pos, int(wall))
        other_wall = wall.back
        to_pos = other_wall.room_pos

        self[room_pos][wall] = has_door

        if to_pos in self:
            self[to_pos][other_wall] = has_door

    def get_center(self, room_pos):
        """
        Returns the physical coordinates of the centre of a room.

        If lines are drawn on a circle with radius 1.0 centred on this point
        between the angles corresponding to the spans of the walls, the lines of
        adjacent rooms will cover each other.

        @param room_pos
            The position of the room.
        @return the coordinates of the room
        @raise IndexError if a room lies outside of the maze
        """
        raise NotImplementedError()

    def adjacent(self, room1_pos, room2_pos):
        """
        Returns whether two rooms are adjacent.

        The rooms are adjacent if the room at room1_pos has a wall that leads to
        the room at room2_pos.

        @param room1_pos, room2_pos
            The coordinates of the rooms to check.
        @return whether there is a wall between the two rooms
        """
        return any((room1_pos[0] + wall.direction[0],
                room1_pos[1] + wall.direction[1]) == room2_pos
            for wall in self.walls(room1_pos))

    def connected(self, room1_pos, room2_pos):
        """
        Returns whether two rooms are connected by a single wall containing a
        door.

        @param room1_pos, room2_pos
            The coordinates of the rooms to check.
        @return whether the two rooms are adjacent and have doors
        """
        # Make sure that they are adjacent
        if not self.adjacent(room1_pos, room2_pos):
            return False

        # Make sure the wall has a door
        try:
            direction = (
                room1_pos[0] - room2_pos[0],
                room1_pos[1] - room2_pos[1])
            wall_index = int(self.__class__.Wall.from_direction(
                room1_pos, direction))
            return wall_index in self[room1_pos]
        except ValueError:
            return False

    def edge(self, wall):
        """
        Returns whether a wall is on the edge of the maze.

        @param wall
            The wall.
        @return whether the wall is on the edge of the maze
        """
        return wall in self and not wall.back in self

    def walls(self, room_pos):
        """
        Generates all walls of a room.

        @param room_pos
            The coordinates of the room.
        @raise IndexError if a room lies outside of the maze
        """
        if room_pos in self:
            return self.__class__.Wall.from_room_pos(room_pos)
        else:
            raise IndexError("Room %s is not part of the maze" % str(room_pos))

    def doors(self, room_pos):
        """
        Generates all walls with doors.

        @param room_pos
            The coordinates of the room.
        @raise IndexError if a room lies outside of the maze
        """
        room = self[room_pos]

        for wall in self.__class__.Wall.WALLS:
            if wall in room:
                yield self.__class__.Wall(room_pos, wall)

    def walk_from(self, room_pos, wall, require_door = False):
        """
        Returns the coordinates of the room through the specified wall.

        The starting room, room_pos, may be outside of the maze if it is
        immediately on the edge and the movement is inside the maze.

        @param room_pos
            The room from which to walk.
        @param wall
            The wall to walk through.
        @param require_door
            Whether to require a door in the specified direction.
        @return the destination coordinates
        @raise ValueError if require_door is True and there is no door on the
            wall
        @raise IndexError if the destination room lies outside of the maze
        """
        wall = self.__class__.Wall(room_pos, int(wall))
        direction = wall.direction
        result = (room_pos[0] + direction[0], room_pos[1] + direction[1])

        if require_door:
            if not wall in self[room_pos]:
                raise ValueError('(%d, %d) is not inside the maze' % room_pos)

        if result in self:
            return result
        else:
            raise IndexError()

    def walk(self, wall, require_door = False):
        """
        Returns the coordinates of the room through the specified wall.

        @param wall
            The wall to walk through.
        @param require_door
            Whether to require a door in the specified direction.
        @return the destination coordinates
        @raise ValueError if require_door is True and there is no door on the
            wall
        @raise IndexError if the destination room lies outside of the maze
        """
        return self.walk_from(wall.room_pos, int(wall), require_door)

    def walk_path(self, from_pos, to_pos, visitor = lambda room_pos: None):
        """
        Generates all rooms on the shortest path between two rooms.

        @param from_pos
            The room in which to start. This room is included.
        @param to_pos
            The last room to visit.
        @param visitor
            A callback to call for every room encountered. This callback may
            raise StopIteration to cancel the walking.
        @raise ValueError if there is no path between the rooms
        """
        # Handle walking to the same room efficiently
        if from_pos == to_pos:
            visitor(from_pos)
            yield from_pos
            return

        # Swap from_pos and to pos to make reconstructing the path easier
        from_pos, to_pos = to_pos, from_pos

        def h(room_pos):
            """The heuristic for a room"""
            return sum((t - f)**2 for f, t in zip(room_pos, to_pos))

        # The rooms already evaluated
        closed_set = []

        # The rooms pending evaluation; this list is sorted on cost
        class infinity(object):
            def __cmp__(self, other):
                if isinstance(other, type(self)): return 0
                else: return 1
        open_set = [(infinity(), from_pos)]

        # The cost from from_pos to the room along the best known path
        g_score = {}
        g_score[from_pos] = 0

        # The estimated cost from from_pos to to_pos through the room
        f_score = {}
        f_score[from_pos] = h(from_pos)

        # The room from which we entered a room
        came_from = {}

        while open_set:
            # Get the node in open_set having the lowest f_score value
            cost, current = open_set.pop(0)

            # Visit the room first
            visitor(current)

            # Have we reached the goal?
            if current == to_pos:
                while current != from_pos:
                    yield current
                    current = came_from[current]
                yield from_pos
                return

            closed_set.append(current)
            for wall in self.doors(current):
                next = wall.back.room_pos

                # Ignore rooms already evaluated or rooms outside of the maze
                if next in closed_set or not next in self:
                    continue

                # The cost to get to this room is one more that the room from
                # which we came
                g = g_score[current] + 1

                # Is this a new room, or has the score improved since last?
                if not next in open_set or g < g_score[next]:
                    came_from[next] = current
                    g_score[next] = g
                    f = g + h(next)
                    f_score[next] = f

                    # Insert the next room while keeping open_set sorted
                    if not next in open_set:
                        bisect.insort(open_set, (f, next))

        raise ValueError()

