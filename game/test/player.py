#!/usr/bin/env python
# -*- coding: utf-8 -*-

from midnight.board import BoardUtil, Board
from midnight.player import TrainingPlayer
import os, json, random


class Player:

    def __init__(self, colour):
        self.colour = colour
        self.last_action = None
        self.last_board = None
        self.cost = 0
        self.player = TrainingPlayer(self.colour)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        value_file_name = "white-weights.json" if colour == "white" else "black-weights.json"
        value_file_path = os.path.join(dir_path, value_file_name)
        initial_board_data = os.path.join(dir_path, "initial-board.json")
        board_util_data = os.path.join(dir_path, "board-util-data.json")

        with open(initial_board_data) as board_file, open(board_util_data) as util_file:
            BoardUtil.initialize(json.load(util_file))

            board_data = json.load(board_file)
            self.board = Board(board_data, colour)

    def action(self):
        # steps = [('MOVE', 1, (6,0), (6,1)),
        #          ('MOVE', 2, (6,1), (6,3)),
        #          ('MOVE', 1, (6,3), (6, 5)),
        #          ('MOVE', 1, (6,5), (6,6)),
        #          ('BOOM', (6, 6))]
        #
        # if self.cost < len(steps):
        #     return steps[self.cost]
        # else:
        #     action = self.player.action()
        #     return action
        print('bot: ', self.player.action())
        values = input('input action:').split(' ')
        values = [int(i) for i in values]
        if len(values) == 2:
            return 'BOOM', (values[0], values[1])
        else:
            return 'MOVE', values[0], (values[1], values[2]), (values[3], values[4])

    def update(self, colour, action):
        if colour == self.colour:
            self.cost += 1

        self.board.take_action(action)
        self.player.update(colour, action)
