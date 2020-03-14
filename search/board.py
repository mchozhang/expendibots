#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Board:
    """
    board
    """
    WHITE = 0
    BLACK = 1

    def __init__(self, data):
        """
        Args:
            data: board json object
        """
        self.path = []

        # 0: white's turn, 1: black's turn
        self.turn = Board.WHITE

        # dict of all cells, e.g. (1, 2): (1, black)
        self.board = dict()

        for token in data["white"]:
            n, x, y = token[0], token[1], token[2]
            self.board[(x, y)] = (n, Board.WHITE)

        for token in data["black"]:
            n, x, y = token[0], token[1], token[2]
            self.board[(x, y)] = (n, Board.BLACK)

    def takeAction(self, action):
        """
        pre-condition: action is valid
        move or boom a token(stack)
        Args:
            action: tuple (n, x, y, nextX, nextY)
        """
        # extend path
        self.path.append(action)

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
        desCell = self.board.get((nextX, nextY), (0, 0))

        # update board
        self.board[(nextX, nextY)] = (desCell[0] + n, startCell[1])
        if startCell[0] == n:
            self.board.pop((x, y))
        else:
            self.board[(x, y)] = (startCell[0] - n, startCell[1])

    def boom(self, x, y):
        """
        pre-condition: (x, y) has token
        a token or stack boom at (x, y)
        """
        for pos in self.getBoomableCells(x, y):
            self.board.pop(pos)

    def getBoomableCells(self, x1, y1):
        """
        get all spots that would be boomed if (x, y) booms
        """
        cells = set()
        board = self.board
        dirs = [(1, -1), (1, 0), (1, 1), (0, 1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        def recursiveSearch(x, y):
            """
            find all the cells that will boom in recursion
            """
            cells.add((x, y))
            for dir in dirs:
                nextX, nextY = x + dir[0], y + dir[1]
                if Board.validPos(nextX, nextY) and (nextX, nextY) in board and (nextX, nextY) not in cells:
                    recursiveSearch(nextX, nextY)

        recursiveSearch(x1, y1)
        return list(cells)

    def getValidActions(self):
        """
        find all valid actions in a single turn,
        include all valid moves and boom
        """
        cells = self.getWhiteCells() if self.turn == Board.WHITE else self.getBlackCells()
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        actions = []

        # find all moves
        for (x, y), (n, color) in cells:
            # move 1 - n tokens
            for i in range(1, n + 1):
                for dir in dirs:
                    for step in range(1, n + 1):
                        nextX, nextY = x + dir[0] * step, y + dir[1] * step
                        if Board.validPos(nextX, nextY) and \
                                ((nextX, nextY) not in self.board or
                                 self.board[(x, y)][1] == self.board[(nextX, nextY)][1]):
                            actions.append((i, x, y, nextX, nextY))

            # boom at this position
            actions.append((0, x, y, -1, -1))

        return actions

    def getWhiteCells(self):
        return list(filter(lambda v: v[1][1] == Board.WHITE, self.board.items()))

    def getBlackCells(self):
        return list(filter(lambda v: v[1][1] == Board.BLACK, self.board.items()))

    def getBoardDict(self):
        """
        get printable dict data
        """
        data = dict()
        for (x, y), (n, color) in self.board.items():
            data[(x, y)] = "⚫️" + str(n) if color == Board.BLACK else "⚪️" + str(n)
        return data

    def __hash__(self):
        return hash(str(self.board))

    def __repr__(self):
        return str(self.board)

    def __lt__(self, other):
        return len(self.path) < len(other.path)

    def __eq__(self, other):
        return isinstance(other, Board) and self.board == other.board

    @staticmethod
    def validPos(x, y):
        """
        (x, y) is in range (1, 8)
        """
        return -1 < x < 8 and -1 < y < 8

    @staticmethod
    def manhattanDistance(x, y, x1, y1):
        return abs(x - x1) + abs(y - y1)
