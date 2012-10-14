#!/usr/bin/env python

try:
    import cProfile as profile
except ImportError:
    print 'cProfile is not available, falling back on profile...'
    import profile
import os
import tempfile
from pstats import Stats

try:
    import maze
except ImportError:
    import sys

    # Use the in-tree maze library at ../lib/
    path_entry = os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        'lib')
    if not path_entry in sys.path:
        sys.path.append(path_entry)
        import maze
    else:
        raise

from maze.quad import Maze
from maze.hex import HexMaze
from maze.randomized_prim import initialize

RAND = 513
def rand(max):
    global RAND
    RAND += 1
    return RAND % max


# The list of profilers
PROFILERS = []

MAZE_SIZE = (200, 140)


def profiler(func):
    """
    Runs profiler tests on a function and prints statistics.

    The function must take as single parameter an instance of BaseMaze. It will
    be run for every maze type.
    """
    def runner():
        for maze_type in (Maze, HexMaze):
            # Create the maze and initialise it
            maze = maze_type(*getattr(func, 'maze_size', MAZE_SIZE))
            initializer = getattr(func, 'initializer', None)
            if initializer:
                print 'Running initialiser for %s for %s...' % (
                    func.__name__, maze_type.__name__)
                initializer(maze)

            # Create a temporary file, run the profiling and write the result to
            # the temporary file to be able to create a Stats object
            fd, filename = tempfile.mkstemp()
            try:
                print 'Profiling %s for %s...' % (
                    func.__name__, maze_type.__name__)
                profile.runctx('func(maze)',
                    globals(), locals(), filename)
                Stats(filename).strip_dirs().sort_stats('time').print_stats(10)
            finally:
                os.close(fd)
                os.unlink(filename)

    runner.__name__ = func.__name__

    PROFILERS.append(runner)

    return func


@profiler
def maze_randomized_prim(maze):
    initialize(maze, rand)


@profiler
def Maze_walk_path(maze):
    list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))
Maze_walk_path.initializer = lambda maze: initialize(maze, rand)


def Maze_walk_path_open_initialize(maze):
    initialize(maze, rand)
    for x in xrange(3, maze.width - 3):
        for y in xrange(3, maze.height - 3):
            for w in maze.walls((x, y)):
                maze[(x, y):w.back.room_pos] = True

@profiler
def Maze_walk_path_open(maze):
    list(maze.walk_path((0, 0), (maze.width - 1, maze.height - 1)))
Maze_walk_path_open.initializer = Maze_walk_path_open_initialize
Maze_walk_path_open.maze_size = (13, 13)


if __name__ == '__main__':
    for profiler in PROFILERS:
        profiler()
