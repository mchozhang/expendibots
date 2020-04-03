#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from queue import Queue, PriorityQueue
from search.board import Board, BoardUtil
from search.util import print_board, print_boom, print_move


def main():
    with open(sys.argv[1]) as file, open("board-data.json") as boardFile:
        BoardUtil.initialize(json.load(boardFile))

        data = json.load(file)
        board = Board(data)

        print_board(board.board, compact=False)
        solutionBoard = wastar(board)
        printSolution(solutionBoard)


def weightedAStarSearch(board):
    queue = PriorityQueue()
    explored = set()

    queue.put((blackNumberHeuristic(board), board))
    explored.add(board)

    while not queue.empty():
        current = queue.get()[1]
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)
            if newNode not in explored:
                newNode.parent = current

                explored.add(newNode)
                priority = 10 * blackNumberHeuristic(newNode) + newNode.cost
                queue.put((priority, newNode))
    return None


def blackNumberHeuristic(board):
    """
    number of the black cells remained
    """
    return len(board.getBlackCells())


def depthFirstSearch(board):
    stack = [board]
    explored = set()

    while stack:
        current = stack.pop()
        if len(current.getBlackCells()) == 0:
            return current

        explored.add(current)
        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)

            if newNode not in explored:
                newNode.parent = current
                stack.append(newNode)
    return None


def breathFirstSearch(board):
    queue = Queue()
    explored = set()

    explored.add(board)
    queue.put(board)

    while queue:
        current = queue.get()
        if len(current.getBlackCells()) == 0:
            return current

        for action in current.getValidActions():
            newNode = current.copy()
            newNode.takeAction(action)

            if newNode not in explored:
                newNode.parent = current
                explored.add(newNode)
                queue.put(newNode)
    return None


def printSolution(board):
    """
    traverse the predecessors of the final board to print the path
    """
    if board is None:
        print("# no solution.")
        return

    # find all the predecessors
    path = []
    current = board
    while current.parent is not None:
        path.insert(0, current.lastAction)
        current = current.parent

    # print the path
    for action in path:
        if action[0] == 0:
            print_boom(action[1], action[2])
        else:
            print_move(action[0], action[1], action[2], action[3], action[4])


# abbreviation of search function
dfs = depthFirstSearch
bfs = breathFirstSearch
wastar = weightedAStarSearch

if __name__ == '__main__':
    main()
