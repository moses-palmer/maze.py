import math
import sys


class BaseMaze(object):
    """
    A maze is a grid of rooms.

    In addition to the methods defined for Room, the following constructs are
    allowed:
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

    class Wall(object):
        """
        A reference to the wall of a room.

        A wall has an index, a direction and a span.
          * The index is its position in the list (LEFT, UP, RIGHT, DOWN).
          * The direction is a direction vector for the wall; up and right are
            positive directions.
          * The span is the physical start and end angle of the wall.
        """

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            if self.wall == other.wall and self.room_pos == other.room_pos:
                return True
            if self.wall == other._get_opposite_index() \
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

        def _get_opposite_index(self):
            """
            Returns the index of the opposite wall.

            The opposite wall is the wall in the same room with a span opposing
            this wall.

            @return the opposite wall
            """
            return (self.wall + len(self.WALLS) / 2) % len(self.WALLS)

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

            The origin of the coordinate system is the center of the room; thus
            points to the left of the center of room will have negative
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
            return self.__class__(
                tuple(r + d
                    for r, d in zip(self.room_pos, self._get_direction())),
                self._get_opposite_index())

        @property
        def span(self):
            """The span of this wall"""
            return self._get_span()


    class Room(object):
        """
        A room is a part of the maze.

        A room has all walls defined in Wall, and a concept of doors on the
        walls.

        In addition to the methods defined for Room, the following constructs
        are allowed:
            if wall in room: => if wall.has_door(wall):
            if room[Wall.LEFT]: => if room.has_door(wall):
            room[Wall.LEFT] = True => room.set_door(Wall.LEFT, True)
            room += Wall.LEFT => room.add_door(Wall.LEFT)
            room -= Wall.LEFT => room_remove_door(Wall.LEFT)
        """

        def __bool__(self):
            return bool(self.doors)
        __nonzero__ = __bool__

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
            self._set_door(from_pos, to_pos, value)
            return

        raise TypeError()

    def __contains__(self, room_pos):
        return room_pos[0] >= 0 and room_pos[0] < self.width \
            and room_pos[1] >= 0 and room_pos[1] < self.height

    def __iter__(self):
        return (room_pos for room_pos in self.room_positions if self[room_pos])

    def _set_door(self, from_pos, to_pos, has_door):
        """
        Adds or removes a door between two rooms.

        @param from_pos, to_pos
            The coordinates of the rooms.
        @param has_door
            True to add the door and False to remove it.
        @raise IndexError if a room lies outside of the maze
        @raise ValueError if the rooms are not adjacent
        """
        if not from_pos in self and to_pos in self:
            raise IndexError()
        if not self.adjacent(from_pos, to_pos):
            raise ValueError('No wall between %s and %s' % (
                str(from_pos), str(to_pos)))

        direction = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
        wall = self.__class__.Wall.from_direction(from_pos, direction)

        from_room = self[from_pos]
        from_room[wall] = has_door

        if to_pos in self:
            to_room = self[to_pos]
            to_room[wall.opposite] = has_door

    def __init__(self, width, height):
        """
        Creates a maze with no open doors.

        @param width
            The width of the maze.
        @param height
            The height of the maze.
        """
        self.rooms = [[self.__class__.Room() for x in xrange(width)]
            for y in xrange(height)]

    @property
    def height(self):
        """The height of the maze."""
        return len(self.rooms)

    @property
    def width(self):
        """The width of the maze."""
        return len(self.rooms[0])

    @property
    def room_positions(self):
        """A generator that yields the positions of all rooms"""
        for x in xrange(0, self.width):
            for y in xrange(0, self.height):
                yield (x, y)

    def add_door(self, from_pos, to_pos):
        """
        Adds a door between two rooms.

        @param from_pos, to_pos
            The coordinates of the rooms.
        @raise IndexError if a room lies outside of the maze
        @raise ValueError if the rooms are not adjacent
        """
        self._set_door(from_pos, to_pos, True)

    def remove_door(self, from_pos, to_pos):
        """
        Removes a door between two rooms.

        @param from_pos, to_pos
            The coordinates of the rooms.
        @raise IndexError if a room lies outside of the maze
        @raise ValueError if the rooms are not adjacent
        """
        return self._set_door(from_pos, to_pos, False)

    def get_center(self, room_pos):
        """
        Returns the physical coordinates of the centre of a room.

        For a maze with square rooms, this will be (0.5, 0.5) for the room at
        (0, 0).

        @param room_pos
            The position of the room.
        @return the coordinates of the room
        @raise IndexError if a room lies outside of the maze
        """
        return tuple(d + 0.5 for d in room_pos)

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
        return wall.room_pos in self and not wall.back.room_pos in self

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
            Whether to require a door in the specified direction. If this
            parameter is True,
        @return the destination coordinates
        @raise ValueError if require_door is True and there is no door on the
            wall
        @raise IndexError if the destination room lies outside of the maze
        """
        wall = self.__class__.Wall(room_pos, int(wall))
        direction = wall.direction
        result = (room_pos[0] + direction[0], room_pos[1] + direction[1])

        if require_door:
            if not wall.opposite in self[result]:
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
            Whether to require a door in the specified direction. If this
            parameter is True,
        @return the destination coordinates
        @raise ValueError if require_door is True and there is no door on the
            wall
        @raise IndexError if the destination room lies outside of the maze
        """
        return self.walk_from(wall.room_pos, int(wall), require_door)

    def walk_path(self, from_pos, to_pos):
        """
        Generates all rooms on the shortest path between two rooms.

        @param from_pos
            The room in which to start. This room is included.
        @param to_pos
            The last room to visit.
        @raise ValueError if there is no path between the rooms
        """
        # Handle walking to the same room efficiently
        if from_pos == to_pos:
            yield from_pos
            return

        # Create the matrix of the walls we used to enter the room
        rooms = [[list((-1, sys.maxint)) for x in xrange(self.width)]
            for y in xrange(self.height)]
        def get_wall(room_pos):
            return rooms[room_pos[1]][room_pos[0]][0]
        def set_wall(room_pos, value):
            rooms[room_pos[1]][room_pos[0]][0] = value
        def get_distance(room_pos):
            return rooms[room_pos[1]][room_pos[0]][1]
        def set_distance(room_pos, value):
            rooms[room_pos[1]][room_pos[0]][1] = value

        # Perform a breadth-first search of the maze
        shortest = sys.maxint
        queue = [(0, to_pos)]
        while queue:
            (distance, room_pos) = queue.pop()

            # If we have walked further than a previously found solution, abort
            if distance + 1 > shortest:
                continue

            for wall in self.doors(room_pos):
                # Do not crash on doors leading out of the maze
                try:
                    next_pos = self.walk(wall)
                except IndexError:
                    continue

                # If the room has been visited along a shorter path before,
                # ignore it
                if get_distance(next_pos) <= distance:
                    continue

                # Update the matrix, since we found the shortest path to the
                # current room
                set_wall(next_pos, wall.opposite.wall)
                set_distance(next_pos, distance + 1)
                queue.append((distance + 1, next_pos))

                # Store the current shortest length so that we may ignore rooms
                # further from the starting point
                if next_pos == from_pos:
                    shortest = distance + 1

        # Make sure that we reached the starting room
        if rooms[from_pos[0]][from_pos[1]][0] == -1:
            raise ValueError()

        # Walk from the starting room in the directions found in the previous
        # step
        current = from_pos
        while current != to_pos:
            yield current
            current = self.walk_from(current, get_wall(current))
        yield to_pos


class Maze(BaseMaze):
    """
    This is a maze with square rooms.
    """
    class Wall(BaseMaze.Wall):
        # Define the walls; this will also add the class variables
        # mapping wall name to its value
        _ANGLES = []
        _DIRECTIONS = []
        NAMES = []
        WALLS = []

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


class HexMaze(BaseMaze):
    """
    This is a maze with hexagonal rooms.
    """
    class Wall(BaseMaze.Wall):
        # Define the walls; this will also add the class variables
        # mapping wall name to its value
        _ANGLES = []
        _DIRECTIONS = []
        NAMES = []
        WALLS = []

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

    def get_center(self, room_pos):
        """
        @see Maze.get_center
        """
        center_x = room_pos[0] + (1.0 if room_pos[1] % 2 == 1 else 0.5)
        center_y = self.Wall.VERTICAL_MULTIPLICATOR * room_pos[1] + 0.5
        return (center_x, center_y)
