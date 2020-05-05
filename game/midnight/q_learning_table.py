#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import random
import json
from midnight.board_util import BoardUtil, marginal_token_num, get_partitions, partition_kill_rate, cornered_token_num


class ApproximateQLearning:
    def __init__(self, values_file):
        # learning rate
        self.alpha = 0.01
        # reward decay
        self.gamma = 0.9
        # e-greedy
        self.epsilon = 0.9

        self.value_file = values_file
        with open(values_file, 'r') as file:
            self.weights = {k: float(v) for k, v in json.load(file).items()}

    def choose_action(self, board):
        """
        choose an action by the Q table
        Args:
            board: Board object
        Returns:
            a valid action
        """
        valid_actions = board.get_valid_actions()

        if np.random.uniform() < self.epsilon:
            # pick the action with the maximum value
            # l = [(self.get_q_value_for_action(board, action), action) for action in valid_actions]
            # print(l)
            action = max([(self.get_q_value_for_action(board, action), action) for action in valid_actions])[1]
        else:
            action = valid_actions[random.randint(0, len(valid_actions) - 1)]
            print("random action:", action)
        return action

    def learn(self, board, next_board, action, reward):
        """
        update Q table values after taking an action
        Args:
            board: current Board object
            next_board: Board object of the next step
            action: action tuple
            reward: reward value
        """
        q_predict = self.get_q_value_for_action(board, action)
        q_target = reward + self.gamma * self.get_max_q_value(next_board)

        # update weights
        for name, value in self.get_features(board, action).items():
            self.weights[name] += self.alpha * (q_target - q_predict) * value

    def get_features(self, board, action):
        features = dict()
        next_board = board.copy()
        next_board.take_action(action)
        own_token_num, own_cell_num = next_board.own_token_cell_num()
        opponent_token_num, own_cell_num = next_board.opponent_token_cell_num()

        features["token-diff"] = own_token_num - opponent_token_num
        features["marginal-num"] = marginal_token_num(board)
        features["cornered-num"] = cornered_token_num(board)

        # partition kill rate
        own_partitions = get_partitions(next_board, True)
        opponent_partitions = get_partitions(next_board, False)
        own_partition_kill_rate = partition_kill_rate(own_partitions, next_board.colour)
        opponent_partition_kill_rate = partition_kill_rate(opponent_partitions, next_board.opponent_colour)
        features["own-token-num-per-partition"] = own_token_num // len(own_partitions) if own_token_num != 0 else 12
        features["own-partition-kill-rate"] = own_partition_kill_rate if own_partition_kill_rate > 1 else 0
        features["opponent-partition-kill-rate"] = opponent_partition_kill_rate if opponent_partition_kill_rate > 1 else 0

        for name, value in features.items():
            features[name] /= 10

        return features

    def get_q_value_for_action(self, board, action):
        q_value = 0
        for name, value in self.get_features(board, action).items():
            q_value += self.weights[name] * value
        return q_value

    def get_max_q_value(self, board):
        values = [self.get_q_value_for_action(board, action) for action in board.get_valid_actions()]
        return max(values) if values else 0

    def write_value_file(self):
        """
        write Q table to the file
        """
        with open(self.value_file, 'w') as file:
            data = json.dumps(self.weights)
            file.write(data)
