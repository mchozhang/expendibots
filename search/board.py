#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Board:
    """
    board
    """
    EMPTY = 0
    WHITE = 1
    BLACK = 2

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

        # dict of black and white, e.g. {1, 2}: 2
        self.whiteCells = dict()
        self.blackCells = dict()

        # initialize board dict and
        for i in range(8):
            for j in range(8):
                self.board[(i, j)] = (0, Board.EMPTY)

        for token in data["white"]:
            n, x, y = token[0], token[1], token[2]
            self.whiteCells[(x, y)] = n
            self.board[(x, y)] = (n, Board.WHITE)

        for token in data["black"]:
            n, x, y = token[0], token[1], token[2]
            self.blackCells[(x, y)] = n
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
        cells = self.whiteCells if self.turn == Board.WHITE else self.blackCells
        preBoard = self.board[(x, y)]
        postBoard = self.board[(nextX, nextY)]
        des = cells.get((nextX, nextY), 0)

        # update board and cells
        self.board[(nextX, nextY)] = (postBoard[0] + n, preBoard[1])
        cells[(nextX, nextY)] = des + n
        if preBoard[0] == n:
            self.board[(x, y)] = (0, Board.EMPTY)
            cells.pop((x, y))
        else:
            self.board[(x, y)] = (preBoard[0] - n, preBoard[1])
            cells[(x, y)] -= n

    def boom(self, x, y):
        """
        pre-condition: (x, y) has token
        a token or stack boom at (x, y)
        """
        for pos in self.getBoomable(x, y):
            self.board[pos] = (0, Board.EMPTY)
            self.blackCells.pop(pos, None)
            self.whiteCells.pop(pos, None)

    def getBoomable(self, x1, y1):
        """
        get all spots that would be boomed if (x, y) booms
        """
        spots = set()
        board = self.board
        dirs = [(1, -1), (1, 0), (1, 1), (0, 1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

        def recursiveSearch(x, y):
            """
            find all the spots that will boom in recursion
            """
            spots.add((x, y))
            for dir in dirs:
                nextX, nextY = x + dir[0], y + dir[1]
                if (nextX, nextY) in board \
                        and board[(nextX, nextY)][0] != 0 \
                        and (nextX, nextY) not in spots:
                    recursiveSearch(nextX, nextY)

        recursiveSearch(x1, y1)
        return list(spots)

    def getValidActions(self):
        """
        find all valid actions in a single turn,
        include all valid moves and boom
        """
        cells = self.whiteCells if self.turn == Board.WHITE else self.blackCells
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        actions = []

        # find all moves
        for (x, y), n in cells.items():
            # move 1 - n tokens
            for i in range(1, n + 1):
                for dir in dirs:
                    for step in range(1, n + 1):
                        nextX, nextY = x + dir[0] * step, y + dir[1] * step
                        if -1 < nextX < 8 and -1 < nextY < 8 and (
                                self.board[(nextX, nextY)][1] == Board.EMPTY or
                                self.board[(x, y)][1] == self.board[(nextX, nextY)][1]):
                            actions.append((i, x, y, nextX, nextY))

        # find all booms
        for (x, y), n in cells.items():
            actions.append((0, x, y, -1, -1))

        return actions

    def getBoardDict(self):
        data = dict()
        for (x, y), n in self.blackCells.items():
            data[(x, y)] = "⚫️" + str(n)

        for (x, y), n in self.whiteCells.items():
            data[(x, y)] = "⚪️" + str(n)

        return data

    def __repr__(self):
        return str(self.getBoardDict())

    def __eq__(self, other):
        return isinstance(other, Board) and self.getBoardDict() == other.getBoardDict()
