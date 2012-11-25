#!/usr/bin/env python
# coding=utf-8

NAME = 'Maze'
DESCRIPTION = 'A library to generate and display mazes'
VERSION = '1.0'
PACKAGES = [
    'maze']
SCRIPTS = [
    'tools/amaze']
REQUIRES = [
    'cairo']

from distutils.core import setup

setup(
    name = NAME,
    description = DESCRIPTION,
    version = VERSION,
    author = 'Moses Palmér',
    author_email = 'mosespalmer@gmail.com',
    url = 'https://github.com/moses-palmer/maze.py/',

    package_dir = {'': 'lib'},
    packages = PACKAGES,
    scripts = SCRIPTS,
    requires = REQUIRES)
