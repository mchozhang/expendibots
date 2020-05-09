#!/usr/bin/env python
# -*- coding: utf-8 -*-

from midnight.q_learning_table import ApproximateQLearning
from midnight.board import Board
from midnight.board_util import BoardUtil
import os
import json


class TrainingPlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (White or Black). The value will be one of the 
        strings "white" or "black" correspondingly.
        """
        self.colour = colour
        self.last_action = None
        self.last_board = None

        dir_path = os.path.dirname(os.path.realpath(__file__))
        value_file_name = "white-weights.json" if colour == "white" else "black-weights.json"
        value_file_path = os.path.join(dir_path, value_file_name)
        initial_board_data = os.path.join(dir_path, "initial-board.json")
        board_util_data = os.path.join(dir_path, "board-util-data.json")

        with open(initial_board_data) as board_file, open(board_util_data) as util_file:
            BoardUtil.initialize(json.load(util_file))

            board_data = json.load(board_file)
            self.q_table = ApproximateQLearning(value_file_path, epsilon=0.9)
            self.board = Board(board_data, colour)

    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        self.last_action = self.q_table.choose_action(self.board)
        self.last_board = self.board.copy()
        return self.last_action

    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s
        turns) to inform your player about the most recent action. You should
        use this opportunity to maintain your internal representation of the
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        next_board = self.board.copy()
        next_board.take_action(action)

        isMe = colour == self.colour
        terminal = len(next_board.get_white_cells()) == 0 or len(next_board.get_black_cells()) == 0

        if terminal and isMe:
            reward = BoardUtil.evaluate_round(self.board, next_board, None, action, None, self.colour)
            self.q_table.learn(self.board, next_board, action, reward)
        elif not isMe and self.last_board:
            reward = BoardUtil.evaluate_round(self.last_board, self.board, next_board, self.last_action, action, self.colour)
            self.q_table.learn(self.last_board, next_board, self.last_action, reward)

        if terminal:
            self.q_table.write_value_file()

        self.board = next_board


class GamePlayer:
    def __init__(self, colour):
        self.colour = colour
        self.last_action = None
        self.last_board = None

        dir_path = os.path.dirname(os.path.realpath(__file__))
        value_file_name = "white-weights.json" if colour == "white" else "black-weights.json"
        value_file_path = os.path.join(dir_path, value_file_name)
        initial_board_data = os.path.join(dir_path, "initial-board.json")
        board_util_data = os.path.join(dir_path, "board-util-data.json")

        with open(initial_board_data) as board_file, open(board_util_data) as util_file:
            BoardUtil.initialize(json.load(util_file))

            board_data = json.load(board_file)
            self.q_table = ApproximateQLearning(value_file_path, epsilon=1)
            self.board = Board(board_data, colour)

    def action(self):
        return self.q_table.choose_action(self.board)

    def update(self, colour, action):
        self.board.take_action(action)