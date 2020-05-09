#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import random
import json
from midnight.board_util import BoardUtil


class ApproximateQLearning:
    def __init__(self, values_file, epsilon=1):
        # learning rate
        self.alpha = 0.01
        # reward decay
        self.gamma = 0.9
        # e-greedy
        self.epsilon = epsilon

        self.value_file = values_file
        with open(values_file, 'r') as file:
            self.weights = {k: float(v) for k, v in json.load(file).items()}

    def choose_action(self, board):
        """
        choose an action by the Q table
        Args:
            board: Board object with valid actions
        Returns:
            a valid action
        """
        valid_actions = board.get_valid_actions()

        if np.random.uniform() < self.epsilon:
            # pick the action with the maximum value
            # find all the actions with the same max q value
            max_indices = [0]
            max_value = self.get_q_value_for_action(board, valid_actions[0])
            for i, action in enumerate(valid_actions[1:]):
                value = self.get_q_value_for_action(board, action)
                if value > max_value:
                    max_indices = [i + 1]
                    max_value = value
                elif value == max_value:
                    max_indices.append(i + 1)

            # randomly pick an action with max q value
            action = valid_actions[max_indices[random.randint(0, len(max_indices) - 1)]]
        else:
            # random action for learning
            action = valid_actions[random.randint(0, len(valid_actions) - 1)]
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
        diff = self.alpha * (q_target - q_predict)

        # update weights
        for name, value in self.get_features(board, action).items():
            self.weights[name] += diff * value

    def get_features(self, board, action):
        features = dict()
        next_board = board.copy()
        next_board.take_action(action)
        own_token_num, own_cell_num = next_board.own_token_cell_num()
        opponent_token_num, opponent_cell_num = next_board.opponent_token_cell_num()
        own_marginal_token_num = BoardUtil.own_marginal_token_num(next_board)
        own_cornered_token_num = BoardUtil.own_cornered_token_num(next_board)

        features["token-diff"] = own_token_num - opponent_token_num
        features["marginal-rate"] = own_marginal_token_num / own_token_num if own_token_num else 1
        features["cornered-rate"] = own_cornered_token_num / own_token_num if own_token_num else 1
        features["average-stack-score"] = BoardUtil.average_stack_score(next_board)
        features["early-non-bottom-num"] = BoardUtil.early_non_bottom_num(next_board)

        # partition kill rate
        own_partitions = BoardUtil.get_partitions(next_board, True)
        opponent_partitions = BoardUtil.get_partitions(next_board, False)
        own_partition_token_diff = BoardUtil.max_partition_token_diff(own_partitions, next_board.colour)
        opponent_partition_token_diff = BoardUtil.max_partition_token_diff(opponent_partitions, next_board.opponent_colour)
        features["max-own-partition-token-diff"] = own_partition_token_diff if own_partition_token_diff > 1 else 0
        features["max-opponent-partition-token-diff"] = opponent_partition_token_diff if opponent_partition_token_diff > 1 else 0

        # vulnerable spots
        own_vulnerable_spots = BoardUtil.vulnerable_spots(next_board, own_partitions, True)
        opponent_vulnerable_spots = BoardUtil.vulnerable_spots(next_board, opponent_partitions, False)
        own_vulnerability_reachability = BoardUtil.partition_vulnerability(own_vulnerable_spots)
        opponent_vulnerability_reachability = BoardUtil.partition_vulnerability(opponent_vulnerable_spots)
        features["own-vulnerability-reachability"] = own_vulnerability_reachability
        features["opponent-vulnerability-reachability"] = opponent_vulnerability_reachability
        features["opponent-leftover-chasing"] = BoardUtil.opponent_leftover_chasing(next_board, opponent_vulnerable_spots)

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
