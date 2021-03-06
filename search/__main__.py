#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from search.board import Board
from search.board_util import BoardUtil
from search.util import print_board
from search.blind_search import bfs, dfs
from search.heuristic_search import wastar
from search.q_learning_table import QLearningTable
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


def main():
    board_data_file = os.path.join(dir_path, "board-util-data.json")
    with open(sys.argv[1]) as file, open(board_data_file) as board_file:
        BoardUtil.initialize(json.load(board_file))

        data = json.load(file)
        board = Board(data)

        print_board(board.board, compact=False)

        # comment and uncomment to switch methods
        # BoardUtil.print_solution(wastar(board))
        # BoardUtil.print_solution(bfs(board))
        # BoardUtil.print_solution(dfs(board))
        q_learning(board)


def q_learning(board):
    ql = QLearningTable(os.path.join(dir_path, "level-1.csv"))

    while True:
        action = ql.choose_action(board)
        new_board = board.copy()
        new_board.take_action(action)

        terminal = True
        if len(new_board.get_black_cells()) == 0:
            reward = 1
        elif len(new_board.get_white_cells()) == 0:
            reward = -1
        else:
            terminal = False
            reward = 0
        ql.learn(board, new_board, action, reward)

        BoardUtil.print_action(action)
        board = new_board
        if terminal:
            break

    ql.write_csv()


if __name__ == '__main__':
    main()
