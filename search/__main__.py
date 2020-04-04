#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from search.board import Board
from search.board_util import BoardUtil
from search.util import print_board
from search.heuristic_search import wastar
import os


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    boardDataFile = os.path.join(dir_path, "board-data.json")

    with open(sys.argv[1]) as file, open(boardDataFile) as boardFile:
        BoardUtil.initialize(json.load(boardFile))

        data = json.load(file)
        board = Board(data)

        print_board(board.board, compact=False)
        BoardUtil.printSolution(wastar(board))


if __name__ == '__main__':
    main()
