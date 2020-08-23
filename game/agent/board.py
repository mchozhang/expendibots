#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
define data structure of Board and Cell and static utility methods
"""

from copy import deepcopy
from agent.board_util import BoardUtil


class Cell:
    def __init__(self, x, y, n, colour):
        self.x = x
        self.y = y
        self.n = n
        self.colour = colour
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
    WHITE = "white"
    BLACK = "black"

    def __init__(self, data=None, colour="white"):
        """
        Args:
            data: board json object
        """
        self.init_self_data(colour)

        # the steps have been taken
        self.cost = 0

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

    def init_self_data(self, colour):
        if colour == "white":
            self.colour = Board.WHITE
            self.opponent_colour = Board.BLACK
            self.bottom_row = 0
            self.second_bottom_row = 1
            self.half_range = (0, 3)
        else:
            self.colour = Board.BLACK
            self.opponent_colour = Board.WHITE
            self.bottom_row = 7
            self.second_bottom_row = 6
            self.half_range = (4, 7)

    def take_action(self, action):
        """
        pre-condition: action is valid
        move or boom a token(stack)
        Args:
            action: tuple (n, x, y, nextX, nextY)
        """
        self.cost += 1
        if action[0] == "BOOM":
            x, y = action[1]
            self.boom(x, y)
        else:
            x, y = action[2]
            next_x, next_y = action[3]
            self.move(action[1], x, y, next_x, next_y)

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

            for (next_x, next_y) in BoardUtil.surround[(x1, y1)]:
                if (next_x, next_y) in self.board and (next_x, next_y) not in visited:
                    recursive_search(next_x, next_y)

        recursive_search(x, y)
        return cells

    def get_valid_actions(self):
        """
        find all valid actions in a single turn,
        include all valid moves and boom
        """
        cells = self.get_own_cells()
        actions = []

        # find all moves
        for cell in cells:
            x, y = cell.pos
            n, color = cell.n, cell.colour

            # boom at this position
            actions.append(("BOOM", (x, y)))

            # find all valid moves
            for (next_x, next_y) in BoardUtil.cardinal[(x, y)][n]:
                if (next_x, next_y) not in self.board or color == self.board[(next_x, next_y)].colour:
                    actions += [("MOVE", i, (x, y), (next_x, next_y)) for i in range(1, n + 1)]

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

    def white_token_cell_num(self):
        """
        get a tuple of the number of white tokens and white cells
        Returns:
            tuple (token_num, cell_num)
        """
        white_cells = self.get_white_cells()
        return sum([cell.n for cell in white_cells]), len(white_cells)

    def black_token_cell_num(self):
        """
        get a tuple of the number of black tokens and black cells
        Returns:
            tuple (token_num, cell_num)
        """
        black_cells = self.get_black_cells()
        return sum([cell.n for cell in black_cells]), len(black_cells)

    def get_own_cells(self):
        """
        get own cells
        Returns:
            list of own cell
        """
        return self.get_white_cells() if self.colour == Board.WHITE else self.get_black_cells()

    def get_opponent_cells(self):
        """
        get opponents cells
        Returns:
            list of opponent cell
        """
        return self.get_white_cells() if self.colour == Board.BLACK else self.get_black_cells()

    def own_token_cell_num(self):
        """
        get number of own tokens and cells
        Returns:
            tuple (token_num, cell_num)
        """
        return self.white_token_cell_num() if self.colour == Board.WHITE else self.black_token_cell_num()

    def opponent_token_cell_num(self):
        """
        get number of opponent tokens and cells
        Returns:
            tuple (token_num, cell_num)
        """
        return self.white_token_cell_num() if self.colour == Board.BLACK else self.black_token_cell_num()

    def copy(self):
        return deepcopy(self)

    def __deepcopy__(self, mem=None):
        """
        deep copy of the board object
        """
        board = type(self)()
        board.board = deepcopy(self.board)
        board.colour = self.colour
        board.opponent_colour = self.opponent_colour
        board.cost = self.cost
        board.bottom_row = self.bottom_row
        board.second_bottom_row = self.second_bottom_row
        board.half_range = self.half_range
        return board

    def __hash__(self):
        return hash(str(self.board))

    def __repr__(self):
        return str(sorted(self.board.items(), key=lambda t: t[1]))

    def __lt__(self, other):
        return False

    def __eq__(self, other):
        return isinstance(other, Board) and self.board == other.board
