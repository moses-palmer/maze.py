def initialize(maze, randomizer):
    """
    A function that initialises a maze with the randomised prim algorithm.

    See http://en.wikipedia.org/wiki/Maze_generation_algorithm

    @param maze
        The maze to initialise.
    @param randomizer
        The function used as a source of randomness. It will be called with an
        argument describing the maximum value to return. It may return any
        integers between 0 and the non-inclusive maximum value.
    """
    # Start with a random room and add all its walls except those on the edge
    start_x, start_y = randomizer(maze.width), randomizer(maze.height)
    walls = [wall for wall in maze.walls((start_x, start_y))
        if not maze.edge(wall)]

    while walls:
        # Select a random wall
        index = randomizer(len(walls))
        wall = walls.pop(index)

        # Get the room behind the wall
        next_room_pos = maze.walk(wall)

        # Is this the first time we visit this room?
        if not maze[next_room_pos]:
            # Add a door to the wall
            maze.set_door(wall.room_pos, wall, True)

            # Add all walls of the new room except those on the edge and those
            # leading to rooms already visited
            walls.extend(w for w in maze.walls(next_room_pos)
                if not maze.edge(w) and not maze[maze.walk(w)])

