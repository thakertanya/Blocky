"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    final = []
    index = []
    possible = [PerimeterGoal, BlobGoal]
    x = random.choice(possible)
    while len(index) < num_goals:
        num = random.randint(0, len(COLOUR_LIST)-1)
        if num not in index:
            index.append(num)
    for y in index:
        if x == PerimeterGoal:
            final.append(PerimeterGoal(COLOUR_LIST[y]))
        else:
            final.append(BlobGoal(COLOUR_LIST[y]))
    return final


def _flatten_help(block: Block, loc: Tuple[int, int]) -> Tuple[int, int, int]:
    """ Returns the colour of the block at <loc> location.
    """
    mid = int(math.pow(2, block.max_depth - block.level - 1))
    if not block.children:
        return block.colour
    elif loc[0] >= mid > loc[1]:
        return _flatten_help(block.children[0], (loc[0] - mid, loc[1]))
    elif loc[0] < mid and loc[1] < mid:
        return _flatten_help(block.children[1], (loc[0], loc[1]))
    elif loc[0] < mid <= loc[1]:
        return _flatten_help(block.children[2], (loc[0], loc[1] - mid))
    else:
        return _flatten_help(block.children[3], (loc[0] - mid, loc[1] - mid))


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    size = int(math.pow(2, block.max_depth - block.level))
    final = []
    for i in range(size):
        x = []
        for j in range(size):
            x.append(_flatten_help(block, (i, j)))
        final.append(x)
    return final


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """ A player goal in the game blocky where the goal is to have as many
    blocks of target colour on the perimeter as possible

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    def score(self, board: Block) -> int:
        f = _flatten(board)
        total = 0
        last_pos = len(f) - 1
        if f[0][0] == self.colour:
            total += 2
        if f[0][last_pos] == self.colour:
            total += 2
        if f[last_pos][0] == self.colour:
            total += 2
        if f[last_pos][last_pos] == self.colour:
            total += 2

        for i in range(1, last_pos):
            if f[last_pos][i] == self.colour:
                total += 1
            if f[0][i] == self.colour:
                total += 1
            if f[i][last_pos] == self.colour:
                total += 1
            if f[i][0] == self.colour:
                total += 1

        return total

    def description(self) -> str:

        return "Aim to put the most number of unit cells of " \
               "colour " + colour_name(self.colour) + " on the perimeter."


class BlobGoal(Goal):
    """ A player goal in the game blocky where the goal is to have as many
    connected blocks of target colour  as possible

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    def score(self, board: Block) -> int:
        flattened_board = _flatten(board)
        length = 2 ** board.max_depth
        visit_list = []
        for i in range(length):
            x = []
            for j in range(length):
                x.append(-1)
            visit_list.append(x)

        maximum = 0
        for i in range(len(visit_list)):
            for j in range(len(visit_list)):
                if visit_list[i][j] == -1:
                    score_tots = self._undiscovered_blob_size((i, j),
                                                              flattened_board,
                                                              visit_list)
                    maximum = max(maximum, score_tots)
        return maximum

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x = pos[0]
        y = pos[1]
        total = 1
        if x < 0 or x >= len(board) or y < 0 or y >= len(board):
            return 0
        elif visited[x][y] == 0 or visited[x][y] == 1:
            return 0
        elif board[x][y] != self.colour:
            visited[x][y] = 0
            return 0
        else:
            visited[x][y] = 1
            total += self._undiscovered_blob_size((x, y - 1), board, visited)
            total += self._undiscovered_blob_size((x + 1, y), board, visited)
            total += self._undiscovered_blob_size((x, y + 1), board, visited)
            total += self._undiscovered_blob_size((x - 1, y), board, visited)
            return total

    def description(self) -> str:
        x = "A player must aim to create a blob of connected " \
            "blocks of colour, " + colour_name(self.colour)
        return x


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
