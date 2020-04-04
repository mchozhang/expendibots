#!/usr/bin/env python
# -*- coding: utf-8 -*-

from search.util import print_board, print_boom, print_move


class BoardUtil:
    """
    static utility methods or objects for Board
    """

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

    @staticmethod
    def printSolution(board):
        """
        traverse the predecessors of the final board to print the path
        """
        if board is None:
            print("# no solution.")
            return

        # find all the predecessors
        path = []
        current = board
        while current.parent is not None:
            path.insert(0, current.lastAction)
            current = current.parent

        # print the path
        for action in path:
            if action[0] == 0:
                print_boom(action[1], action[2])
            else:
                print_move(action[0], action[1], action[2], action[3], action[4])