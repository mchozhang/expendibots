#!/usr/bin/env python
# -*- coding: utf-8 -*-
# an agent using user input for every move to play against another agent,
# this agent is used to test the 'agent' module

from agent.board import BoardUtil, Board
from agent.player import TrainingPlayer
import os
import json


class Player:
    """
    an agent requiring user to input every move
    """
    def __init__(self, colour):
        self.colour = colour
        self.last_action = None
        self.last_board = None
        self.cost = 0
        self.player = TrainingPlayer(self.colour)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        initial_board_data = os.path.join(dir_path, "initial-board.json")
        board_util_data = os.path.join(dir_path, "board-util-data.json")

        with open(initial_board_data) as board_file, open(board_util_data) as util_file:
            BoardUtil.initialize(json.load(util_file))

            board_data = json.load(board_file)
            self.board = Board(board_data, colour)

    def action(self):
        """
        input 2 values to perform a BOOM, 5 values to perform a MOVE
        Returns:
            a tuple representing an action
        """
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
