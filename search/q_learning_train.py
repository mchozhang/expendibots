#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from search.board import Board
from search.board_util import BoardUtil
from search.util import print_board
from search.q_learning_search import QLearningBoard
import os


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    board_data_file = os.path.join(dir_path, "board-data.json")

    with open(sys.argv[1]) as file, open(board_data_file) as board_file:
        BoardUtil.initialize(json.load(board_file))

        data = json.load(file)
        board = Board(data)
        print_board(board.board, compact=False)

        ql = QLearningBoard(os.path.join(dir_path, "level-1.csv"))
        for i in range(1000):
            board = Board(data)
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
                    reward = 0
                    terminal = False
                ql.learn(board, new_board, action, reward, terminal)

                BoardUtil.print_action(action)
                board = new_board
                if terminal:
                    break

        ql.write_csv(os.path.join(dir_path, "level-1.csv"))


if __name__ == '__main__':
    main()
