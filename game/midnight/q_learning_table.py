#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import random


class QLearningTable:
    def __init__(self, csv_file):
        # learning rate
        self.alpha = 0.01
        # reward decay
        self.gamma = 0.9
        # e-greedy
        self.epsilon = 0.9

        self.csv_path = csv_file
        try:
            # read Q table from csv file
            self.q_table = pd.read_csv(csv_file, index_col=0)

            # change column type to tuple
            self.q_table.columns = [eval(col) for col in self.q_table.columns]

        except Exception as e:
            self.q_table = pd.DataFrame()

    def choose_action(self, board):
        """
        choose an action by the Q table
        Args:
            board: Board object
        Returns:
            a valid action
        """
        self.fill_table(board)
        valid_actions = board.get_valid_actions()

        if np.random.uniform() < self.epsilon:
            # pick the action with the maximum value
            actions = self.q_table.loc[str(board), valid_actions]
            action = actions.idxmax()
        else:
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
        self.fill_table(next_board)
        q_predict = self.q_table.at[str(board), action]
        next_valid_actions = next_board.get_valid_actions()

        if len(next_valid_actions) == 0:
            # terminal state have empty value
            q_target = reward
        else:
            q_target = reward + self.gamma * self.q_table.loc[str(next_board), next_valid_actions].max()

        # update Q table
        self.q_table.at[str(board), action] += self.alpha * (q_target - q_predict)

    def fill_table(self, board):
        """
        add new state and actions to the q_table, fill empty cell with 0
        Args:
            board: Board object
        """
        board_str = str(board)
        if board_str not in self.q_table.index:
            row_len, col_len = self.q_table.shape

            # append state as new row
            row = pd.DataFrame([[0.0] * col_len], index=[board_str], columns=self.q_table.columns)
            self.q_table = self.q_table.append(row)

            # append new actions as columns
            for action in board.get_valid_actions():
                if action not in self.q_table.columns:
                    self.q_table[action] = 0.0 * row_len

    def write_csv(self):
        """
        write Q table to the csv file
        """
        self.q_table.to_csv(self.csv_path)
