#!/usr/bin/env python
# -*- coding: utf-8 -*-

from midnight.util import print_board, print_boom, print_move


class BoardUtil:
    """
    static utility methods or objects for Board
    """

    cardinal = dict()
    surround = dict()

    @staticmethod
    def initialize(data):
        """
        parse board-util-data.json which contains the adjacent cell data of every cell
        Args:
            data: json data from board-util-data.json
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
    def manhattan_distance(x, y, x1, y1):
        return abs(x - x1) + abs(y - y1)

    @staticmethod
    def print_action(action):
        """
        print an action
        Args:
            action: action tuple
        """
        if action[0] == "BOOM":
            x, y = action[1]
            print_boom(x, y)
        else:
            x, y = action[2]
            next_x, next_y = action[3]
            print_move(action[1], x, y, next_x, next_y)

    @staticmethod
    def evaluate(board, next_board, colour):
        white_number_change = board.get_white_number() - next_board.get_white_number()
        black_number_change = board.get_black_number() - next_board.get_black_number()
        if colour == "white":
            reward = black_number_change - white_number_change
        else:
            reward = white_number_change - black_number_change
        return reward
