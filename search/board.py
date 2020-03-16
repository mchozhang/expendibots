#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from copy import copy, deepcopy


class Cell:
    def __init__(self, x, y, n, color):
        self.x = x
        self.y = y
        self.n = n
        self.color = color
        self.pos = (x, y)

    def __repr__(self):
        s = str(self.n) + " " + str(self.pos)
        return "⚫️" + s if self.color == Board.BLACK else "⚪️" + s

    def __eq__(self, other):
        return self.pos == other.pos and self.n == other.n and self.color == other.color

    def __hash__(self):
        return hash((self.pos, self.n, self.color))

    def __deepcopy__(self, memodict={}):
        return type(self)(self.x, self.y, self.n, self.color)


class Board:
    """
    board
    """
    WHITE = 0
    BLACK = 1

    def __init__(self, data=None):
        """
        Args:
            data: board json object
        """
        self.parent = None
        self.lastAction = None
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

    def takeAction(self, action):
        """
        pre-condition: action is valid
        move or boom a token(stack)
        Args:
            action: tuple (n, x, y, nextX, nextY)
        """
        # record last action
        self.lastAction = action
        self.cost += 1

        if action[0] == 0:
            self.boom(action[1], action[2])
        else:
            self.move(action[0], action[1], action[2], action[3], action[4])

    def move(self, n, x, y, nextX, nextY):
        """
        pre-condition: the move is valid
        a token at (x,y) moves to (nextX, nextY)
        """
        startCell = self.board[(x, y)]
        desCell = self.board.get((nextX, nextY), Cell(nextX, nextY, 0, startCell.color))

        # update destination cell
        desCell.n += n
        self.board[(nextX, nextY)] = desCell

        # update start cell
        if startCell.n == n:
            self.board.pop((x, y))
        else:
            startCell.n -= n

    def boom(self, x, y):
        """
        pre-condition: (x, y) has token
        a token or stack boom at (x, y)
        """
        for cell in self.getBoomableCells(x, y):
            self.board.pop(cell.pos)

    def getBoomableCells(self, x, y):
        """
        pre-condition: (x, y) has token
        get all spots that would be boomed if (x, y) booms
        """
        cells = []
        visited = set()
        board = self.board

        def recursiveSearch(x1, y1):
            """
            find all the cells that will boom in recursion
            """
            cells.append(self.board[(x1, y1)])
            visited.add((x1, y1))

            for (nextX, nextY) in BoardUtil.surround[(x1, y1)]:
                if (nextX, nextY) in board and (nextX, nextY) not in visited:
                    recursiveSearch(nextX, nextY)

        recursiveSearch(x, y)
        return cells

    def getValidActions(self):
        """
        find all valid actions in a single turn,
        include all valid moves and boom
        """
        cells = self.getWhiteCells() if self.turn == Board.WHITE else self.getBlackCells()
        actions = []

        # find all moves
        for cell in cells:
            x, y = cell.pos
            n, color = cell.n, cell.color

            # boom at this position
            actions.append((0, x, y, -1, -1))

            # find all valid moves
            for (nextX, nextY) in BoardUtil.cardinal[(x, y)][n]:
                if (nextX, nextY) not in self.board or color == self.board[(nextX, nextY)].color:
                    actions += [(i, x, y, nextX, nextY) for i in range(1, n + 1)]

        return actions

    def getBlackPiles(self):
        """
        find all collections of cells that will boom if one of the tokens booms
        Returns:
            list of list of cells in the same pile
        """
        cells = set(self.getBlackCells())
        res = []

        while cells:
            randomCell = cells.pop()
            boomableCells = self.getBoomableCells(randomCell.x, randomCell.y)
            pile = [randomCell]
            for cell in boomableCells[1:]:
                if cell.color == Board.BLACK:
                    pile.append(cell)
                    cells.remove(cell)
            res.append(pile)

        return res

    def getWhiteCells(self):
        return list(filter(lambda cell: cell.color == Board.WHITE, self.board.values()))

    def getBlackCells(self):
        return list(filter(lambda cell: cell.color == Board.BLACK, self.board.values()))

    def copy(self):
        return deepcopy(self)

    def __deepcopy__(self, memodict={}):
        """
        deep copy of the board
        """
        board = type(self)()
        board.board = deepcopy(self.board)
        board.lastAction = self.lastAction
        board.turn = self.turn
        board.cost = self.cost
        return board

    def __hash__(self):
        return hash(str(self.board))

    def __repr__(self):
        return str(self.board)

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return isinstance(other, Board) and self.board == other.board


class BoardUtil:
    cardinal = dict()
    surround = dict()

    @staticmethod
    def initialize(data):
        """
        parse board-data.json which contains the adjacent cell data of every cell
        Args:
            data: json data from board-data.json
        """
        for pos, steps in data["cardinal"].items():
            BoardUtil.cardinal[eval(pos)] = dict()
            for step, cells in steps.items():
                BoardUtil.cardinal[eval(pos)][int(step)] = [eval(cell) for cell in cells]

        for pos, cells in data["surround"].items():
            BoardUtil.surround[eval(pos)] = [eval(cell) for cell in cells]

    @staticmethod
    def validPos(x, y):
        """
        (x, y) is in range (1, 8)
        """
        return -1 < x < 8 and -1 < y < 8

    @staticmethod
    def manhattanDistance(x, y, x1, y1):
        return abs(x - x1) + abs(y - y1)
