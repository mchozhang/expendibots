#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
define data structure of Board and Cell and static utility methods
"""

from copy import deepcopy
from search.board_util import BoardUtil


class Cell:
    def __init__(self, x, y, n, color):
        self.x = x
        self.y = y
        self.n = n
        self.colour = color
        self.pos = (x, y)

    def __repr__(self):
        s = str(self.n) + " " + str(self.pos)
        return "⚫️" + s if self.colour == Board.BLACK else "⚪️" + s

    def __lt__(self, other):
        return self.pos < other.pos

    def __eq__(self, other):
        return self.pos == other.pos and self.n == other.n and self.colour == other.colour

    def __hash__(self):
        return hash((self.pos, self.n, self.colour))

    def __deepcopy__(self, mem=None):
        return type(self)(self.x, self.y, self.n, self.colour)


class Board:
    """
    board object
    """
    WHITE = 0
    BLACK = 1

    def __init__(self, data=None):
        """
        Args:
            data: board json object
        """
        self.parent = None
        self.last_action = None
        self.cost = 0

        # 0: white's turn, 1: black's turn
        self.turn = Board.WHITE

        # dict of all not-empty cells, key: (x, y) value: Cell(), must not contain empty cell
        self.board = dict()

        # initialize board data
        if data is not None:
            for token in data["white"]:
                n, x, y = token[0], token[1], token[2]
                self.board[(x, y)] = Cell(x, y, n, Board.WHITE)

            for token in data["black"]:
                n, x, y = token[0], token[1], token[2]
                self.board[(x, y)] = Cell(x, y, n, Board.BLACK)

    def take_action(self, action):
        """
        pre-condition: action is valid
        move or boom a token(stack)
        Args:
            action: tuple (n, x, y, nextX, nextY)
        """
        # record last action
        self.last_action = action
        self.cost += 1

        if action[0] == 0:
            self.boom(action[1], action[2])
        else:
            self.move(action[0], action[1], action[2], action[3], action[4])

    def move(self, n, x, y, next_x, next_y):
        """
        pre-condition: the move is valid
        a token at (x,y) moves to (next_x, next_y)
        """
        start_cell = self.board[(x, y)]
        des_cell = self.board.get((next_x, next_y), Cell(next_x, next_y, 0, start_cell.colour))

        # update destination cell
        des_cell.n += n
        self.board[(next_x, next_y)] = des_cell

        # update start cell
        if start_cell.n == n:
            self.board.pop((x, y))
        else:
            start_cell.n -= n

    def boom(self, x, y):
        """
        pre-condition: (x, y) has token
        a token or stack boom at (x, y)
        """
        for cell in self.get_connected_cells(x, y):
            self.board.pop(cell.pos)

    def get_connected_cells(self, x, y):
        """
        pre-condition: (x, y) has token
        get all spots that would be boomed if (x, y) booms
        """
        cells = []
        visited = set()

        def recursive_search(x1, y1):
            """
            find all the cells that will boom in recursion
            """
            cells.append(self.board[(x1, y1)])
            visited.add((x1, y1))

            for (nextX, nextY) in BoardUtil.surround[(x1, y1)]:
                if (nextX, nextY) in self.board and (nextX, nextY) not in visited:
                    recursive_search(nextX, nextY)

        recursive_search(x, y)
        return cells

    def get_valid_actions(self):
        """
        find all valid actions in a single turn,
        include all valid moves and boom
        """
        cells = self.get_white_cells() if self.turn == Board.WHITE else self.get_black_cells()
        actions = []

        # find all moves
        for cell in cells:
            x, y = cell.pos
            n, color = cell.n, cell.colour

            # boom at this position
            actions.append((0, x, y, -1, -1))

            # find all valid moves
            for (nextX, nextY) in BoardUtil.cardinal[(x, y)][n]:
                if (nextX, nextY) not in self.board or color == self.board[(nextX, nextY)].colour:
                    actions += [(i, x, y, nextX, nextY) for i in range(1, n + 1)]

        return actions

    def get_white_cells(self):
        """
        get white cell list
        Returns:
            list of white cell
        """
        return list(filter(lambda cell: cell.colour == Board.WHITE, self.board.values()))

    def get_black_cells(self):
        """
        get black cell list
        Returns:
            list of black cell
        """
        return list(filter(lambda cell: cell.colour == Board.BLACK, self.board.values()))

    def copy(self):
        return deepcopy(self)

    def __deepcopy__(self, mem=None):
        """
        deep copy of the board object
        """
        board = type(self)()
        board.board = deepcopy(self.board)
        board.last_action = self.last_action
        board.turn = self.turn
        board.cost = self.cost
        return board

    def __hash__(self):
        return hash(str(self.board))

    def __repr__(self):
        return str(sorted(self.board.items(), key=lambda t: t[1]))

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return isinstance(other, Board) and self.board == other.board
